import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app
from app.database import get_db
from app.models.report import Report
from app.models.shorturl import ShortURL

GEOLOCATION_DATA = {"regionName": "Testland", "lat": "15", "lon": "10", "status": "success"}

# fixture for db dependency
@pytest.fixture
def mock_db_session():
    session = MagicMock()

    # mock db setup
    mock_short_url = MagicMock(spec=ShortURL)
    mock_report = MagicMock(spec=Report)
    mock_short_url.report.return_value = mock_report
    yield session

# http test client
@pytest.fixture
def client(mock_db_session):
    # Dependency override for db session
    app.dependency_overrides[get_db] = lambda: mock_db_session
    yield TestClient(app)
    del app.dependency_overrides[get_db]

@pytest.fixture
def short_url_obj():
    return ShortURL(id=1, original_url="http://example.com")

@pytest.fixture
def ip_address():
    return "192.168.1.1"

@pytest.fixture
def geolocation_data():
    return GEOLOCATION_DATA

@pytest.fixture
def mock_get_geo_from_ip(geolocation_data):
    mock = MagicMock(return_value=geolocation_data)
    return mock

@pytest.fixture
def mock_get_all_for_short_url():
    return [Report(short_url_id=1, visited_at="2024-07-03 11:00:00+00:00", ip_address="0.0.0.0", geolocation=GEOLOCATION_DATA)]

@pytest.fixture
def mock_get_title_tag_from_url():
    return "titleawd"

def test_read_form(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers['content-type']

def test_shorten_url(client, mock_db_session, mock_get_title_tag_from_url):
    salt = "testsalt"
    url = "http://example.com"

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.helpers.get_title_tag_from_url", mock_get_title_tag_from_url)
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        response = client.post("/shorten", data={"url": url, "salt": salt})
        assert response.status_code == 200
        assert 'short_url' in response.json()
        assert 'title' in response.json()
        assert 'target_url' in response.json()
        assert 'short_url_hash' in response.json()
        mock_db_session.add.assert_called()

def test_shorten_url_with_same_salt(client, mock_db_session, mock_get_title_tag_from_url):
    salt = "testsalt"
    url = "http://example.com"

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.helpers.get_title_tag_from_url", mock_get_title_tag_from_url)
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        response1 = client.post("/shorten", data={"url": url, "salt": salt})
        response1_obj = response1.json()
        assert response1.status_code == 200

        response2 = client.post("/shorten", data={"url": url, "salt": salt})
        response2_obj = response2.json()
        assert response2.status_code == 200

        assert response1_obj["short_url_hash"] == response2_obj["short_url_hash"]
        assert response1_obj["short_url"] == response2_obj["short_url"]
        assert response1_obj["target_url"] == response2_obj["target_url"]

def test_shorten_url_with_different_salts(client, mock_db_session, mock_get_title_tag_from_url):
    salt1 = "testsalt1"
    salt2 = "testsalt2"
    url = "http://example.com"

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.helpers.get_title_tag_from_url", mock_get_title_tag_from_url)
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        response1 = client.post("/shorten", data={"url": url, "salt": salt1})
        response1_obj = response1.json()
        assert response1.status_code == 200

        response2 = client.post("/shorten", data={"url": url, "salt": salt2})
        response2_obj = response2.json()
        assert response2.status_code == 200

        assert response1_obj["short_url_hash"] != response2_obj["short_url_hash"]
        assert response1_obj["short_url"] != response2_obj["short_url"]
        assert response1_obj["target_url"] == response2_obj["target_url"]

def test_redirect_to_url(client, mock_db_session, mock_get_geo_from_ip):
    url = "http://example.com"
    short_url = "abc123"

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.helpers.get_geo_from_ip", mock_get_geo_from_ip)
        mock_db_session.query.return_value.filter.return_value.first.return_value = MagicMock(original_url=url)

        response = client.get(f"/{short_url}", follow_redirects=False)
        assert response.status_code == 307  # status code for redirect
        assert response.headers['location'] == url
        mock_db_session.add.assert_called()

def test_redirect_to_url_not_found(client, mock_db_session):
    short_url = "unknown123"
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    response = client.get(f"/{short_url}")
    assert response.status_code == 404
    assert "Short URL does not exist!" in response.text

def test_generate_report(client, mock_db_session):
    short_url = "abc123"

    mock_db_session.query.return_value.filter.return_value.all.return_value = [Report(short_url_id=1, visited_at="2024-07-03 11:00:00+00:00", ip_address="0.0.0.0", geolocation=GEOLOCATION_DATA)]
    response = client.get(f"/report/{short_url}")
    assert response.status_code == 200
    assert "Report" in response.text
    assert GEOLOCATION_DATA["regionName"] in response.text
