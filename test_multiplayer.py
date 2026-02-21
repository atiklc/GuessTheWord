import unittest

from multiplayer import PlayerState, Room


class MultiplayerRoomTests(unittest.TestCase):
    def setUp(self):
        self.room = Room(code="ABC123", host_id="h1", total_rounds=2, words=["kelime"])
        self.room.players["h1"] = PlayerState(name="Host")
        self.room.players["p2"] = PlayerState(name="P2")
        self.room.players["p3"] = PlayerState(name="P3")

    def test_round_finalizes_after_all_submitted(self):
        self.room.start_round()
        self.room.submit_guess("h1", "kelime")
        self.room.submit_guess("p2", "yanlis")
        self.room.submit_guess("p3", "kelime")

        self.assertTrue(self.room.all_submitted())
        self.room.finalize_round()

        board = {row["name"]: row["score"] for row in self.room.leaderboard()}
        self.assertEqual(board["Host"], 400)
        self.assertEqual(board["P3"], 300)
        self.assertEqual(board["P2"], 0)

    def test_game_finishes_on_last_round(self):
        self.room.start_round()
        self.room.submit_guess("h1", "kelime")
        self.room.submit_guess("p2", "kelime")
        self.room.submit_guess("p3", "kelime")
        self.room.finalize_round()
        self.assertEqual(self.room.status, "round_result")

        self.room.start_round()
        self.room.submit_guess("h1", "kelime")
        self.room.submit_guess("p2", "yanlis")
        self.room.submit_guess("p3", "yanlis")
        self.room.finalize_round()
        self.assertEqual(self.room.status, "finished")


if __name__ == "__main__":
    unittest.main()
