from sqlalchemy.types import TypeDecorator, String
from shortparse.security.encryption import EncryptionManager
from shortparse.settings import DB_ENCRYPTION_KEY

# Initialize encryption manager globally with key from app settings
encryption_manager = EncryptionManager(DB_ENCRYPTION_KEY)

class EncryptedString(TypeDecorator):
    """SQLAlchemy custom type that transparently encrypts strings on save,
    and decrypts them on load using AES-256-GCM.
    """
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return encryption_manager.encrypt(str(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return encryption_manager.decrypt(str(value))
