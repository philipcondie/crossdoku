from fastapi import HTTPException, status

class ScoreboardExcepction(HTTPException):
    pass

class DuplicateScoreException(ScoreboardExcepction):
    def __init__(self,player: str, game: str, date:str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Score already exists for {player} in {game} for {date}"
        )

class InvalidDateException(ScoreboardExcepction):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid date in the request")