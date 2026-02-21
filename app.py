from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random
import string
from typing import Dict, List

from flask import Flask, jsonify, request, send_from_directory

from game import GuessTheWordGame

app = Flask(__name__)


@dataclass
class Submission:
    guess: str
    submitted_at: datetime


@dataclass
class PlayerState:
    name: str
    score: int = 0


@dataclass
class Room:
    code: str
    host_id: str
    total_rounds: int
    words: List[str]
    players: Dict[str, PlayerState] = field(default_factory=dict)
    status: str = "waiting"  # waiting, playing, round_result, finished
    current_round: int = 0
    secret_word: str = ""
    hint: str = ""
    submissions: Dict[str, Submission] = field(default_factory=dict)
    round_winners: List[str] = field(default_factory=list)

    def start_round(self) -> None:
        self.current_round += 1
        self.status = "playing"
        self.secret_word = random.choice(self.words).lower()
        helper = GuessTheWordGame(words=self.words)
        self.hint = helper.generate_hint(self.secret_word)
        self.submissions = {}
        self.round_winners = []

    def submit_guess(self, player_id: str, guess: str) -> None:
        if self.status != "playing":
            raise ValueError("Tur aktif değil")
        if player_id not in self.players:
            raise ValueError("Oyuncu odada değil")
        if player_id in self.submissions:
            raise ValueError("Bu tur zaten tahmin gönderildi")
        self.submissions[player_id] = Submission(guess=guess.strip().lower(), submitted_at=datetime.utcnow())

    def all_submitted(self) -> bool:
        return len(self.submissions) == len(self.players)

    def finalize_round(self) -> None:
        ordered_correct = [
            pid
            for pid, sub in sorted(self.submissions.items(), key=lambda item: item[1].submitted_at)
            if sub.guess == self.secret_word
        ]
        self.round_winners = ordered_correct[:4]

        helper = GuessTheWordGame(words=self.words)
        for idx, pid in enumerate(self.round_winners, start=1):
            self.players[pid].score += helper.calculate_points(idx)

        self.status = "round_result"
        if self.current_round >= self.total_rounds:
            self.status = "finished"

    def leaderboard(self) -> List[dict]:
        rows = [{"player_id": pid, "name": p.name, "score": p.score} for pid, p in self.players.items()]
        return sorted(rows, key=lambda r: r["score"], reverse=True)


WORDS = ["bilgisayar", "yazilim", "algoritma", "oyuncak", "macera", "kelime", "bulmaca"]


def generate_code(size: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=size))


def generate_id(size: int = 12) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=size))


ROOMS: dict[str, Room] = {}


def get_room_or_404(code: str) -> Room:
    room = ROOMS.get(code.upper())
    if not room:
        raise ValueError("Oda bulunamadı")
    return room


@app.get("/")
def home():
    return send_from_directory(".", "index.html")


@app.post("/api/create")
def create_room():
    data = request.get_json(force=True)
    host_name = (data.get("host_name") or "").strip()
    total_rounds = int(data.get("total_rounds") or 1)

    if not host_name:
        return jsonify({"error": "Host adı zorunlu"}), 400
    if total_rounds < 1:
        return jsonify({"error": "Tur sayısı en az 1 olmalı"}), 400

    code = generate_code()
    while code in ROOMS:
        code = generate_code()

    host_id = generate_id()
    room = Room(code=code, host_id=host_id, total_rounds=total_rounds, words=WORDS)
    room.players[host_id] = PlayerState(name=host_name)
    ROOMS[code] = room

    return jsonify({"room_code": code, "player_id": host_id, "is_host": True})


@app.post("/api/join")
def join_room():
    data = request.get_json(force=True)
    code = (data.get("room_code") or "").strip().upper()
    name = (data.get("name") or "").strip()

    if not code or not name:
        return jsonify({"error": "Oda kodu ve isim zorunlu"}), 400

    try:
        room = get_room_or_404(code)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404

    if room.status != "waiting":
        return jsonify({"error": "Oyun başladı, yeni oyuncu alınmıyor"}), 400

    pid = generate_id()
    room.players[pid] = PlayerState(name=name)
    return jsonify({"room_code": code, "player_id": pid, "is_host": False})


@app.post("/api/start")
def start_game():
    data = request.get_json(force=True)
    code = (data.get("room_code") or "").strip().upper()
    player_id = data.get("player_id")
    room = get_room_or_404(code)

    if player_id != room.host_id:
        return jsonify({"error": "Sadece host başlatabilir"}), 403
    if room.status != "waiting":
        return jsonify({"error": "Oyun zaten başladı"}), 400

    room.start_round()
    return jsonify({"ok": True})


@app.post("/api/submit")
def submit_guess():
    data = request.get_json(force=True)
    code = (data.get("room_code") or "").strip().upper()
    player_id = data.get("player_id")
    guess = (data.get("guess") or "").strip()
    room = get_room_or_404(code)

    try:
        room.submit_guess(player_id, guess)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if room.all_submitted():
        room.finalize_round()

    return jsonify({"ok": True})


@app.post("/api/next-round")
def next_round():
    data = request.get_json(force=True)
    code = (data.get("room_code") or "").strip().upper()
    player_id = data.get("player_id")
    room = get_room_or_404(code)

    if player_id != room.host_id:
        return jsonify({"error": "Sadece host geçebilir"}), 403
    if room.status != "round_result":
        return jsonify({"error": "Tur sonucu ekranında değil"}), 400

    room.start_round()
    return jsonify({"ok": True})


@app.get("/api/state")
def get_state():
    code = (request.args.get("room_code") or "").strip().upper()
    player_id = request.args.get("player_id")

    try:
        room = get_room_or_404(code)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404

    if player_id not in room.players:
        return jsonify({"error": "Oyuncu bu odada değil"}), 403

    submitted_players = len(room.submissions)
    player_submitted = player_id in room.submissions

    payload = {
        "room_code": room.code,
        "status": room.status,
        "is_host": player_id == room.host_id,
        "total_rounds": room.total_rounds,
        "current_round": room.current_round,
        "hint": room.hint if room.status in {"playing", "round_result", "finished"} else "",
        "word_length": len(room.secret_word) if room.status in {"playing", "round_result", "finished"} else 0,
        "players": [{"id": pid, "name": p.name} for pid, p in room.players.items()],
        "submitted_count": submitted_players,
        "total_players": len(room.players),
        "player_submitted": player_submitted,
        "leaderboard": room.leaderboard(),
        "round_winners": [room.players[pid].name for pid in room.round_winners] if room.status in {"round_result", "finished"} else [],
    }
    return jsonify(payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
