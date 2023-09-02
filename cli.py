import importlib
import json
from contextlib import contextmanager
from typing import Any, Generator

import click
from sqlalchemy import insert
from sqlalchemy.orm import Session

from app.db.session import SessionLocal

MODELS_MODULE_NAME = "app.db.base"


class DBDataImporter:
    def __init__(self, session: Session) -> None:
        self._session = session

    def from_json(self, file_path: str) -> None:
        data = get_json_content(file_path)
        insert_data_to_db(self._session, data)


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


def get_model_class(model_name: str) -> Any:
    try:
        module = importlib.import_module(MODELS_MODULE_NAME)
    except ImportError as exc:
        raise ImportError(f"Unable to import module '{MODELS_MODULE_NAME}'") from exc

    try:
        model = getattr(module, model_name)
    except AttributeError as exc:
        raise ImportError(f"Model '{model_name}' not found in module '{MODELS_MODULE_NAME}'") from exc

    return model


def insert_row_to_db(session: Session, table: Any, row: dict) -> None:
    query = insert(table).values(**row)
    session.execute(query)


def insert_data_to_db(session: Session, raw_data: list[dict]) -> None:
    for entry in raw_data:
        model_name = entry["model"]
        model = get_model_class(model_name)

        data: list[dict] = entry["data"]
        for row in data:
            insert_row_to_db(session, model, row)


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("json_file", type=click.Path(exists=True))
def populate_db(json_file: str) -> None:
    """Populate database with JSON data"""
    print(f"Reading data from {json_file}...")
    with create_db_session() as session:  # type: Session
        try:
            DBDataImporter(session).from_json(json_file)
            session.commit()
            print("Data import completed")
        except Exception as exc:
            print(f"Error: {exc}")
            print("Rolling back...")
            session.rollback()


if __name__ == "__main__":
    cli()
