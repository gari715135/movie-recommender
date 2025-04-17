from __future__ import annotations
import logging

DOMAIN = "https://letterboxd.com"
REQUEST_DELAY = 0.25
MAX_WORKERS = 100
POOL_SIZE = 100

# basic logging config used by every module
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)
LOGGER = logging.getLogger("lbxd")
