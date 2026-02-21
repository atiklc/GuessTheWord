from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Dict, Iterable, List


@dataclass
class Player:
    name: str
    score: int = 0


@dataclass
class GuessTheWordGame:
    words: List[str]
    players: Dict[str, Player] = field(default_factory=dict)
    revealed_ratio: float = 0.35

    @staticmethod
    def normalize_name(name: str) -> str:
        return name.strip().lower()

    def register_players(self, player_names: Iterable[str]) -> None:
        for name in player_names:
            normalized = self.normalize_name(name)
            if normalized and normalized not in self.players:
                self.players[normalized] = Player(name=name.strip())

    def choose_word(self) -> str:
        if not self.words:
            raise ValueError("Kelime listesi boş olamaz.")
        return random.choice(self.words).lower()

    def generate_hint(self, word: str) -> str:
        if not word:
            raise ValueError("Kelime boş olamaz.")

        reveal_count = max(1, round(len(word) * self.revealed_ratio))
        indexes = set(random.sample(range(len(word)), k=min(reveal_count, len(word))))
        return "".join(letter if i in indexes else "_" for i, letter in enumerate(word))

    def calculate_points(self, rank: int) -> int:
        if rank < 1:
            raise ValueError("Sıra 1 veya daha büyük olmalıdır.")
        return max(0, 400 - (rank - 1) * 100)

    def score_round(self, ordered_winners: List[str]) -> None:
        awarded: set[str] = set()
        rank = 1
        for player_name in ordered_winners:
            normalized = self.normalize_name(player_name)
            if normalized in awarded or normalized not in self.players:
                continue
            self.players[normalized].score += self.calculate_points(rank)
            awarded.add(normalized)
            rank += 1
            if rank > 4:
                break

    def leaderboard(self) -> List[Player]:
        return sorted(self.players.values(), key=lambda p: p.score, reverse=True)


def collect_round_winners(game: GuessTheWordGame, secret_word: str) -> List[str]:
    winners: List[str] = []
    print("Her oyuncu sırayla 1 tahmin yapar.")
    for key, player in game.players.items():
        guess = input(f"{player.name} tahmini: ").strip().lower()
        if guess == secret_word:
            winners.append(key)
            print(f"✅ {player.name} doğru bildi!")
        else:
            print("❌ Yanlış tahmin.")
    return winners


def play_cli() -> None:
    words = ["bilgisayar", "yazilim", "algoritma", "oyuncak", "macera", "kelime", "bulmaca"]
    game = GuessTheWordGame(words=words)

    print("=== Kelime Tahmin Oyununa Hoş Geldiniz ===")
    names = input("Oyuncu isimlerini virgülle girin: ").split(",")
    game.register_players(names)

    if not game.players:
        print("En az bir oyuncu gerekli.")
        return

    round_count_text = input("Toplam tur sayısı: ").strip()
    round_count = int(round_count_text) if round_count_text.isdigit() and int(round_count_text) > 0 else 1

    for round_no in range(1, round_count + 1):
        secret_word = game.choose_word()
        hint = game.generate_hint(secret_word)

        print(f"\n=== {round_no}. Tur / {round_count} ===")
        print("İpucu:", hint)
        print("Kelime uzunluğu:", len(secret_word))

        winners = collect_round_winners(game, secret_word)
        game.score_round(winners)

        print("\nAra Skor Tablosu")
        for rank, player in enumerate(game.leaderboard(), start=1):
            print(f"{rank}. {player.name}: {player.score} puan")

    print("\n=== Oyun Bitti: Final Skor Tablosu ===")
    table = game.leaderboard()
    for rank, player in enumerate(table, start=1):
        print(f"{rank}. {player.name}: {player.score} puan")

    if table:
        print(f"\n🏆 Kazanan: {table[0].name} ({table[0].score} puan)")


if __name__ == "__main__":
    play_cli()
