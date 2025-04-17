from __future__ import annotations
import time
from typing import Final

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import LOGGER, REQUEST_DELAY, POOL_SIZE

_MAX_RETRIES: Final[int] = 3
_BACKOFF_FACTOR: Final[float] = 0.5


def _build_session() -> requests.Session:
    retries = Retry(
        total=_MAX_RETRIES,
        backoff_factor=_BACKOFF_FACTOR,
        allowed_methods=["GET"],
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(
        max_retries=retries,
        pool_connections=POOL_SIZE,
        pool_maxsize=POOL_SIZE,
    )
    sess = requests.Session()
    sess.mount("https://", adapter)
    return sess


_SESSION: Final[requests.Session] = _build_session()


def get_html(url: str) -> str:
    """Fetch *url* and return HTML text."""
    LOGGER.debug("GET %s", url)
    r = _SESSION.get(url, timeout=10)
    r.raise_for_status()
    time.sleep(REQUEST_DELAY)
    return r.text
