import unittest

from game import GuessTheWordGame


class GuessTheWordGameTests(unittest.TestCase):
    def setUp(self) -> None:
        self.game = GuessTheWordGame(words=["algoritma"])
        self.game.register_players(["Ayşe", "Mehmet", "Zeynep", "Can", "Ali"])

    def test_calculate_points_for_top_four(self):
        self.assertEqual(self.game.calculate_points(1), 400)
        self.assertEqual(self.game.calculate_points(2), 300)
        self.assertEqual(self.game.calculate_points(3), 200)
        self.assertEqual(self.game.calculate_points(4), 100)
        self.assertEqual(self.game.calculate_points(5), 0)

    def test_score_round_applies_only_first_four_unique_winners(self):
        self.game.score_round(["Ayşe", "ayşe", "Mehmet", "Zeynep", "Can", "Ali"])

        leaderboard = {player.name: player.score for player in self.game.leaderboard()}
        self.assertEqual(leaderboard["Ayşe"], 400)
        self.assertEqual(leaderboard["Mehmet"], 300)
        self.assertEqual(leaderboard["Zeynep"], 200)
        self.assertEqual(leaderboard["Can"], 100)
        self.assertEqual(leaderboard["Ali"], 0)

    def test_generate_hint_keeps_word_length_and_reveals_letters(self):
        hint = self.game.generate_hint("algoritma")
        self.assertEqual(len(hint), len("algoritma"))
        self.assertIn("_", hint)
        self.assertTrue(any(ch != "_" for ch in hint))


    def test_scores_accumulate_across_rounds(self):
        self.game.score_round(["Ayşe", "Mehmet"])
        self.game.score_round(["Mehmet", "Can"])

        leaderboard = {player.name: player.score for player in self.game.leaderboard()}
        self.assertEqual(leaderboard["Ayşe"], 400)
        self.assertEqual(leaderboard["Mehmet"], 700)
        self.assertEqual(leaderboard["Can"], 300)

    def test_register_players_keeps_original_display_name(self):
        self.assertIn("ayşe", self.game.players)
        self.assertEqual(self.game.players["ayşe"].name, "Ayşe")


if __name__ == "__main__":
    unittest.main()
