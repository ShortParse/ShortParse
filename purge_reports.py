import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from shortparse.database import SessionLocal
from shortparse.db_models import Job
from shortparse.settings import REPORTS_DIR
from shortparse.cache import REPORT_CACHE_ROOT, HAS_REDIS, redis_client

print("[*] Starting ShortParse Report Purge...")

# 1. Clear Database
db = SessionLocal()
try:
    deleted_jobs = db.query(Job).delete()
    db.commit()
    print(f"[OK] Deleted {deleted_jobs} job records from the database.")
except Exception as e:
    db.rollback()
    print(f"[ERROR] Failed to delete database jobs: {e}")
finally:
    db.close()

# 2. Clear Reports Directory
reports_deleted = 0
if REPORTS_DIR.exists():
    for item in REPORTS_DIR.iterdir():
        try:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
            reports_deleted += 1
        except Exception as e:
            print(f"[ERROR] Failed to delete report item {item}: {e}")
    print(f"[OK] Cleared {reports_deleted} items from reports directory ({REPORTS_DIR}).")
else:
    print(f"[*] Reports directory ({REPORTS_DIR}) does not exist.")

# 3. Clear Cache Directory
cache_deleted = 0
if REPORT_CACHE_ROOT.exists():
    for item in REPORT_CACHE_ROOT.iterdir():
        try:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
            cache_deleted += 1
        except Exception as e:
            print(f"[ERROR] Failed to delete cache item {item}: {e}")
    print(f"[OK] Cleared {cache_deleted} items from cache directory ({REPORT_CACHE_ROOT}).")
else:
    print(f"[*] Cache directory ({REPORT_CACHE_ROOT}) does not exist.")

# 4. Clear Redis Cache
if HAS_REDIS and redis_client:
    try:
        keys = redis_client.keys("shortparse:*")
        if keys:
            redis_client.delete(*keys)
            print(f"[OK] Cleared {len(keys)} keys from Redis cache.")
        else:
            print("[*] No Redis keys to clear.")
    except Exception as e:
        print(f"[ERROR] Failed to clear Redis keys: {e}")
else:
    print("[*] Redis not connected/active.")

print("[OK] Purge completed successfully!")
