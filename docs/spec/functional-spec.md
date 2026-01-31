# Contextractor - Functional Specification

## Overview

Contextractor crawls websites and extracts clean, readable content using Trafilatura. Content is stored in Key-Value Store with metadata in Dataset.

## Input

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| startUrls | array | required | URLs to extract content from |
| linkSelector | string | "" | CSS selector for links to enqueue |
| globs | array | [] | Glob patterns to match enqueued links |
| excludes | array | [] | Glob patterns to exclude |
| maxPagesPerCrawl | integer | 0 | Max pages (0 = unlimited) |
| exportHtml | boolean | false | Save raw HTML |
| exportText | boolean | false | Extract plain text |
| exportJson | boolean | false | Extract JSON with metadata |
| exportMarkdown | boolean | true | Extract Markdown |
| exportXml | boolean | false | Extract XML |
| exportXmlTei | boolean | false | Extract XML-TEI scholarly format |
| extractionMode | enum | BALANCED | FAVOR_PRECISION, BALANCED, FAVOR_RECALL |
| includeMetadata | boolean | true | Include title, author, date |
| initialCookies | array | [] | Pre-set cookies for authentication (encrypted) |
| customHttpHeaders | object | {} | Custom HTTP headers for all requests |

## Output

### Dataset Entry

```json
{
  "loadedUrl": "https://example.com/page",
  "rawHtml": {
    "hash": "...",
    "length": 89898,
    "key": "abc123-raw.html",
    "url": "https://api.apify.com/v2/key-value-stores/{id}/records/abc123-raw.html"
  },
  "extractedMarkdown": {
    "key": "abc123.md",
    "url": "...",
    "hash": "...",
    "length": 6887
  },
  "loadedAt": "2026-01-28T18:58:36.534Z",
  "metadata": {
    "title": "Page Title",
    "author": null,
    "publishedAt": "2024-01-15",
    "description": "Meta description",
    "siteName": "Example Site",
    "lang": "en"
  },
  "httpStatus": 200
}
```

**Rules:**
- `rawHtml`: always has `hash` + `length`; adds `key` + `url` only if `exportHtml` enabled
- `extractedMarkdown`, `extractedText`, etc.: entire object only present if that export is enabled
- `metadata`: extracted from trafilatura

### Key-Value Store

Named `content`. Files stored with MD5-based keys:
- `{hash}-raw.html` - Raw HTML
- `{hash}.txt` - Plain text
- `{hash}.json` - JSON with metadata
- `{hash}.md` - Markdown
- `{hash}.xml` - XML
- `{hash}.tei.xml` - XML-TEI
