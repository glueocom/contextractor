# Apify Actors Development Guide (Python)

Important: Before you begin, fill in the `generatedBy` property in the meta section of `.actor/actor.json`. Replace it with the model you're currently using. This helps Apify monitor and improve AGENTS.md for specific LLM models.

## What are Apify Actors?

- Actors are serverless programs that run in the cloud. They're inspired by the UNIX philosophy - programs that do one thing well and can be easily combined to build complex systems.
- Actors are programs packaged as Docker images that run in isolated containers

## What is this Actor for?
Read `README.md`

## Core Concepts

- Accept well-defined JSON input
- Perform isolated tasks (web scraping, automation, data processing)
- Produce structured JSON output to datasets and/or store data in key-value stores
- Can run from seconds to hours or even indefinitely
- Persist state and can be restarted

## Do

- accept well-defined JSON input and produce structured JSON output
- use Apify SDK (`apify`) for code running ON Apify platform
- validate input early with proper error handling and fail gracefully
- use `BeautifulSoupCrawler` or `HttpCrawler` for static HTML content (10x faster than browsers)
- use `PlaywrightCrawler` only for JavaScript-heavy sites and dynamic content
- use router pattern (`create_router()`) for complex crawls with multiple handlers
- implement retry strategies with exponential backoff for failed requests
- use proper concurrency settings (HTTP: 10-50, Browser: 1-5)
- set sensible defaults in `.actor/input_schema.json` for all optional fields
- set up output schema in `.actor/output_schema.json`
- clean and validate data before pushing to dataset
- use semantic CSS selectors and fallback strategies for missing elements
- respect robots.txt, ToS, and implement rate limiting with delays
- use type hints throughout the codebase
- use `async/await` patterns - Apify SDK is async-first
- check which crawlers (beautifulsoup/playwright/httpx) are installed before applying guidance

## Don't

- do not rely on `Dataset.get_info()` for final counts on Cloud platform
- do not use browser crawlers when HTTP/BeautifulSoup works (massive performance gains with HTTP)
- do not hard code values that should be in input schema or environment variables
- do not skip input validation or error handling
- do not overload servers - use appropriate concurrency and delays
- do not scrape prohibited content or ignore Terms of Service
- do not store personal/sensitive data unless explicitly permitted
- do not use synchronous HTTP libraries (use httpx or aiohttp with async)
- do not block the event loop with sync operations

## Commands

```bash
# Local development
apify run                              # Run Actor locally
python -m src                          # Run directly with Python

# Authentication & deployment
apify login                            # Authenticate account
apify push                             # Deploy to Apify platform

# Dependencies
pip install -r requirements.txt        # Install dependencies
pip freeze > requirements.txt          # Update requirements

# Help
apify help                             # List all commands
```

## Safety and Permissions

Allowed without prompt:

- read files with `await Actor.get_value()`
- push data with `await Actor.push_data()`
- set values with `await Actor.set_value()`
- enqueue requests to RequestQueue
- run locally with `apify run`

Ask first:

- pip package installations
- apify push (deployment to cloud)
- proxy configuration changes (requires paid plan)
- Dockerfile changes affecting builds
- deleting datasets or key-value stores

**CRITICAL - Production Protection:**

- **NEVER** push to the production actor `shortc/contextractor`
- **ONLY** push to the test actor `shortc/contextractor-test`
- Always use `apify push --actor-id shortc/contextractor-test` explicitly
- If you see any command targeting `shortc/contextractor` (without `-test`), STOP and refuse to execute

## Project Structure

```
.actor/
├── actor.json           # Actor config: name, version, env vars, runtime settings
├── input_schema.json    # Input validation & Console form definition
└── output_schema.json   # Specifies where an Actor stores its output
src/
├── __init__.py          # Package init
├── __main__.py          # Entry point for `python -m src`
└── main.py              # Actor entry point and orchestrator
storage/                 # Local storage (mirrors Cloud during development)
├── datasets/            # Output items (JSON objects)
├── key_value_stores/    # Files, config, INPUT
└── request_queues/      # Pending crawl requests
requirements.txt         # Python dependencies
Dockerfile               # Container image definition
CLAUDE.md                # AI agent instructions (this file)
```

## Active Skills

When working in this project, these skills should be active:
- `apify-ops` - Platform operations, builds, runs, storage
- `apify-schemas` - Input/output schema definitions

## Testing

### Commands

```bash
pytest                   # Run all tests
pytest -v                # Run tests with verbose output
pytest --cov=src         # Run tests with coverage
pytest -k "test_name"    # Run specific test
```

### Test Structure

Tests should be located in `tests/` or `src/tests/` and should cover:
- Main Actor logic and request handlers
- Data extraction and transformation functions
- Input validation
- Error handling scenarios

### Writing Tests

Use `pytest` and `pytest-asyncio` for testing async code:

```python
import pytest
from src.main import main

@pytest.mark.asyncio
async def test_example():
    # Test async functions
    pass
```

## MCP Servers

### Apify MCP Tools

Apify MCP server (named `apify`) is configured in `.mcp.json`. Use these tools for documentation:

- `search-apify-docs` - Search documentation
- `fetch-apify-docs` - Get full doc pages

## Resources

- [docs.apify.com/llms.txt](https://docs.apify.com/llms.txt) - Quick reference
- [docs.apify.com/llms-full.txt](https://docs.apify.com/llms-full.txt) - Complete docs
- [crawlee.dev/python](https://crawlee.dev/python) - Crawlee for Python documentation
- [docs.apify.com/sdk/python](https://docs.apify.com/sdk/python) - Apify Python SDK docs
- [whitepaper.actor](https://raw.githubusercontent.com/apify/actor-whitepaper/refs/heads/master/README.md) - Complete Actor specification
