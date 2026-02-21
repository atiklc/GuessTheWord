from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random
import string
from typing import Dict, List

from game import GuessTheWordGame


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
