import hashlib
import base62

def generate_short_url(url: str) -> str:
    # Generate SHA-256 hash of the URL
    sha256_hash = hashlib.sha256(url.encode()).digest()

    # Truncate the hash to the first 8 bytes for a short representation
    truncated_hash = sha256_hash[:8]

    # Encode using base62
    short_url = base62.encodebytes(truncated_hash)

    return short_url[:15]  # Ensure the length is within 15 characters
