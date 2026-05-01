from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Generator

import pytest
from sqlalchemy.orm import Session

from app.auth import crud as auth_crud
from app.auth.models import User
from app.auth.schemas.user import UserCreate
from app.core.config import settings
from app.events import crud as event_crud
from app.events.models import Event, EventType, Location, Organizer
from app.events.schemas.event import EventCreate
from app.events.schemas.event_type import EventTypeCreate
from app.events.schemas.location import LocationCreate
from app.events.schemas.organizer import OrganizerCreate
from app.tests.integration.test_db_config.session import TestingSessionLocal
from app.tickets import crud as tickets_crud
from app.tickets.deps import reserve_ticket_if_available
from app.tickets.exceptions import NoMoreTicketsLeft
from app.tickets.models import TicketCategory
from app.tickets.schemas.ticket import TicketCreateBody
from app.tickets.schemas.ticket_category import TicketCategoryCreate


def get_test_user_email(index: int) -> str:
    return f"race-condition-{index}@example.com"


@pytest.fixture(name="db")
def create_session() -> Generator:
    with TestingSessionLocal() as session:
        yield session


class TestTicketDeps:
    users_count: int = 5

    @pytest.fixture
    def users(self, db: Session) -> list[User]:
        users = [
            auth_crud.user.create(
                db,
                obj_in=UserCreate(
                    email=get_test_user_email(i), password=settings.TEST_USER_PASSWORD, is_activated=True
                ),
            )
            for i in range(self.users_count)
        ]
        return users

    @pytest.fixture
    def user(self, users: list[User]) -> User:
        return users[0]

    @pytest.fixture
    def location(self, db: Session) -> Location:
        location_in = LocationCreate(name="Location", city="New York", slug="location", latitude=50.0, longitude=18.0)
        return event_crud.location.create(db, obj_in=location_in)

    @pytest.fixture
    def organizer(self, db: Session) -> Organizer:
        organizer_in = OrganizerCreate(name="Organizer")
        return event_crud.organizer.create(db, obj_in=organizer_in)

    @pytest.fixture
    def event_type(self, db: Session) -> EventType:
        event_type_in = EventTypeCreate(name="event type", slug="event-type")
        return event_crud.event_type.create(db, obj_in=event_type_in)

    @pytest.fixture
    def event(  # pylint: disable=too-many-arguments
        self, db: Session, user: User, location: Location, organizer: Organizer, event_type: EventType
    ) -> Event:
        event_in = EventCreate(
            name="Test Event",
            description="Description",
            slug="test-event",
            is_active=True,
            held_at=datetime.now() + timedelta(days=30),
            created_by_id=user.id,
            location_id=location.id,
            organizer_id=organizer.id,
            event_type_id=event_type.id,
        )
        return event_crud.event.create(db, obj_in=event_in)

    @pytest.fixture
    def ticket_category(self, db: Session, event: Event) -> TicketCategory:
        category_in = TicketCategoryCreate(name="single_quota", quota=1, event_id=event.id)
        return tickets_crud.ticket_category.create(db, obj_in=category_in)

    @pytest.fixture
    def teardown(  # pylint: disable=too-many-arguments
        self,
        db: Session,
        users: list[User],
        location: Location,
        organizer: Organizer,
        event_type: EventType,
        event: Event,
        ticket_category: TicketCategory,
    ) -> Generator:
        yield
        for user in users:
            tickets = tickets_crud.ticket.get_all_by_user(db, user_id=user.id)
            for ticket in tickets:
                tickets_crud.ticket.remove(db, id_=ticket.id)
        tickets_crud.ticket_category.remove(db, id_=ticket_category.id)
        event_crud.event.remove(db, id_=event.id)
        event_crud.event_type.remove(db, id_=event_type.id)
        event_crud.location.remove(db, id_=location.id)
        event_crud.organizer.remove(db, id_=organizer.id)
        for user in users:
            auth_crud.user.remove(db, id_=user.id)

    def _reserve_ticket(self, user: User, ticket_category: TicketCategory) -> bool:
        ticket_data = TicketCreateBody(email=user.email, ticket_category_id=ticket_category.id)
        with TestingSessionLocal() as thread_db:
            try:
                reserve_ticket_if_available(thread_db, ticket_data=ticket_data, user=user)
                return True
            except NoMoreTicketsLeft:
                return False

    @pytest.mark.usefixtures("teardown")
    def test_reserve_ticket_if_available_has_no_race_condition(
        self, ticket_category: TicketCategory, users: list[User]
    ) -> None:
        with ThreadPoolExecutor(max_workers=len(users)) as executor:
            result = list(
                executor.map(lambda user: self._reserve_ticket(user=user, ticket_category=ticket_category), users)
            )

        assert sum(result) == 1, "Only one ticket should be reserved successfully"
