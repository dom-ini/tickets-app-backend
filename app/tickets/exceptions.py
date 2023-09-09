from fastapi import HTTPException, status


class TicketCategoryNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket category not found")


class TicketAlreadyReserved(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="User can reserve only one ticket per event")


class TicketNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")


class NoMoreTicketsLeft(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Could not reserve ticket - there are no tickets left"
        )
