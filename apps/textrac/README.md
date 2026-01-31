# Contextractor

Extract clean, readable content from any website. Uses [Trafilatura](https://trafilatura.readthedocs.io/) under the hood to strip away navigation, ads, and boilerplate - leaving just the actual content.

## What it does

- Outputs **Markdown**, plain text, JSON, XML, or XML-TEI (for academic use)
- Handles JavaScript-heavy sites via Playwright
- Follows links across a site with glob pattern filtering
- Pulls out metadata: title, author, date, description, language

## Output

For each URL, you get:
- The extracted content in your chosen format(s)
- Metadata (title, author, publication date, etc.)
- HTTP status and processing timestamp
- Raw HTML if you need it
