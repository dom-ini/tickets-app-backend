import datetime
from unittest.mock import Mock

import pytest

from app.events import crud


@pytest.fixture(name="mock_event")
def get_mock_event() -> Mock:
    return Mock()


@pytest.fixture(name="mock_speaker")
def get_mock_speaker() -> Mock:
    return Mock()


def test_speakers(mock_event: Mock, mock_speaker: Mock) -> None:
    expected = [mock_speaker]
    mock_event.speakers = expected
    speakers = crud.event.speakers(mock_event)

    assert speakers == expected


def test_add_speaker(mock_db: Mock, mock_event: Mock, mock_speaker: Mock) -> None:
    crud.event.add_speaker(mock_db, event=mock_event, speaker=mock_speaker)
    mock_event.speakers.append.assert_called_once_with(mock_speaker)


def test_remove_speaker(mock_db: Mock, mock_event: Mock, mock_speaker: Mock) -> None:
    crud.event.remove_speaker(mock_db, event=mock_event, speaker=mock_speaker)
    mock_event.speakers.remove.assert_called_once_with(mock_speaker)


@pytest.mark.parametrize("expected", [True, False])
def test_is_active(mock_event: Mock, expected: bool) -> None:
    mock_event.is_active = expected
    assert crud.event.is_active(mock_event) == expected


@pytest.mark.parametrize(
    "held_at,expected", [(datetime.datetime(2010, 1, 1), True), (datetime.datetime(2040, 9, 9), False)]
)
def test_is_expired(mock_event: Mock, held_at: datetime.datetime, expected: bool) -> None:
    mock_event.held_at = held_at
    assert crud.event.is_expired(mock_event) == expected
