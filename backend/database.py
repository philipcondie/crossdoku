from sqlmodel import create_engine, SQLModel, Session, select

from .models import *
from .config import get_settings

# database set up
settings = get_settings()

# SQLite requires check_same_thread=False for FastAPI's async handling
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(
    settings.database_url, 
    connect_args=connect_args, 
    echo=(settings.environment == "development"),
    pool_pre_ping=True
    )

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def close_db():
    engine.dispose()

def get_session():
    with Session(engine) as session:
        yield session

def seed_database():
    with Session(engine) as session:
        existing = session.exec(select(Player)).first()
        if existing:
            return # already seeded
    import datetime

    player1 = Player(name="Phil")
    player2 = Player(name="Spencer")
    player3 = Player(name="Nate")
    player4 = Player(name="Morgan")
    player5 = Player(name="Sarah")
    player6 = Player(name="Ally")
    player7 = Player(name="Jonathan")
    player8 = Player(name="Rebecca")

    all_players = [player1, player2, player3, player4, player5, player6, player7, player8]

    game1 = Game(
        name="Sudoku",
        scoreMethod=ScoreMethod.LOW,
        players=all_players)
    game2 = Game(
        name="Crossword",
        scoreMethod=ScoreMethod.LOW,
        players=all_players)

    with Session(engine) as session:
        # Add and commit players and games first to get their IDs
        for player in all_players:
            session.add(player)
        session.add(game1)
        session.add(game2)
        session.commit()

        # Refresh to get auto-generated IDs
        for player in all_players:
            session.refresh(player)
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