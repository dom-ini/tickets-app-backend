from unittest.mock import Mock

import pytest

from app.events import crud


@pytest.fixture(name="mock_event")
def get_mock_event() -> Mock:
    return Mock()


@pytest.fixture(name="mock_artist")
def get_mock_artist() -> Mock:
    return Mock()


def test_artists(mock_event: Mock, mock_artist: Mock) -> None:
    expected = [mock_artist]
    mock_event.artists = expected
    artists = crud.event.artists(mock_event)

    assert artists == expected


def test_add_artist(mock_db: Mock, mock_event: Mock, mock_artist: Mock) -> None:
    crud.event.add_artist(mock_db, event=mock_event, artist=mock_artist)
    mock_event.artists.append.assert_called_once_with(mock_artist)


def test_remove_artist(mock_db: Mock, mock_event: Mock, mock_artist: Mock) -> None:
    crud.event.remove_artist(mock_db, event=mock_event, artist=mock_artist)
    mock_event.artists.remove.assert_called_once_with(mock_artist)
