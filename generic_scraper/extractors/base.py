from abc import ABC, abstractmethod
from typing import Any

from ..schema import Record


class BaseExtractor(ABC):
    """Base class for all extractors. Config is a dict from YAML."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.source_id = str(config.get("id", "unknown"))
        self.base_url = (config.get("base_url") or "").rstrip("/")

    @abstractmethod
    def extract(self) -> list[Record]:
        """Fetch and parse data; return list of Records."""
        pass
