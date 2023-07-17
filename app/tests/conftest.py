# pylint: disable=W0621,W0613,E1101
from typing import Generator

import pytest
import sqlalchemy
from sqlalchemy.orm.session import Session, SessionTransaction
from starlette.testclient import TestClient

from app.common.deps import get_db
from app.db import base
from app.main import app
from app.tests.test_db.session import TestingSessionLocal, engine
from app.tests.test_db.setup_db import init_db
from app.tests.utils.users import get_normal_user_token_headers, get_superuser_token_headers

base.Base.metadata.drop_all(bind=engine)
base.Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db() -> None:
    init_db()


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


@pytest.fixture()
def client(db: Session) -> Generator:
    def override_get_db() -> Generator:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]


@pytest.fixture()
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture()
def normal_user_token_headers(client: TestClient) -> dict[str, str]:
    return get_normal_user_token_headers(client)
