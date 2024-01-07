import pytest
from sqlalchemy.orm import Session

from app.events.models import Event
from app.tickets import crud
from app.tickets.models import TicketCategory
from app.tickets.schemas import TicketCategoryCreate


class TestTicketCategory:
    def test_create(self, db: Session, event: Event) -> None:
        category_in = TicketCategoryCreate(name="example", quota=100, event_id=event.id)
        category = crud.ticket_category.create(db, obj_in=category_in)
        assert isinstance(category, TicketCategory)
        assert category.name == category_in.name
        assert category.quota == category_in.quota
        assert category.event_id == category_in.event_id

    def test_remove(self, db: Session, ticket_category: TicketCategory) -> None:
        crud.ticket_category.remove(db, id_=ticket_category.id)
        ticket_category2 = crud.ticket_category.get(db, id_=ticket_category.id)
        assert ticket_category2 is None

    def test_get_all_by_event(self, db: Session, ticket_categories: list[TicketCategory], event: Event) -> None:
        categories = crud.ticket_category.get_all_by_event(db, event_id=event.id)
        assert len(categories) == len(ticket_categories)

    @pytest.mark.usefixtures("ticket", "ticket_category")
    def test_get_all_by_event_tickets_left(
        self,
        db: Session,
        event: Event,
    ) -> None:
        categories = crud.ticket_category.get_all_by_event(db, event_id=event.id)
        category = categories[0]
        tickets_quota = category[0].quota
        tickets_left = category[1]
        assert tickets_left == tickets_quota - 1
