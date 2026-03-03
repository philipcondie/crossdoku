import datetime
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ..models import Base, Game, Player, Score, ScoreMethod
from ..schemas import ScoreCreate
from ..services import (
    addNewScore,
    getAllPlayers,
    getDailyScores,
    getScoreboardDaily,
    updateScore,
)


class ServicesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)

        self.player = Player(name="JohnDoe")
        self.game = Game(name="Sudoku", scoreMethod=ScoreMethod.LOW)
        self.session.add_all([self.player, self.game])
        self.session.commit()
        self.session.refresh(self.player)
        self.session.refresh(self.game)

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_get_all_players_returns_orm_objects(self) -> None:
        players = getAllPlayers(self.session)

        self.assertEqual(len(players), 1)
        self.assertIsInstance(players[0], Player)
        self.assertEqual(players[0].name, "JohnDoe")

    def test_add_and_update_score_round_trip(self) -> None:
        created = addNewScore(
            self.session,
            ScoreCreate(
                date=datetime.date(2026, 1, 1),
                score=5,
                playerName="JohnDoe",
                gameName="Sudoku",
            ),
        )

        self.assertEqual(created["score"], 5)
        self.assertEqual(created["playerName"], "JohnDoe")

        updated = updateScore(
            self.session,
            ScoreCreate(
                date=datetime.date(2026, 1, 1),
                score=4,
                playerName="JohnDoe",
                gameName="Sudoku",
            ),
        )

        self.assertEqual(updated["score"], 4)

    def test_daily_score_queries_return_schema_shapes(self) -> None:
        self.session.add(
            Score(
                date=datetime.date(2026, 1, 1),
                playerId=self.player.id,
                gameId=self.game.id,
                score=5,
            )
        )
        self.session.commit()

        daily_scores = getDailyScores(
            self.session,
            startDate=datetime.date(2026, 1, 1),
            endDate=datetime.date(2026, 1, 1),
        )
        scoreboard = getScoreboardDaily(self.session, datetime.date(2026, 1, 1))

        self.assertEqual(len(daily_scores), 1)
        self.assertEqual(daily_scores[0].playerName, "JohnDoe")
        self.assertEqual(daily_scores[0].gameName, "Sudoku")
        self.assertEqual(scoreboard.players[0].name, "JohnDoe")
        self.assertEqual(scoreboard.games[0].name, "Sudoku")
