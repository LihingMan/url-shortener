from bs4 import BeautifulSoup
from fastapi import Request
import hashlib
import logging
import base62
import httpx


IP_API = "http://ip-api.com/json/"

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

def generate_short_url(url: str) -> str:
    # Generate SHA-256 hash of the URL
    sha256_hash = hashlib.sha256(url.encode()).digest()

    # Truncate the hash to the first 8 bytes for a short representation
    truncated_hash = sha256_hash[:8]

    # Encode using base62
    short_url = base62.encodebytes(truncated_hash)

    return short_url[:15]  # Ensure the length is within 15 characters

def get_client_ip(request: Request):
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.client.host

async def get_geo_from_ip(ip_address: str):
    ip_api_url = f"{IP_API}/{ip_address}"
    async with httpx.AsyncClient() as client:
        response = await client.get(ip_api_url)
        response.raise_for_status()

    return response.json()

# TODO test
async def get_title_tag_from_url(url: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('title')

        if title_tag is None:
            return "-"

        return title_tag.string

    except Exception as e:
        log.error(f"unexpected error when parsing for title: {str(e)}")
        return "-"
