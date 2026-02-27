from .base import BaseExtractor
from .html_listing import HtmlListingExtractor
from .json_api import JsonApiExtractor
from .html_attrs import HtmlAttrsExtractor
from .css_select import CssSelectExtractor

EXTRACTOR_REGISTRY = {
    "html_listing": HtmlListingExtractor,
    "json_api": JsonApiExtractor,
    "html_attrs": HtmlAttrsExtractor,
    "css_select": CssSelectExtractor,
}


def get_extractor(source_type: str) -> type[BaseExtractor]:
    t = source_type.strip().lower()
    if t not in EXTRACTOR_REGISTRY:
        raise ValueError(f"Unknown source_type: {source_type}. Known: {list(EXTRACTOR_REGISTRY)}")
    return EXTRACTOR_REGISTRY[t]
