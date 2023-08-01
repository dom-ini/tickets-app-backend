from typing import Any, Mapping, Protocol, Type

from app.db.base_class import Base
from app.tests.test_db_config.session import TestingSessionLocal


class DataProtocol(Protocol):
    model: Type[Base]
    data: list[dict[str, Any]]


def init_db(initial_data: Mapping[str, DataProtocol]) -> None:
    session = TestingSessionLocal()
    for entry in initial_data.values():
        instances = [entry.model(**instance) for instance in entry.data]
        session.add_all(instances)
    session.commit()
