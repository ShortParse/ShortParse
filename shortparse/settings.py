import os
from pathlib import Path


#
# Base paths
#

BASE_DIR = Path(__file__).resolve().parent.parent

STORAGE_DIR = Path(
    os.getenv(
        "SHORTPARSE_STORAGE_DIR",
        BASE_DIR / "storage",
    )
)

REPORTS_DIR = STORAGE_DIR / "reports"

LOGS_DIR = STORAGE_DIR / "logs"


#
# Environment
#

ENVIRONMENT = os.getenv(
    "SHORTPARSE_ENV",
    "development",
)

DEBUG = (
    os.getenv(
        "SHORTPARSE_DEBUG",
        "true",
    ).lower()
    == "true"
)


#
# Warcraft Logs API
#

WCL_CLIENT_ID = os.getenv(
    "WARCRAFTLOGS_CLIENT_ID",
    "",
)

WCL_CLIENT_SECRET = os.getenv(
    "WARCRAFTLOGS_CLIENT_SECRET",
    "",
)


#
# Redis Cache
#

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")


#
# Application
#

APP_NAME = "ShortParse"
APP_VERSION = "0.1.0"


def has_warcraftlogs_credentials() -> bool:
    return bool(
        WCL_CLIENT_ID
        and WCL_CLIENT_SECRET
    )