# Crossdoku

A collaborative puzzle scoring and leaderboard app for tracking daily Crossword and Sudoku results among a group of players. Calculates individual and combined rankings using T-scores, with monthly points standings.

## Features

- Submit and update scores for daily NYT puzzles (Crossword, Sudoku)
- Daily leaderboard with individual game rankings and combined T-scores
- Monthly standings tracking wins, participation, and combined performance
- Timezone-aware date handling aligned with NYT puzzle release times
- Password-protected access

## Tech Stack

| Layer    | Technology                              |
|----------|-----------------------------------------|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS |
| Backend  | FastAPI (Python 3.12), SQLAlchemy        |
| Database | PostgreSQL 15 (dev: SQLite in-memory)    |
| Infra    | Docker Compose                           |

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js (for frontend development)

### Run with Docker

```bash
docker-compose up
```

This starts the PostgreSQL database and backend API. The backend will be available at `http://localhost:8000` and auto-populates seed data on first run.

Then start the frontend separately:

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

### Environment Variables

**Backend** — set in `docker-compose.yml` or a `.env` file in `/backend`:

| Variable       | Default                                              | Description                        |
|----------------|------------------------------------------------------|------------------------------------|
| `DATABASE_URL` | `sqlite:///:memory:`                                 | PostgreSQL or SQLite connection URL |
| `CORS_ORIGINS` | `http://localhost:5173`                              | Allowed frontend origins           |
| `ENVIRONMENT`  | `development`                                        | App environment                    |
| `APP_PASSWORD` | `dev`                                                | App-level access password          |

**Frontend** — create a `.env` file in `/frontend`:

```
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
crossdoku/
├── backend/
│   ├── main.py          # FastAPI app and route registration
│   ├── models.py        # SQLAlchemy database models
│   ├── config.py        # Pydantic settings
│   ├── seeding.py       # Dev database seeding (ORM-based)
│   ├── seed_data/       # CSV files for initial players and scores
│   └── scripts/
│       └── upload_data.py  # Production backfill script (idempotent)
└── frontend/
    └── src/
        ├── components/  # UI components
        ├── pages/       # Route-level page components
        └── api/         # API client functions
```

### Backfilling Production Data

To upload seed data to a production PostgreSQL database:

```bash
cd backend
python scripts/upload_data.py --db-url "postgresql://..."
```

The script is idempotent — safe to run multiple times with no duplicate inserts.
### Database Migrations (Alembic)

Migrations live in `backend/alembic/versions/`. To generate a new migration after changing models:

```bash
cd backend
DATABASE_URL="postgresql+psycopg2://..." alembic revision --autogenerate -m "description"
```

Review the generated file in `alembic/versions/` before committing — autogenerate has known blind spots (e.g. `CheckConstraint`). Commit the migration file and it will be applied automatically on next deploy.

## Scoring

Scores are ranked using **T-scores** — a statistical normalization that allows fair comparison across different puzzle types (crossword times vs. sudoku times). A lower raw score is better for both games. No points are awarded for ties.

Monthly standings award points across four categories:
- **Participation** — completed all games on a given day
- **Individual wins** — best score per game per day
- **Combined wins** — best combined T-score per day
- **Total points** — aggregate of the above

## API Overview

| Method | Endpoint          | Description                          |
|--------|-------------------|--------------------------------------|
| POST   | `/auth/verify`    | Verify app password                  |
| GET    | `/players/`       | List all players                     |
| GET    | `/games/{player}` | Get games for a player               |
| POST   | `/score/`         | Submit a score                       |
| PUT    | `/score/`         | Update an existing score             |
| GET    | `/scores/daily`   | Daily scoreboard with rankings       |
| GET    | `/scores/monthly` | Monthly standings with point totals  |
| GET    | `/scores/combined`| Combined T-scores for a date         |
