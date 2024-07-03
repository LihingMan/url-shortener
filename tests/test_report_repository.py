import pytest
from unittest.mock import MagicMock
from app.models.report import Report
from app.models.shorturl import ShortURL
from app.repository.report_repository import insert_one

@pytest.fixture
def mock_db_session():
    session = MagicMock()

    # mock db setup
    mock_short_url = MagicMock(spec=ShortURL)
    mock_report = MagicMock(spec=Report)
    mock_short_url.report.return_value = mock_report
    yield session

def test_find_or_insert_one_new_url(mock_db_session):
    insert_one(mock_db_session, 1, "192.168.1.1", {"country": "Testland", "city": "Testville"})
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called() 
