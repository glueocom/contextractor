"""Data models for contextractor-engine."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TrafilaturaConfig:
    """Configuration for trafilatura extraction.

    Maps all non-deprecated trafilatura.extract() parameters.
    Excluded (deprecated): no_fallback, as_dict, max_tree_size, settingsfile, config, options.
    Excluded (per-call): url, record_id, output_format.
    """

    fast: bool = False
    favor_precision: bool = False
    favor_recall: bool = False
    include_comments: bool = True
    include_tables: bool = True
    include_images: bool = False
    include_formatting: bool = True
    include_links: bool = True
    deduplicate: bool = False
    target_language: str | None = None
    with_metadata: bool = True
    only_with_metadata: bool = False
    tei_validation: bool = False
    prune_xpath: str | list[str] | None = None
    url_blacklist: set[str] | None = field(default=None)
    author_blacklist: set[str] | None = field(default=None)
    date_extraction_params: dict[str, Any] | None = None

    @classmethod
    def balanced(cls) -> "TrafilaturaConfig":
        """Default balanced extraction."""
        return cls()

    @classmethod
    def precision(cls) -> "TrafilaturaConfig":
        """High precision, less noise."""
        return cls(favor_precision=True)

    @classmethod
    def recall(cls) -> "TrafilaturaConfig":
        """High recall, more content."""
        return cls(favor_recall=True)

    def to_trafilatura_kwargs(self) -> dict[str, Any]:
        """Convert to trafilatura.extract() keyword arguments.

        Excludes url, record_id, output_format — those are per-call.
        Only includes optional params if they are set (not None).
        """
        kwargs: dict[str, Any] = {
            "fast": self.fast,
            "favor_precision": self.favor_precision,
            "favor_recall": self.favor_recall,
            "include_comments": self.include_comments,
            "include_tables": self.include_tables,
            "include_images": self.include_images,
            "include_formatting": self.include_formatting,
            "include_links": self.include_links,
            "deduplicate": self.deduplicate,
            "with_metadata": self.with_metadata,
            "only_with_metadata": self.only_with_metadata,
            "tei_validation": self.tei_validation,
        }
        # Only include optional params if set
        if self.target_language is not None:
            kwargs["target_language"] = self.target_language
        if self.prune_xpath is not None:
            kwargs["prune_xpath"] = self.prune_xpath
        if self.url_blacklist is not None:
            kwargs["url_blacklist"] = self.url_blacklist
        if self.author_blacklist is not None:
            kwargs["author_blacklist"] = self.author_blacklist
        if self.date_extraction_params is not None:
            kwargs["date_extraction_params"] = self.date_extraction_params
        return kwargs

    def to_json_dict(self) -> dict[str, Any]:
        """Convert config to JSON-serializable dict with camelCase keys.

        Used for API responses and GUI defaults.
        Excludes None values and non-serializable types (sets converted to lists).
        """
        result: dict[str, Any] = {
            "fast": self.fast,
            "favorPrecision": self.favor_precision,
            "favorRecall": self.favor_recall,
            "includeComments": self.include_comments,
            "includeTables": self.include_tables,
            "includeImages": self.include_images,
            "includeFormatting": self.include_formatting,
            "includeLinks": self.include_links,
            "deduplicate": self.deduplicate,
            "withMetadata": self.with_metadata,
            "onlyWithMetadata": self.only_with_metadata,
            "teiValidation": self.tei_validation,
        }
        # Include optional fields only if set
        if self.target_language is not None:
            result["targetLanguage"] = self.target_language
        if self.prune_xpath is not None:
            result["pruneXpath"] = self.prune_xpath
        if self.url_blacklist is not None:
            result["urlBlacklist"] = list(self.url_blacklist)
        if self.author_blacklist is not None:
            result["authorBlacklist"] = list(self.author_blacklist)
        if self.date_extraction_params is not None:
            result["dateExtractionParams"] = self.date_extraction_params
        return result

    @classmethod
    def get_default_json(cls) -> dict[str, Any]:
        """Get default config as JSON-serializable dict with camelCase keys."""
        return cls().to_json_dict()


@dataclass
class ExtractionResult:
    """Result from a single format extraction."""

    content: str
    output_format: str  # "txt", "json", "markdown", "xml", "xmltei"


@dataclass
class MetadataResult:
    """Extracted metadata from HTML."""

    title: str | None = None
    author: str | None = None
    date: str | None = None
    description: str | None = None
    sitename: str | None = None
    language: str | None = None
