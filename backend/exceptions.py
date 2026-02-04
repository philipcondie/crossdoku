from fastapi import HTTPException, status

class ScoreboardExcepction(HTTPException):
    pass

class DuplicateScoreException(ScoreboardExcepction):
    def __init__(self,player: str, game: str, date:str, score: int):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Score of {score} already exists for {player} in {game} for {date} "
        )

class InvalidDateException(ScoreboardExcepction):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid date in the request")

class InvalidUpdateException(ScoreboardExcepction):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND,detail="Cannot update non-existent score")

class InvalidPasswordException(ScoreboardExcepction):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid password")