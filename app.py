from __future__ import annotations

import json
import os
import ssl
from enum import Enum
from logging import getLogger
from typing import Any, Dict, List

import httpx
import trafilatura
import truststore
from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright
from pydantic import BaseModel, Field

CHROME_CDP_URL = os.getenv("CHROME_CDP_URL", "http://127.0.0.1:9222")
HTTPX_TLS_VERIFY = os.getenv("HTTPX_TLS_VERIFY", "true").lower() == "true"


class FetchMethod(str, Enum):
    httpx = "httpx"
    cdp = "cdp"


class FetchRequest(BaseModel):
    URL: List[str] = Field(..., description="List of web page URLs to fetch")
    output_format: str = Field("json", description="Output format for extracted text data")
    with_metadata: bool = True
    method: FetchMethod = FetchMethod.httpx
    include_comments: bool = True
    include_tables: bool = True
    include_formatting: bool = False
    include_links: bool = False
    include_images: bool = False
    favor_precision: bool = False
    favor_recall: bool = False


logger = getLogger("uvicorn.app")
app = FastAPI(title="webfetcher", version="0.1.0")


async def fetch_html_httpx(url: str) -> str:
    ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0, verify=ctx) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


async def fetch_html_cdp(url: str) -> str:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp(CHROME_CDP_URL)
        page = await browser.new_page()
        try:
            response = await page.goto(url, wait_until="networkidle", timeout=30_000)
            if response and not response.ok:
                raise HTTPException(status_code=response.status, detail=f"Failed to fetch {url}")
            html = await page.content()
        finally:
            await page.close()
            await browser.close()
        return html


@app.post("/fetch")
async def fetch(req: FetchRequest) -> Dict[str, Any]:
    results = []
    logger.debug(req.model_dump_json())
    for url in req.URL:
        try:
            if req.method == FetchMethod.cdp:
                html = await fetch_html_cdp(url)
            else:
                html = await fetch_html_httpx(url)

            extracted_contents = trafilatura.extract(
                html,
                output_format=req.output_format,
                include_comments=req.include_comments,
                include_tables=req.include_tables,
                include_formatting=req.include_formatting,
                include_links=req.include_links,
                include_images=req.include_images,
                favor_precision=req.favor_precision,
                favor_recall=req.favor_recall,
                with_metadata=req.with_metadata,
            )
            if extracted_contents is None:
                raise HTTPException(status_code=500, detail=f"Failed to extract content from {url}")

            if req.output_format == "json":
                output_contents = json.loads(extracted_contents)
            else:
                output_contents = {"content": extracted_contents}

            response_body: Dict[str, Any] = {"url": url} | output_contents

            results.append(response_body)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Failed to fetch {url}: {exc}")

    return {"results": results}
