from .database import create_db_and_tables, close_db, seed_database, engine, get_session
from sqlmodel import Session, select
from .models import *

create_db_and_tables()
seed_database()


with Session(engine) as session:
    players = session.exec(select(Player)).all()
    for player in players:
        print("="*50)
        print(player.id)
        print(player.name)
        for game in player.games:
            print(game.id)
            print(game.name)

close_db()