"""
Credential Encryption Utilities
Fernet symmetric encryption for platform credentials.
"""

from cryptography.fernet import Fernet
import base64
import hashlib
import structlog

logger = structlog.get_logger(__name__)

# Cached cipher instance
_cipher = None


def _get_cipher() -> Fernet:
    """Get or create the Fernet cipher using the app's SECRET_KEY."""
    global _cipher
    if _cipher is None:
        from app.core.config import settings
        # Derive a 32-byte key from SECRET_KEY using SHA256
        key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(key)
        _cipher = Fernet(fernet_key)
    return _cipher


def encrypt_credential(plaintext: str) -> str:
    """Encrypt a credential string (e.g., password) using Fernet."""
    if not plaintext:
        return ""
    cipher = _get_cipher()
    return cipher.encrypt(plaintext.encode()).decode()


def decrypt_credential(ciphertext: str) -> str:
    """Decrypt a credential string back to plaintext."""
    if not ciphertext:
        return ""
    try:
        cipher = _get_cipher()
        return cipher.decrypt(ciphertext.encode()).decode()
    except Exception as e:
        logger.error("credential_decryption_failed", error=str(e))
        raise ValueError("Failed to decrypt credential. Key may have changed.")
