# Contextractor: Migrate to uv workspace monorepo

Restructure `/Users/miroslavsekera/r/contextractor/` from flat requirements.txt project into a **uv workspace** monorepo with two sub-projects.

## Target Structure

```
/Users/miroslavsekera/r/contextractor/
├── pyproject.toml              # Root workspace config
├── uv.lock                     # Unified lockfile
├── .python-version             # Pin Python 3.12
├── packages/
│   └── contextractor-engine/
│       ├── pyproject.toml      # Library package config
│       ├── src/
│       │   └── contextractor_engine/
│       │       ├── __init__.py
│       │       ├── extractor.py      # Core extraction wrapper
│       │       ├── models.py         # ExtractionConfig + result types
│       │       └── py.typed
│       └── tests/
│           └── test_extractor.py
├── apps/
│   └── contextractor/          # Existing actor (migrated)
│       ├── pyproject.toml      # Actor-specific deps + workspace ref
│       ├── .actor/             # Unchanged
│       ├── Dockerfile          # Updated for uv
│       └── src/                # Refactored to use engine
├── docs/
├── tools/
└── prompts/
```

## Phase 1: Root workspace setup

Create root `pyproject.toml`:

```toml
[project]
name = "contextractor-workspace"
version = "0.1.0"
requires-python = ">=3.12"

[tool.uv.workspace]
members = ["packages/*", "apps/*"]
```

Create `.python-version` with `3.12`.

Run `uv sync` to generate `uv.lock`.

## Phase 2: Engine package — `packages/contextractor-engine/`

### Package config

```toml
[project]
name = "contextractor-engine"
version = "0.1.0"
description = "Trafilatura extraction wrapper with configurable options"
requires-python = ">=3.12"
dependencies = [
    "trafilatura>=2.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/contextractor_engine"]
```

### ExtractionConfig model — `models.py`

Use a **dataclass** (not Pydantic — keep deps minimal for a library). Name: `ExtractionConfig`.

Map all **non-deprecated** `trafilatura.extract()` parameters:

| Field | Type | Default | Trafilatura param |
|-------|------|---------|-------------------|
| `fast` | `bool` | `False` | `fast` |
| `favor_precision` | `bool` | `False` | `favor_precision` |
| `favor_recall` | `bool` | `False` | `favor_recall` |
| `include_comments` | `bool` | `True` | `include_comments` |
| `include_tables` | `bool` | `True` | `include_tables` |
| `include_images` | `bool` | `False` | `include_images` |
| `include_formatting` | `bool` | `True` | `include_formatting` |
| `include_links` | `bool` | `True` | `include_links` |
| `deduplicate` | `bool` | `False` | `deduplicate` |
| `target_language` | `str \| None` | `None` | `target_language` |
| `with_metadata` | `bool` | `True` | `with_metadata` |
| `only_with_metadata` | `bool` | `False` | `only_with_metadata` |
| `tei_validation` | `bool` | `False` | `tei_validation` |
| `prune_xpath` | `str \| list[str] \| None` | `None` | `prune_xpath` |
| `url_blacklist` | `set[str] \| None` | `None` | `url_blacklist` |
| `author_blacklist` | `set[str] \| None` | `None` | `author_blacklist` |
| `date_extraction_params` | `dict[str, Any] \| None` | `None` | `date_extraction_params` |

**Excluded (deprecated):** `no_fallback` (use `fast`), `as_dict` (use `.as_dict()`), `max_tree_size` (use settings.cfg), `settingsfile`, `config`, `options` (internal).

Also exclude from the config: `url` (passed per-call), `record_id` (passed per-call), `output_format` (determined by caller).

Provide **factory methods** for convenience:

```python
@dataclass
class ExtractionConfig:
    # ... fields above ...

    @classmethod
    def balanced(cls) -> "ExtractionConfig":
        """Default balanced extraction."""
        return cls()

    @classmethod
    def precision(cls) -> "ExtractionConfig":
        """High precision, less noise."""
        return cls(favor_precision=True)

    @classmethod
    def recall(cls) -> "ExtractionConfig":
        """High recall, more content."""
        return cls(favor_recall=True)

    def to_trafilatura_kwargs(self) -> dict[str, Any]:
        """Convert to trafilatura.extract() keyword arguments.
        Excludes url, record_id, output_format — those are per-call."""
        return {
            "fast": self.fast,
            "favor_precision": self.favor_precision,
            "favor_recall": self.favor_recall,
            "include_comments": self.include_comments,
            "include_tables": self.include_tables,
            "include_images": self.include_images,
            "include_formatting": self.include_formatting,
            "include_links": self.include_links,
            "deduplicate": self.deduplicate,
            "target_language": self.target_language,
            "with_metadata": self.with_metadata,
            "only_with_metadata": self.only_with_metadata,
            "tei_validation": self.tei_validation,
            "prune_xpath": self.prune_xpath,
            "url_blacklist": self.url_blacklist,
            "author_blacklist": self.author_blacklist,
            "date_extraction_params": self.date_extraction_params,
        }
```

