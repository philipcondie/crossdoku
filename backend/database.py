from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select
from sqlalchemy.pool import StaticPool
from .models import Base, Player, ScoreMethod, Game, Score
from .config import get_settings

# database set up
settings = get_settings()

is_sqlite = settings.database_url.startswith("sqlite")
is_memory = ":memory:" in settings.database_url

if is_memory:
    # In-memory SQLite: use StaticPool so all connections share the same DB
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=(settings.environment == "dev"),
    )
else:
    connect_args = {"check_same_thread": False} if is_sqlite else {}
    engine = create_engine(
        settings.database_url,
        connect_args=connect_args,
        echo=(settings.environment == "dev"),
        pool_pre_ping=True,
    )

def create_db_and_tables():
    Base.metadata.create_all(engine)

def close_db():
    engine.dispose()

def get_session():
    with Session(engine) as session:
        yield session

def seed_database():
    with Session(engine) as session:
        existing = session.execute(select(Player)).first()
        if existing:
            return # already seeded

    import csv
    import datetime
    from pathlib import Path

    seed_dir = Path(__file__).parent / "seed_data"

    def load_scores_from_csv(csv_path):
        scores = []
        with open(csv_path) as f:
            reader = csv.reader(f)
            header = next(reader)
            player_names = header[1:]  # skip "Date" column

            for row in reader:
                date_str = row[0]
                month, day = date_str.split("/")
                score_date = datetime.date(2026, int(month), int(day))

                for i, value in enumerate(row[1:]):
                    if value.strip():
                        scores.append({
                            "date": score_date,
                            "player_name": player_names[i],
                            "score": int(value),
                        })
        return scores

    # Define games and their corresponding CSV files
    game_configs = [
        {"name": "Crossword", "scoreMethod": ScoreMethod.LOW, "csv": "crossword.csv"},
        {"name": "Sudoku", "scoreMethod": ScoreMethod.LOW, "csv": "sudoku.csv"},
    ]

    with Session(engine) as session:
        # Collect all unique player names from all CSVs
        all_player_names = set()
        for config in game_configs:
            csv_path = seed_dir / config["csv"]
            with open(csv_path) as f:
                reader = csv.reader(f)
                header = next(reader)
                all_player_names.update(header[1:])

        # Create players
        players = {}
        for name in all_player_names:
            player = Player(name=name)
            session.add(player)
            players[name] = player
        session.commit()
        for player in players.values():
            session.refresh(player)

        # Create games and load scores from CSVs
        for config in game_configs:
            game = Game(
                name=config["name"],
                scoreMethod=config["scoreMethod"],
                players=list(players.values()),
            )
            session.add(game)
            session.commit()
            session.refresh(game)

            score_entries = load_scores_from_csv(seed_dir / config["csv"])
            for entry in score_entries:
                player = players[entry["player_name"]]
                session.add(Score(
                    date=entry["date"],
                    playerId=player.id,
                    gameId=game.id,
                    score=entry["score"],
                ))

        session.commit()