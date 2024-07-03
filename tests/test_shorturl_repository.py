import pytest
from unittest.mock import MagicMock
from app.models.report import Report
from app.models.shorturl import ShortURL
from app.repository.shorturl_repository import NotFound, find_or_insert_one, find_original_url

@pytest.fixture
def mock_db_session():
    session = MagicMock()

    # mock db setup
    mock_short_url = MagicMock(spec=ShortURL)
    mock_report = MagicMock(spec=Report)
    mock_short_url.report.return_value = mock_report
    yield session

def test_find_or_insert_one_existing_url(mock_db_session):
    url = "http://example.com"
    short_url_hash = "abc123"

    mock_short_url = ShortURL(short_url=short_url_hash, original_url=url)
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_short_url

    result = find_or_insert_one(mock_db_session, short_url_hash, url)
    assert result == short_url_hash
    mock_db_session.add.assert_not_called()

def test_find_or_insert_one_new_url(mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    new_url = "http://newexample.com"
    result = find_or_insert_one(mock_db_session, "new123", new_url)

    assert result is not None
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called() 

def test_find_original_url_found(mock_db_session):
    url = "http://example.com"
    short_url_hash = "abc123"

    mock_short_url = ShortURL(short_url=short_url_hash, original_url=url)
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_short_url

    result = find_original_url(mock_db_session, short_url_hash)
    assert result.original_url == url

def test_find_original_url_not_found(mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(NotFound, match="Short URL does not exist!"):
        find_original_url(mock_db_session, "notfoundhash")