### Result types — also in `models.py`

```python
@dataclass
class ExtractionResult:
    """Result from a single format extraction."""
    content: str
    output_format: str  # "txt", "json", "markdown", "xml", "xmltei", "html", "csv"

@dataclass
class MetadataResult:
    """Extracted metadata from HTML."""
    title: str | None
    author: str | None
    date: str | None
    description: str | None
    sitename: str | None
    language: str | None
```

### Core extractor — `extractor.py`

```python
class ContentExtractor:
    """Trafilatura wrapper with configurable extraction."""

    def __init__(self, config: ExtractionConfig | None = None):
        self.config = config or ExtractionConfig.balanced()

    def extract(
        self,
        html: str,
        url: str | None = None,
        output_format: str = "txt",
    ) -> ExtractionResult | None:
        """Extract content in specified format."""
        kwargs = self.config.to_trafilatura_kwargs()
        result = trafilatura.extract(
            html,
            url=url,
            output_format=output_format,
            **kwargs,
        )
        if result is None:
            return None
        return ExtractionResult(content=result, output_format=output_format)

    def extract_metadata(self, html: str, url: str | None = None) -> MetadataResult:
        """Extract metadata from HTML."""
        raw = trafilatura.bare_extraction(html, url=url, with_metadata=True)
        if not raw:
            return MetadataResult(...)  # all None
        return MetadataResult(
            title=getattr(raw, "title", None),
            author=getattr(raw, "author", None),
            date=getattr(raw, "date", None),
            description=getattr(raw, "description", None),
            sitename=getattr(raw, "sitename", None),
            language=getattr(raw, "language", None),
        )

    def extract_all_formats(
        self,
        html: str,
        url: str | None = None,
        formats: list[str] | None = None,
    ) -> dict[str, ExtractionResult]:
        """Extract content in multiple formats at once.
        Default formats: ["txt", "markdown", "json", "xml"]
        Returns dict keyed by format name."""
        ...
```

### Public API — `__init__.py`

```python
from .extractor import ContentExtractor
from .models import ExtractionConfig, ExtractionResult, MetadataResult

__all__ = [
    "ContentExtractor",
    "ExtractionConfig",
    "ExtractionResult",
    "MetadataResult",
]
```

## Phase 3: Actor migration — `apps/contextractor/`

### Actor package config

```toml
[project]
name = "contextractor"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "apify>=2.0.0,<4.0.0",
    "crawlee[playwright]>=0.4.0",
    "contextractor-engine",
]

[tool.uv.sources]
contextractor-engine = { workspace = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src"]
```

Delete `requirements.txt`.

### Replace `extractionMode` with `extractionConfig`

In `input_schema.json`, replace the `extractionMode` field with:

```json
"extractionConfig": {
    "sectionCaption": "Content extraction",
    "title": "Extraction configuration",
    "type": "object",
    "description": "Trafilatura extraction options. Leave empty for balanced defaults. See trafilatura docs for details.",
    "editor": "json",
    "default": {},
    "prefill": {}
}
```

The `extractionConfig` object is **optional**. When empty `{}` or absent, defaults to `ExtractionConfig.balanced()`.

Supported JSON keys (map 1:1 to `ExtractionConfig` fields):

```json
{
    "fast": false,
    "favor_precision": false,
    "favor_recall": false,
    "include_comments": true,
    "include_tables": true,
    "include_images": false,
    "include_formatting": true,
    "include_links": true,
    "deduplicate": false,
    "target_language": null,
    "with_metadata": true,
    "only_with_metadata": false,
    "tei_validation": false,
    "prune_xpath": null,
    "url_blacklist": null,
    "author_blacklist": null
}
```

### Refactor `src/config.py`

- Remove `extraction_mode` from `build_crawl_config`
- Add `extraction_config` key that passes through the raw dict
- In `build_crawl_config`:

```python
from contextractor_engine import ExtractionConfig

def build_extraction_config(raw: dict[str, Any]) -> ExtractionConfig:
    """Build ExtractionConfig from actor input's extractionConfig field."""
    if not raw:
        return ExtractionConfig.balanced()
    return ExtractionConfig(**{k: v for k, v in raw.items() if v is not None})
```

