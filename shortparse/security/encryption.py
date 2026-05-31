import base64
import os
import logging
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger("shortparse.security")

def generate_key() -> str:
    """Generates a secure 32-byte base64-encoded key."""
    return base64.b64encode(AESGCM.generate_key(bit_length=256)).decode('utf-8')

class EncryptionManager:
    def __init__(self, key_str: str):
        self.is_active = False
        self.aesgcm = None
        
        if not key_str:
            logger.warning(
                "DB_ENCRYPTION_KEY is empty/missing. Column encryption is inactive. "
                "Values will be stored in transparent PLAINTEXT. Do not use in production!"
            )
            return

        try:
            self.key = base64.b64decode(key_str.encode('utf-8'))
            if len(self.key) != 32:
                logger.error(
                    f"DB_ENCRYPTION_KEY must decode to exactly 32 bytes (got {len(self.key)} bytes). "
                    "Column encryption is inactive!"
                )
                return
            
            self.aesgcm = AESGCM(self.key)
            self.is_active = True
        except Exception as e:
            logger.error(f"Failed to initialize EncryptionManager from DB_ENCRYPTION_KEY: {e}")

    def encrypt(self, plaintext: str) -> str:
        """Encrypts plaintext string using AES-256-GCM. Returns base64 encoded string."""
        if not self.is_active or not plaintext:
            return plaintext
        
        try:
            nonce = os.urandom(12)
            ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
            combined = nonce + ciphertext
            return base64.b64encode(combined).decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return plaintext

    def decrypt(self, ciphertext_str: str) -> str:
        """Decrypts a base64 encoded GCM ciphertext string. Returns raw plaintext string."""
        if not self.is_active or not ciphertext_str:
            return ciphertext_str
        
        try:
            # Attempt to decode base64
            combined = base64.b64decode(ciphertext_str.encode('utf-8'))
            if len(combined) < 13: # 12 bytes nonce + at least 1 byte ciphertext
                return ciphertext_str # Too short, likely plaintext
            
            nonce = combined[:12]
            ciphertext = combined[12:]
            decrypted = self.aesgcm.decrypt(nonce, ciphertext, None)
            return decrypted.decode('utf-8')
        except Exception:
            # Fall back to raw string (in case the database has old plaintext columns or is corrupted)
            return ciphertext_str
