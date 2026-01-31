# Contextractor - Technical Specification

## Stack

- Python 3.12+
- Crawlee for Python with PlaywrightCrawler
- Apify SDK
- Trafilatura for content extraction

## Architecture

```
Input URLs → PlaywrightCrawler → Trafilatura → KVS (blobs) + Dataset (metadata)
```

## Key Implementation Details

### Handler Pattern

Handler must be defined inside `async with Actor:` context. Config passed via `Request.user_data`:

```python
async with Actor:
    kvs = await Actor.open_key_value_store(name='content')
    crawler = PlaywrightCrawler(...)

    @crawler.router.default_handler
    async def handler(ctx: PlaywrightCrawlingContext) -> None:
        config = ctx.request.user_data.get('config', {})
        html = await ctx.page.content()
        # extract and save...

    requests = [Request.from_url(url, user_data={'config': config}) for url in start_urls]
    await crawler.run(requests)
```

### Content-Type Headers

All content-type headers must include charset: `text/html; charset=utf-8`

### Public URLs

Use `await kvs.get_public_url(key)` to get download URLs.

### Trafilatura Extraction

```python
trafilatura.extract(html, output_format='markdown', url=url,
    with_metadata=True, include_tables=True,
    favor_precision=(mode == 'FAVOR_PRECISION'),
    favor_recall=(mode == 'FAVOR_RECALL'))
```

Formats: `txt`, `json`, `markdown`, `xml`, `xmltei`

### Key Generation

MD5 hash of URL, first 16 characters: `hashlib.md5(url.encode()).hexdigest()[:16]`

### Browser Context Options

Custom headers and cookies are passed to the PlaywrightCrawler via `browser_new_context_options`:

```python
options = {}
if initial_cookies:
    options['storage_state'] = {'cookies': initial_cookies}
if custom_headers:
    options['extra_http_headers'] = custom_headers
```

This applies headers to all HTTP requests and pre-sets cookies on all browser contexts.

## Dependencies

```
apify>=2.0.0,<4.0.0
crawlee[playwright]>=0.4.0
trafilatura>=2.0.0
```
