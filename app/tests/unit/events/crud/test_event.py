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
