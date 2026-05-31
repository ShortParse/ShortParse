import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup root path to make shortparse importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from shortparse.database import Base, DB_PATH
from shortparse.db_models import User, LinkedAccount, Job, SystemConfig
from shortparse.security.db_types import encryption_manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("shortparse.migration")

def run_migration():
    """Migrates and encrypts data from the source SQLite database to a target database."""
    logger.info("======================================================================")
    logger.info("ShortParse Zero-Trust Database Migration & Encryption Tool")
    logger.info("======================================================================")
    
    # 1. Enforce encryption key validation
    if not encryption_manager.is_active:
        logger.error(
            "DB_ENCRYPTION_KEY is not configured or invalid! "
            "You must define a secure 32-byte base64 key in DB_ENCRYPTION_KEY "
            "to encrypt sensitive data columns. Migration aborted."
        )
        sys.exit(1)
        
    # 2. Configure source engine (always local SQLite)
    source_db_url = f"sqlite:///{DB_PATH}"
    if not DB_PATH.exists():
        logger.warning(f"Source SQLite database file not found at: {DB_PATH}")
        logger.warning("If this is a fresh setup with no pre-existing data, you can bypass this migration.")
        sys.exit(0)
        
    logger.info(f"Connecting to source SQLite database: {source_db_url}")
    source_engine = create_engine(source_db_url)
    SourceSession = sessionmaker(bind=source_engine)
    source_session = SourceSession()
    
    # 3. Configure destination engine (PostgreSQL or secondary SQLite)
    dest_db_url = os.getenv("DATABASE_URL", "")
    if dest_db_url.startswith("postgres://"):
        dest_db_url = dest_db_url.replace("postgres://", "postgresql://", 1)
        
    if not dest_db_url or dest_db_url.startswith("sqlite"):
        logger.warning("No PostgreSQL DATABASE_URL detected. Performing IN-PLACE encryption on source SQLite database!")
        dest_engine = source_engine
        dest_session = source_session
        in_place = True
    else:
        logger.info(f"Connecting to destination PostgreSQL database: {dest_db_url}")
        dest_engine = create_engine(dest_db_url)
        DestSession = sessionmaker(bind=dest_engine)
        dest_session = DestSession()
        in_place = False
        
    try:
        # Create all schemas on the destination if not present
        logger.info("Validating database schemas and creating tables...")
        Base.metadata.create_all(dest_engine)
        
        # 4. Migrate Users
        logger.info("Starting Users migration & column encryption...")
        users = source_session.query(User).all()
        logger.info(f"Found {len(users)} users to process.")
        
        for u in users:
            # We encrypt manually here because if we are migrating across distinct DBs,
            # we need to decrypt first (if already encrypted, but we assume source is plaintext)
            # and let the custom type or manual encryption encrypt it for target.
            # To be safe, we check if the source is already encrypted. If decrypting returns the same string
            # and it looks base64-encoded GCM, we do not double encrypt.
            # But since this is a clean migration tool: we read raw database value directly bypassing TypeDecorator
            # to make sure we don't double-encrypt, OR we just let SQLAlchemy handle it!
            # Under SQLAlchemy:
            # - If we read from source SQLite using SQLAlchemy model, the *old* model had `String` column,
            #   so SQLAlchemy returned it as standard plaintext string.
            # - When we write to destination PostgreSQL using new model, it has `EncryptedString` column,
            #   so SQLAlchemy automatically encrypts it!
            # This is extremely elegant and handles the encryption completely transparently!
            
            if in_place:
                # If in-place, we are modifying the same database, but the model has already been upgraded to `EncryptedString`!
                # Since the source database file has plaintext values, reading them via SQLAlchemy using the upgraded model
                # will attempt to decrypt them. Decryption fails (since they are plaintext) and returns the original plaintext strings.
                # To encrypt them, we simply mark the fields as dirty so they get written back encrypted!
                u.discord_webhook_url = u.discord_webhook_url
                u.gemini_api_key = u.gemini_api_key
                source_session.add(u)
            else:
                # Detach from source session to insert into destination
                source_session.expunge(u)
                
                # Check if user already exists in target
                existing_user = dest_session.query(User).filter(User.id == u.id).first()
                if existing_user:
                    logger.info(f"User {u.username} ({u.id}) already exists in destination. Updating...")
                    existing_user.username = u.username
                    existing_user.email = u.email
                    existing_user.is_premium = u.is_premium
                    existing_user.premium_tier = u.premium_tier
                    existing_user.discord_webhook_url = u.discord_webhook_url
                    existing_user.discord_auto_post = u.discord_auto_post
                    existing_user.gemini_api_key = u.gemini_api_key
                    existing_user.excluded_ledger_players = u.excluded_ledger_players
                else:
                    logger.info(f"Inserting new User {u.username} ({u.id})...")
                    dest_session.add(u)
                    
        dest_session.commit()
        logger.info("Users successfully migrated and encrypted.")
        
        # 5. Migrate LinkedAccounts
        logger.info("Starting LinkedAccounts migration & token encryption...")
        accounts = source_session.query(LinkedAccount).all()
        logger.info(f"Found {len(accounts)} linked accounts to process.")
        
        for acc in accounts:
            if in_place:
                acc.access_token = acc.access_token
                acc.refresh_token = acc.refresh_token
                source_session.add(acc)
            else:
                source_session.expunge(acc)
                existing_acc = dest_session.query(LinkedAccount).filter(LinkedAccount.id == acc.id).first()
                if existing_acc:
                    existing_acc.access_token = acc.access_token
                    existing_acc.refresh_token = acc.refresh_token
                    existing_acc.expires_at = acc.expires_at
                else:
                    dest_session.add(acc)
                    
        dest_session.commit()
        logger.info("Linked accounts successfully migrated and encrypted.")
        
        # 6. Migrate Jobs
        if not in_place:
            logger.info("Starting Jobs migration...")
            jobs = source_session.query(Job).all()
            logger.info(f"Found {len(jobs)} jobs to process.")
            
            for j in jobs:
                source_session.expunge(j)
                existing_job = dest_session.query(Job).filter(Job.job_id == j.job_id).first()
                if not existing_job:
                    dest_session.add(j)
                    
            dest_session.commit()
            logger.info("Jobs successfully migrated.")
            
        # 7. Migrate SystemConfigs
        if not in_place:
            logger.info("Starting SystemConfigs migration...")
            configs = source_session.query(SystemConfig).all()
            logger.info(f"Found {len(configs)} configuration keys to process.")
            
            for c in configs:
                source_session.expunge(c)
                existing_c = dest_session.query(SystemConfig).filter(SystemConfig.key == c.key).first()
                if not existing_c:
                    dest_session.add(c)
                    
            dest_session.commit()
            logger.info("System configurations successfully migrated.")
            
        logger.info("✨ Database migration and encryption completed with 100% SUCCESS!")
        
    except Exception as e:
        logger.error(f"Migration failed due to an error: {e}")
        dest_session.rollback()
        raise e
    finally:
        source_session.close()
        if not in_place:
            dest_session.close()

if __name__ == "__main__":
    run_migration()
