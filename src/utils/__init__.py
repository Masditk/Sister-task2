from typing import Optional
import logging
from importlib import metadata

try:
    VERSION = metadata.version(__name__)
except metadata.PackageNotFoundError:
    VERSION = "0.0.0"

__all__ = ["VERSION", "get_logger", "setup_logging"]


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name or __package__ or __name__)


def setup_logging(level: int = logging.INFO, fmt: Optional[str] = None) -> None:
    root = logging.getLogger()
    if not root.handlers:
        fmt = fmt or "%(asctime)s %(levelname)s %(name)s: %(message)s"
        logging.basicConfig(level=level, format=fmt)
    else:
        logging.getLogger(__package__ or __name__).setLevel(level)