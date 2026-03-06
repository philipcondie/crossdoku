from sqlalchemy.orm import Session
from sqlalchemy import select
import csv
import datetime
from pathlib import Path

from .models import Player, Game, Score, ScoreMethod

SEED_DIR = Path(__file__).parent / "seed_data"
GAME_CONFIGS = [
        {"name": "Crossword", "scoreMethod": ScoreMethod.LOW, "csv": "crossword.csv"},
        {"name": "Sudoku", "scoreMethod": ScoreMethod.LOW, "csv": "sudoku.csv"},
    ]

def load_scores_from_csv(csv_path):
    scores = []
    with open(csv_path) as f:
        reader = csv.reader(f)
        header = next(reader)
        player_names = header[1:]  # skip "Date" column

        for row in reader:
            date_str = row[0]
            month, day, year = date_str.split("/")
            score_date = datetime.date(int(year), int(month), int(day))

            for i, value in enumerate(row[1:]):
                if value.strip():
                    scores.append({
                        "date": score_date,
                        "player_name": player_names[i],
                        "score": int(value),
                    })
    return scores

def seed_database():    
    from .database import engine

    with Session(engine) as session:
        # Collect all unique player names from all CSVs
        all_player_names = set()
        for config in GAME_CONFIGS:
            csv_path = SEED_DIR / config["csv"]
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
        for config in GAME_CONFIGS:
            game = Game(
                name=config["name"],
                scoreMethod=config["scoreMethod"],
                players=list(players.values()),
            )
            session.add(game)
            session.commit()
            session.refresh(game)

            score_entries = load_scores_from_csv(SEED_DIR / config["csv"])
            for entry in score_entries:
                player = players[entry["player_name"]]
                session.add(Score(
                    date=entry["date"],
                    playerId=player.id,
                    gameId=game.id,
                    score=entry["score"],
                ))

        session.commit()