### Refactor `src/extraction.py`

Replace direct `trafilatura` calls with `ContentExtractor`:

```python
from contextractor_engine import ContentExtractor, ExtractionConfig

# In handler setup:
extractor = ContentExtractor(config=extraction_config)

# In extraction:
result = extractor.extract(html, url=url, output_format="markdown")
metadata = extractor.extract_metadata(html, url=url)
```

Remove `get_extraction_options()` — replaced by `ExtractionConfig.to_trafilatura_kwargs()`.
Remove `extract_format()` — replaced by `ContentExtractor.extract()`.
Keep `save_content_to_kvs()` and `compute_content_info()` in the actor (storage is actor-specific).

### Update Dockerfile for uv

```dockerfile
FROM apify/actor-python-playwright:3.14-1.57.0

USER myuser

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy workspace root files
COPY --chown=myuser:myuser pyproject.toml uv.lock ./

# Copy engine package
COPY --chown=myuser:myuser packages/contextractor-engine/ ./packages/contextractor-engine/

# Copy actor package
COPY --chown=myuser:myuser apps/contextractor/ ./apps/contextractor/

# Install dependencies
RUN uv sync --frozen --no-dev --directory apps/contextractor

# Compile
RUN python3 -m compileall -q apps/contextractor/src/

WORKDIR /home/myuser/apps/contextractor
CMD ["uv", "run", "python3", "-m", "src"]
```

Update `.actor/actor.json` dockerfile path: `"dockerfile": "../../Dockerfile"` — since the Dockerfile now lives at root level to access workspace. Alternatively, keep Dockerfile in `apps/contextractor/` with adjusted COPY paths that reference `../../packages/`. Choose the approach that works best with Apify's build system (which uses the actor directory as build context).

**Important**: Apify builds from the actor's directory as Docker context. If using monorepo source on Apify platform, the Git URL must point to repo root with the actor path specified. The Dockerfile must be relative to the build context. Consider keeping the Dockerfile in the actor directory and using `../../` relative paths, OR set the build context at repo root level.

## Phase 4: Build script for engine package

Add `scripts/build-engine.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Building contextractor-engine..."
uv build --package contextractor-engine --out-dir dist/

echo "Done. Artifacts in dist/"
ls -la dist/
```

This produces standard `.whl` and `.tar.gz` in `dist/` — pip-installable from anywhere:

```bash
pip install dist/contextractor_engine-0.1.0-py3-none-any.whl
```

Make executable: `chmod +x scripts/build-engine.sh`

## Phase 5: Update docs/spec

### `docs/spec/tech-spec.md`

Update to reflect:

- **Stack**: Add uv workspace, hatchling build system
- **Architecture**: Two-package monorepo — engine (library) + actor (app)
- **Dependencies**: Engine depends on trafilatura only; Actor depends on engine + apify + crawlee
- **Build**: `uv build --package contextractor-engine` for distribution
- **ExtractionConfig**: Replaces `extractionMode` enum. Dataclass mapping to trafilatura.extract() params.
- **Docker**: uv-based install with frozen lockfile
- Remove `requirements.txt` references

### `docs/spec/functional-spec.md`

Update to reflect:

- Replace `extractionMode` row with `extractionConfig` (optional JSON object, defaults to balanced)
- Document available config fields with types and defaults
- Note backward compatibility: `{}` or omitted = same as previous `BALANCED` mode
- Mention that `favor_precision: true` = previous `FAVOR_PRECISION`, `favor_recall: true` = previous `FAVOR_RECALL`

## Execution Order

1. Initialize uv workspace at root (`pyproject.toml`, `.python-version`)
2. Create `packages/contextractor-engine/` with package structure
3. Implement `models.py` (ExtractionConfig, ExtractionResult, MetadataResult)
4. Implement `extractor.py` (ContentExtractor)
5. Write basic tests for engine
6. Migrate `apps/contextractor/` to use workspace dependency
7. Refactor actor to use `ContentExtractor` instead of direct trafilatura calls
8. Replace `extractionMode` with `extractionConfig` in input schema
9. Update Dockerfile for uv
10. Create `scripts/build-engine.sh`
11. Run `uv sync` and verify everything resolves
12. Update `docs/spec/tech-spec.md` and `docs/spec/functional-spec.md`
13. Delete `apps/contextractor/requirements.txt`
14. Test: `uv run --directory apps/contextractor python -m src` locally
