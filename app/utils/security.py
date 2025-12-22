import hashlib
from passlib.context import CryptContext

# Use sha256_crypt as the primary scheme to avoid bcrypt's backend self-check
# issues and 72-byte limit. Keep bcrypt_sha256 and bcrypt for legacy hashes.
pwd_context = CryptContext(
    schemes=["sha256_crypt", "bcrypt_sha256", "bcrypt"],
    default="sha256_crypt",
    deprecated="auto",
)


def _normalize_secret(secret: str) -> str:
    """
    Normalize secrets to a reasonable length; if very long, pre-hash to hex.
    """
    if secret is None:
        secret = ""
    secret = str(secret)
    if len(secret.encode("utf-8")) > 256:
        secret = hashlib.sha256(secret.encode("utf-8")).hexdigest()
    return secret


def hash_password(password: str) -> str:
    """
    Hash a plaintext password (sha256_crypt by default).
    """
    normalized = _normalize_secret(password)
    return pwd_context.hash(normalized)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against stored hash (supports sha256_crypt,
    bcrypt_sha256, and bcrypt).
    """
    if not hashed_password:
        return False
    normalized = _normalize_secret(plain_password)
    return pwd_context.verify(normalized, hashed_password)


