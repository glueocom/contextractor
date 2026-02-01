"""Content extraction using trafilatura."""

from __future__ import annotations

import hashlib
import re
from typing import Any

import trafilatura


def extract_metadata(html: str, url: str) -> dict[str, Any]:
    """Extract metadata from HTML using trafilatura.

    Args:
        html: Raw HTML content.
        url: Source URL for context.

    Returns:
        Dictionary with extracted metadata fields.
    """
    metadata_result = trafilatura.bare_extraction(html, url=url, with_metadata=True)
    metadata: dict[str, Any] = {
        'title': None,
        'author': None,
        'publishedAt': None,
        'description': None,
        'siteName': None,
        'lang': None,
    }

    if metadata_result:
        metadata['title'] = getattr(metadata_result, 'title', None)
        metadata['author'] = getattr(metadata_result, 'author', None)
        metadata['publishedAt'] = getattr(metadata_result, 'date', None)
        metadata['description'] = getattr(metadata_result, 'description', None)
        metadata['siteName'] = getattr(metadata_result, 'sitename', None)
        metadata['lang'] = getattr(metadata_result, 'language', None)

    # Fallback: extract lang from <html lang="..."> if not found
    if not metadata['lang']:
        lang_match = re.search(r'<html[^>]*\slang=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if lang_match:
            metadata['lang'] = lang_match.group(1)

    return metadata


def get_extraction_options(url: str, extraction_mode: str) -> dict[str, Any]:
    """Build trafilatura extraction options.

    Args:
        url: Source URL.
        extraction_mode: One of BALANCED, FAVOR_PRECISION, FAVOR_RECALL.

    Returns:
        Options dictionary for trafilatura.extract().
    """
    return {
        'url': url,
        'with_metadata': True,
        'include_tables': True,
        'include_formatting': True,
        'include_links': True,
        'favor_precision': extraction_mode == 'FAVOR_PRECISION',
        'favor_recall': extraction_mode == 'FAVOR_RECALL',
    }


def compute_content_info(content: str | bytes) -> dict[str, Any]:
    """Compute hash and length for content.

    Args:
        content: String or bytes content.

    Returns:
        Dictionary with hash and length.
    """
    if isinstance(content, str):
        content = content.encode('utf-8')
    return {
        'hash': hashlib.md5(content).hexdigest(),
        'length': len(content),
    }


async def save_content_to_kvs(
    kvs: Any,
    key: str,
    content: str,
    content_type: str,
) -> dict[str, Any]:
    """Save content to key-value store and return info dict.

    Args:
        kvs: Key-value store instance.
        key: Storage key.
        content: Content to save.
        content_type: MIME type.

    Returns:
        Dictionary with key, url, hash, and length.
    """
    await kvs.set_value(key, content, content_type=content_type)
    content_bytes = content.encode('utf-8')
    return {
        'key': key,
        'url': await kvs.get_public_url(key),
        'hash': hashlib.md5(content_bytes).hexdigest(),
        'length': len(content_bytes),
    }


def extract_format(
    html: str,
    output_format: str,
    extract_opts: dict[str, Any],
) -> str | None:
    """Extract content in specified format.

    Args:
        html: Raw HTML content.
        output_format: One of txt, json, markdown, xml, xmltei.
        extract_opts: Trafilatura extraction options.

    Returns:
        Extracted content or None if extraction failed.
    """
    return trafilatura.extract(html, output_format=output_format, **extract_opts)
