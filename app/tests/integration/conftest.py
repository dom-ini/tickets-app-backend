# pylint: disable=W0621,W0613,E1101
from datetime import datetime, timedelta
from typing import Generator

import pytest
import sqlalchemy
from fastapi_mail import ConnectionConfig, FastMail
from sqlalchemy.orm.session import Session, SessionTransaction
from starlette.testclient import TestClient

from app.auth import crud, models, schemas
from app.auth.utils import generate_valid_password
from app.common.deps import get_db
from app.common.emails import MailSender, get_mailer_config, mailer
from app.core.config import settings
from app.db import base
from app.events import crud as event_crud, models as event_models, schemas as event_schemas
from app.main import app
from app.tests.integration.test_db_config.initial_data import INITIAL_DATA
from app.tests.integration.test_db_config.session import TestingSessionLocal, engine
from app.tests.integration.test_db_config.setup_db import init_db
from app.tests.integration.utils.users import get_normal_user_token_headers, get_superuser_token_headers
from app.tickets import crud as ticket_crud, models as ticket_models, schemas as ticket_schemas

base.Base.metadata.drop_all(bind=engine)
base.Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db() -> None:
    init_db(INITIAL_DATA)


@pytest.fixture()
def db() -> Generator:
    """
    Create nested transaction and rollback it on tear down, so that transaction is never committed to database
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    nested = connection.begin_nested()

    @sqlalchemy.event.listens_for(session, "after_transaction_end")
    def end_savepoint(session: Session, transaction: SessionTransaction) -> None:
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


def create_test_mailer() -> MailSender:
    config = ConnectionConfig(**get_mailer_config())
    config.SUPPRESS_SEND = True
    mail_engine = FastMail(config)
    return MailSender(mail_engine)


@pytest.fixture()
def client(db: Session) -> Generator:
    def override_get_db() -> Generator:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[mailer] = create_test_mailer
    yield TestClient(app)
    del app.dependency_overrides[get_db]
    del app.dependency_overrides[mailer]


@pytest.fixture()
def mail_engine() -> MailSender:
    return create_test_mailer()


@pytest.fixture()
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture()
def normal_user_token_headers(client: TestClient) -> dict[str, str]:
    return get_normal_user_token_headers(client)


@pytest.fixture()
def superuser(db: Session) -> models.User:
    user_in = schemas.UserCreate(
        email="random@example.com",
        password=generate_valid_password(),
        is_activated=True,
        is_disabled=False,
        is_superuser=True,
    )
    return crud.user.create(db, obj_in=user_in)


@pytest.fixture(name="location")
def create_location(db: Session) -> event_models.Location:
    location_in = event_schemas.LocationCreate(
        name="Location", city="New York", slug="location", latitude=50.0, longitude=18.0
    )
    return event_crud.location.create(db, obj_in=location_in)


@pytest.fixture(name="organizer")
def create_organizer(db: Session) -> event_models.Organizer:
    organizer_in = event_schemas.OrganizerCreate(name="Organizer")
    return event_crud.organizer.create(db, obj_in=organizer_in)


@pytest.fixture(name="event_type")
def create_event_type(db: Session) -> event_models.EventType:
    event_type_in = event_schemas.EventTypeCreate(name="event type", slug="event-type")
    return event_crud.event_type.create(db, obj_in=event_type_in)


@pytest.fixture(name="nested_event_type")
def create_nested_event_type(db: Session, event_type: event_models.EventType) -> event_models.EventType:
    event_type_in = event_schemas.EventTypeCreate(
        name="nested event type", slug="nested-event-type", parent_type_id=event_type.id
    )
    return event_crud.event_type.create(db, obj_in=event_type_in)


@pytest.fixture(name="speaker")
def create_speaker(db: Session) -> event_models.Speaker:
    speaker_in = event_schemas.SpeakerCreate(name="Speaker", description="Description", slug="speaker")
    return event_crud.speaker.create(db, obj_in=speaker_in)


@pytest.fixture(name="event")
def create_event(
    db: Session,
    location: event_models.Location,
    organizer: event_models.Organizer,
    event_type: event_models.EventType,
    superuser: models.User,
) -> event_models.Event:
    event_in = event_schemas.EventCreate(
        name="Event",
        description="Description",
        slug="event",
        held_at=datetime.now() + timedelta(days=30),
        is_active=True,
        location_id=location.id,
        organizer_id=organizer.id,
        event_type_id=event_type.id,
        created_by_id=superuser.id,
    )
    return event_crud.event.create(db, obj_in=event_in)


@pytest.fixture(name="test_user")
def get_test_user(db: Session) -> models.User:
    user = crud.user.get_by_email(db, email=settings.TEST_USER_EMAIL)
    assert user is not None
    return user


@pytest.fixture(name="ticket_category")
def get_ticket_category(db: Session, event: event_models.Event) -> ticket_models.TicketCategory:
    category_in = ticket_schemas.TicketCategoryCreate(name="example", quota=100, event_id=event.id)
    return ticket_crud.ticket_category.create(db, obj_in=category_in)
