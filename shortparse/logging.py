from shortparse.settings import LOGS_DIR
import logging

from pathlib import Path
from logging.handlers import TimedRotatingFileHandler


LOG_DIRECTORY = LOGS_DIR

LOG_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)

LOG_FILE = LOG_DIRECTORY / "shortparse.log"


file_handler = TimedRotatingFileHandler(
    filename=LOG_FILE,
    when="midnight",
    interval=1,
    backupCount=60,
    encoding="utf-8",
)

file_handler.suffix = "%Y-%m-%d"

formatter = logging.Formatter(
    (
        "[%(asctime)s] "
        "[%(levelname)s] "
        "%(name)s: %(message)s"
    )
)

file_handler.setFormatter(formatter)


console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)


logging.basicConfig(
    level=logging.INFO,
    handlers=[
        file_handler,
        console_handler,
    ],
)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)