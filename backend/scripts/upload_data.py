#!/usr/bin/env python3
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select
from sqlalchemy.dialects.postgresql import insert
import csv
import sys
from pathlib import Path
import typer

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.models import Player, Game, Score, player_game_table
from backend.seeding import SEED_DIR, GAME_CONFIGS, load_scores_from_csv



cli = typer.Typer()

@cli.command()
def upload_data(
    db_url: str = typer.Option(
        ...,
        "--db-url",
        envvar="DATABASE_URL",
        help="Database connection URL"
    ),
):
    if not db_url.startswith("postgresql"):
        print("Only run data upload to the production database")
        return
    
    engine = create_engine(
        db_url,
        pool_pre_ping=True
    )
    
    with Session(engine) as session:
        game_ids = upload_games(session)

    with Session(engine) as session:
        player_ids = upload_players(session)
    
    with Session(engine) as session:
        upload_scores(session, game_ids, player_ids)

    with Session(engine) as session:
        upload_player_game_links(session, game_ids, player_ids)
    
    print("Completed Data Upload")


def upload_games(session: Session) -> dict[str,int]:
    for config in GAME_CONFIGS:
        stmt = insert(Game).values(
            name=config["name"],
            scoreMethod=config["scoreMethod"]
        )
        stmt = stmt.on_conflict_do_nothing(index_elements=["name"])
        session.execute(stmt)
    session.commit()
    return {g.name: g.id for g in session.scalars(select(Game))}

def upload_players(session: Session) -> dict [str,int]:
    # get player names
    all_player_names = set()
    for config in GAME_CONFIGS:
        csv_path = SEED_DIR / config["csv"]
        with open(csv_path) as f:
            reader = csv.reader(f)
            header = next(reader)
            all_player_names.update(header[1:])

    # create players
    for name in all_player_names:
        stmt = insert(Player).values(
            name=name
        )
        stmt = stmt.on_conflict_do_nothing(index_elements=["name"])
        session.execute(stmt)
    session.commit()
    return {p.name: p.id for p in session.scalars(select(Player))}

def upload_scores(session: Session, game_ids: dict[str,int], player_ids: dict[str,int]):
    for config in GAME_CONFIGS:
        score_rows = [
            {
                "playerId": player_ids[row["player_name"]],
                "gameId": game_ids[config["name"]],
                "date": row["date"],
                "score": row["score"],
            }
            for row in load_scores_from_csv(SEED_DIR / config["csv"])
        ]
        stmt = insert(Score).values(score_rows)
        stmt = stmt.on_conflict_do_nothing(constraint="uq_player_game_date")
        session.execute(stmt)
    session.commit()

def upload_player_game_links(session: Session, game_ids: dict[str,int], player_ids: dict[str,int]):
    for config in GAME_CONFIGS:
        csv_path = SEED_DIR / config["csv"]
        with open(csv_path) as f:
            reader = csv.reader(f)
            header = next(reader)
            game_player_names = header[1:]

        game_id = game_ids[config["name"]]
        for name in game_player_names:
            stmt = insert(player_game_table).values(game_id=game_id, player_id=player_ids[name])
            stmt = stmt.on_conflict_do_nothing(index_elements=["player_id", "game_id"])
            session.execute(stmt)
    session.commit()

if __name__ == "__main__":
    cli()