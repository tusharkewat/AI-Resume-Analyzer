from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

# Configure Argon2 password hasher
password_hash = PasswordHash((Argon2Hasher(),))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against its hashed representation."""
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hashes a password using Argon2."""
    return password_hash.hash(password)
