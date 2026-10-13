import http.client

# Qobuz/CDN responses can exceed Python's default 100-header limit.
http.client._MAXHEADERS = max(http.client._MAXHEADERS, 1000)

from . import converter, db, exceptions, media, metadata
from .config import Config

__all__ = ["Config", "converter", "db", "exceptions", "media", "metadata"]
__version__ = "2.2.0"
