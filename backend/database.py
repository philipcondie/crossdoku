from sqlmodel import create_engine, SQLModel, Session

from .models import *

# database set up
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url,connect_args=connect_args,echo=True)

def create_db_and_tables():
    import os
    if os.path.exists(sqlite_file_name):
        os.remove(sqlite_file_name)
    SQLModel.metadata.create_all(engine)

def close_db():
    engine.dispose()
    # remove the file for now
    import os
    if os.path.exists(sqlite_file_name):
        os.remove(sqlite_file_name)

def get_session():
    with Session(engine) as session:
        yield session

def seed_database():
    import datetime

    player1 = Player(name="phil")
    player2 = Player(name="spencer")

    game1 = Game(
        name="Sudoku",
        scoreMethod=ScoreMethod.LOW,
        players=[player1,player2])
    game2 = Game(
        name="Crossword",
        scoreMethod=ScoreMethod.LOW,
        players=[player1, player2])

    with Session(engine) as session:
        # Add and commit players and games first to get their IDs
        session.add(player1)
        session.add(player2)
        session.add(game1)
        session.add(game2)
        session.commit()

        # Refresh to get auto-generated IDs
        session.refresh(player1)
        session.refresh(player2)
        session.refresh(game1)
        session.refresh(game2)

        # Now create scores using the actual IDs
        scores = [
            # Phil's Sudoku scores
            Score(date=datetime.date(2025, 12, 1), playerId=player1.id, gameId=game1.id, score=180),
            Score(date=datetime.date(2025, 12, 2), playerId=player1.id, gameId=game1.id, score=165),
            Score(date=datetime.date(2025, 12, 3), playerId=player1.id, gameId=game1.id, score=172),

            # Spencer's Sudoku scores
            Score(date=datetime.date(2025, 12, 1), playerId=player2.id, gameId=game1.id, score=100),
            Score(date=datetime.date(2025, 12, 2), playerId=player2.id, gameId=game1.id, score=188),

            # Phil's Crossword scores
            Score(date=datetime.date(2025, 12, 1), playerId=player1.id, gameId=game2.id, score=240),
            Score(date=datetime.date(2025, 12, 3), playerId=player1.id, gameId=game2.id, score=225),

            # Spencer's Crossword scores
            Score(date=datetime.date(2025, 12, 1), playerId=player2.id, gameId=game2.id, score=200),
            Score(date=datetime.date(2025, 12, 3), playerId=player2.id, gameId=game2.id, score=298),
        ]

        # Add all scores
        for score in scores:
            session.add(score)

        session.commit()