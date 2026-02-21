from __future__ import annotations

from flask import Flask, jsonify, request, send_from_directory

from multiplayer import PlayerState, Room, WORDS, generate_code, generate_id

app = Flask(__name__)

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
