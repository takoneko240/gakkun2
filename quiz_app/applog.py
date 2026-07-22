import logging
from logging.handlers import RotatingFileHandler

from . import config

LOG_PATH = config.resolve_path("gakkun2.log")

logger = logging.getLogger("gakkun2")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = RotatingFileHandler(LOG_PATH, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
