# webfetcher

## Features
- `webfetcher` retrieves web pages from provided URLs and extracts text data.
- Extracted text can be returned or saved in requested formats such as JSON or Markdown.

## System Architecture
- Chromium-compatible CDP endpoint (for example, Lightpanda)
- trafilatura: https://github.com/adbar/trafilatura
- fastapi

This project provides a FastAPI-based web fetching service. It retrieves web pages using `httpx` or a Chromium-compatible CDP renderer and extracts text content using `trafilatura`.
Web pages rendered with JavaScript are fetched through the Chromium DevTools Protocol.

## API

### POST /fetch
Request body:
- `URL`: an array of web page URLs to fetch
- `output_format`: output format for extracted text data (`json`, `markdown`, etc.)
- `with_metadata`: include metadata or not (`true`, `false`)
- `method`: fetch method (`httpx`, `cdp`, etc.)
- `include_comments`: include comments or not (`true`, `false`)
- `include_tables`: include tables or not (`true`, `false`)
- `include_formatting`: keep formatting-related structural elements (`<b>/<strong>`, `<i>/<emph>`, etc.) (`false`, `true`)
- `include_links`: keep links (`<a href="...">...</a>`) (`false`, `true`)
- `include_images`: keep images (`<img src="...">`) (`false`, `true`)
- `favor_precision`: increase precision-oriented extraction (`false`, `true`)
- `favor_recall`: increase recall-oriented extraction (`false`,`true`)

Example `curl` request:

```bash
curl -X POST http://localhost:8000/fetch \
  -H "Content-Type: application/json" \
   -d '{"URL": ["https://example.com"], "output_format": "markdown", "method": "cdp", "with_metadata": true, "favor_precision": false, "favor_recall": false}'
```

## Usage
1. Install dependencies listed in `pyproject.toml`.
   ```bash
   uv sync
   ```
2. Run the FastAPI app with `uvicorn`.
   ```bash
   uv run uvicorn app:app --host 0.0.0.0 --port 8000
   ```
3. Send a POST request to `/fetch` with the desired parameters.

## Docker Compose
This repository includes `docker-compose.yml` to run the service in separate containers.

`webfetcher` is the FastAPI service for fetching and extracting text. The renderer service is any Chromium-compatible CDP endpoint; the sample Docker Compose setup uses the official Lightpanda image as an example. `webfetcher` calls this endpoint when `method` is set to `cdp`.

To start both services with published GHCR images:

```bash
set WEBFETCHER_TAG=0.2.0
set LIGHTPANDA_TAG=0.2.0
docker compose up -d
```

Environment variables are centralized in `.env` and loaded by Compose.
Start from `.env.example` and copy it to `.env` before running Compose.

Current `.env` keys:
- `CHROME_CDP_URL`: CDP endpoint URL (default: `http://lightpanda:9222`)
- `SSL_CERT_FILE`: custom CA certificate path (`/app/certs/custom.crt`)
- `WEBFETCHER_LOG_LEVEL`: log level for `webfetcher` (for example `info`, `debug`)
- `LIGHTPANDA_ADVERTISE_HOST`: advertised CDP host name for lightpanda (default: `lightpanda`)
- `LIGHTPANDA_LOG_LEVEL`: log level for `lightpanda`

The `webfetcher` API is available on port `8000`.

To stop the services:

```bash
docker compose down
```

## Official Chromium-compatible Container Example
This service can use any Chromium-compatible CDP endpoint.

For a sample renderer, run the official Lightpanda image:

```bash
docker run -d --name lightpanda -p 127.0.0.1:9222:9222 lightpanda/browser:nightly
```

Then configure `webfetcher` with:

```bash
export CHROME_CDP_URL=http://127.0.0.1:9222
```

In `docker-compose.yml`, the sample renderer service is named `lightpanda` and exposes CDP on port `9222` inside the compose network.

## Local Development
Run only the webfetcher service locally:

```bash
uv run app:app --host 0.0.0.0 --port 8000
```

## Notes
- This repository currently uses `app.py` as the FastAPI entry point.
- The renderer can be any Chromium-compatible CDP endpoint and is only used when `method` is set to `cdp`.
- The `webfetcher` container image is pulled from GHCR by default in `docker-compose.yml`.

## Publish Container to GHCR
This repository includes a GitHub Actions workflow at `.github/workflows/publish-ghcr.yml` that publishes the `webfetcher` image to GHCR.

Publishing options:
- Publish a GitHub Release: when a release is published, the workflow builds from that tag and pushes the image.
- Manual dispatch: run the workflow manually and provide the target `tag` input.

Published image:
- `ghcr.io/<owner>/<repo>:<tag>`
- `ghcr.io/<owner>/<repo>:sha-<short-commit>`
- `ghcr.io/<owner>/<repo>-lightpanda:<tag>`
- `ghcr.io/<owner>/<repo>-lightpanda:sha-<short-commit>`

Example pull command:

```bash
docker pull ghcr.io/mitslabo/webfetcher:0.2.0
docker pull ghcr.io/mitslabo/webfetcher-lightpanda:0.2.0
```

Run with Compose using a published GHCR image:

```bash
set WEBFETCHER_TAG=0.2.0
set LIGHTPANDA_TAG=0.2.0
docker compose up -d
```

To stop:

```bash
docker compose down
```

## Publishing Checklist
- Add a repository description and topics on GitHub.
- Set the repository visibility and default branch policy.
- Confirm `.env` is not committed (`.gitignore` is already configured).
- Verify `LICENSE`, `CONTRIBUTING.md`, and `SECURITY.md` are present.

## Project Policies
- License: AGPL-3.0 (see `LICENSE`)
- Contribution guide: see `CONTRIBUTING.md`
- Security policy: see `SECURITY.md`
