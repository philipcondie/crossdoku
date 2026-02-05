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

        # Generate scores for 35 days with variety
        import random
        random.seed(42)  # Reproducible randomness for consistent seed data

        today = datetime.date.today()
        scores = []

        # Define player participation patterns (some players play more than others)
        # Probability of each player having a score on any given day for each game
        participation = {
            player1: {"sudoku": 0.85, "crossword": 0.80},  # Phil - very active
            player2: {"sudoku": 0.75, "crossword": 0.70},  # Spencer - active
            player3: {"sudoku": 0.60, "crossword": 0.55},  # Nate - moderate
            player4: {"sudoku": 0.50, "crossword": 0.65},  # Morgan - moderate, prefers crossword
            player5: {"sudoku": 0.70, "crossword": 0.40},  # Sarah - prefers sudoku
            player6: {"sudoku": 0.30, "crossword": 0.35},  # Ally - casual player
            player7: {"sudoku": 0.45, "crossword": 0.50},  # Jonathan - moderate
            player8: {"sudoku": 0.15, "crossword": 0.20},  # Rebecca - rare player (edge case)
        }

        # Score ranges (in seconds) for each player to give them different skill levels
        score_ranges = {
            player1: {"sudoku": (120, 240), "crossword": (180, 300)},   # Phil - good
            player2: {"sudoku": (90, 180), "crossword": (150, 280)},    # Spencer - very good
            player3: {"sudoku": (150, 300), "crossword": (200, 350)},   # Nate - average
            player4: {"sudoku": (180, 350), "crossword": (160, 280)},   # Morgan - avg sudoku, good crossword
            player5: {"sudoku": (100, 200), "crossword": (250, 400)},   # Sarah - great sudoku, slow crossword
            player6: {"sudoku": (200, 400), "crossword": (220, 380)},   # Ally - casual
            player7: {"sudoku": (140, 280), "crossword": (190, 320)},   # Jonathan - decent
            player8: {"sudoku": (250, 450), "crossword": (280, 450)},   # Rebecca - beginner
        }

        for days_ago in range(35):
            score_date = today - datetime.timedelta(days=days_ago)

            for player in all_players:
                # Sudoku scores
                if random.random() < participation[player]["sudoku"]:
                    min_score, max_score = score_ranges[player]["sudoku"]
                    scores.append(Score(
                        date=score_date,
                        playerId=player.id,
                        gameId=game1.id,
                        score=random.randint(min_score, max_score)
                    ))

                # Crossword scores
                if random.random() < participation[player]["crossword"]:
                    min_score, max_score = score_ranges[player]["crossword"]
                    scores.append(Score(
                        date=score_date,
                        playerId=player.id,
                        gameId=game2.id,
                        score=random.randint(min_score, max_score)
                    ))

        # Add all scores
        for score in scores:
            session.add(score)

        session.commit()