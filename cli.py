import importlib
import json
from contextlib import contextmanager
from typing import Any, Generator

import click
from sqlalchemy import insert, text
from sqlalchemy.orm import Session

from app.db.session import SessionLocal

MODELS_MODULE_NAME = "app.db.base"
IMAGE_URL_QUERIES = [
    text(
        """
        UPDATE event
        SET poster_vertical = 'event-' || id || '.webp', poster_horizontal = 'event-' || id || '-hor.webp';
    """
    ),
    text(
        """
        UPDATE speaker
        SET photo = 'speaker-' || id || '.webp';
    """
    ),
]


class DBDataImporter:
    MODULE_NAME = "app.db.base"

    def __init__(self, session: Session) -> None:
        self._session = session

    def from_json(self, file_path: str) -> None:
        data = get_json_content(file_path)
        insert_data_to_db(session=self._session, module_name=self.MODULE_NAME, raw_data=data)


def get_json_content(file_path: str) -> list[dict]:
    with open(file_path, "r", encoding="utf-8") as file:
        content = json.load(file)
    if not isinstance(content, list):
        raise ValueError("JSON data should be a list")
    return content


@contextmanager
def create_db_session() -> Generator:
    try:
        session = SessionLocal()
        yield session
    finally:
        session.close()


def get_model_class(model_name: str, module_name: str) -> Any:
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        raise ImportError(f"Unable to import module '{module_name}'") from exc

    try:
        model = getattr(module, model_name)
    except AttributeError as exc:
        raise ImportError(f"Model '{model_name}' not found in module '{module_name}'") from exc

    return model


def insert_row_to_db(session: Session, table: Any, row: dict) -> None:
    query = insert(table).values(**row)
    session.execute(query)


def insert_data_to_db(session: Session, module_name: str, raw_data: list[dict]) -> None:
    for entry in raw_data:
        model_name = entry["model"]
        model = get_model_class(model_name, module_name)

        data: list[dict] = entry["data"]
        for row in data:
            insert_row_to_db(session, model, row)


@click.group()
def cli() -> None:
    pass


@contextmanager
def get_safe_session() -> Generator:
    with create_db_session() as session:  # type: Session
        try:
            yield session
            session.commit()
        except Exception as exc:
            print(f"Error: {exc}")
            print("Rolling back...")
            session.rollback()


@cli.command()
@click.argument("json_file", type=click.Path(exists=True))
def populate_db(json_file: str) -> None:
    """Populate database with JSON data"""
    print(f"Reading data from {json_file}...")
    with get_safe_session() as session:  # type: Session
        DBDataImporter(session).from_json(json_file)
        print("Data import completed")


@cli.command()
def regenerate_image_urls() -> None:
    """Set image urls for event posters and speaker photos"""
    print("Regenerating urls...")
    with get_safe_session() as session:  # type: Session
        for query in IMAGE_URL_QUERIES:
            session.execute(query)
        print("Urls regenerated")


if __name__ == "__main__":
    cli()
