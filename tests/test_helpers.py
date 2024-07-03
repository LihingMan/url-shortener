from app.helpers import generate_short_url

def test_generate_short_url_basic():
    url = "https://www.example.com"
    result = generate_short_url(url)
    assert result is not None, "The result should not be None"
    assert len(result) <= 15, "The short URL should be no longer than 15 characters"
    assert generate_short_url(url) == result, "The short URL should be consistent"

def test_generate_short_url_uniqueness():
    url1 = "https://www.example.com"
    url2 = "https://www.different.com"
    result1 = generate_short_url(url1)
    result2 = generate_short_url(url2)
    assert result1 != result2, "Different URLs should produce different short URLs"

def test_generate_short_url_empty():
    url = ""
    result = generate_short_url(url)
    assert result is not None, "The result should not be None for an empty URL"
    assert len(result) <= 15, "The short URL for an empty URL should be no longer than 15 characters"

def test_generate_short_url_special_characters():
    url = "https://www.example.com/special?query=parameter&strange=✔☺"
    result = generate_short_url(url)
    assert result is not None, "The result should not be None for a URL with special characters"
    assert len(result) <= 15, "The short URL for a URL with special characters should be no longer than 15 characters"

def test_generate_short_url_long_url():
    url = "https://" + "a" * 1000 + ".com"
    result = generate_short_url(url)
    assert result is not None, "The result should not be None for a long URL"
    assert len(result) <= 15, "The short URL for a long URL should be no longer than 15 characters"
