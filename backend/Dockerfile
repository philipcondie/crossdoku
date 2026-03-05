# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . ./backend/

EXPOSE 8000
CMD ["sh", "-c", "cd /app/backend && alembic upgrade head && cd /app && uvicorn backend.main:app --host 0.0.0.0 --port 8000"]