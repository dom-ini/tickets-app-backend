from fastapi import HTTPException, status


class InvalidSortField(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid sorting field")


class InvalidFilterType(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid filtering type")


class InvalidFilterField(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid filtering field")
