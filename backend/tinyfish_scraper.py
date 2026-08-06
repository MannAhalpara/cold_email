import sys
import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv
from tinyfish import TinyFish

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()


def init_client() -> TinyFish:
    """Initialize and return a TinyFish API client."""
    return TinyFish()


def fetch_and_analyze_site(url: str, client: TinyFish = None) -> dict:
    """Fetch website content via TinyFish API completely in-memory."""
    if client is None:
        client = init_client()

    response = client.fetch.get_contents(
        urls=[url],
        format="markdown",
        links=False,
        image_links=False,
        include_html_head=False,
    )

    if hasattr(response, "model_dump"):
        response = response.model_dump()

    page = response["results"][0]

    return {
        "url": page.get("final_url") or page.get("url"),
        "title": page.get("title"),
        "description": page.get("description"),
        "author": page.get("author"),
        "published_date": page.get("published_date"),
        "content": page.get("text"),
    }


def fetch_and_combine_prof_sites(prof: dict, client: TinyFish = None) -> dict:
    """
    Collect lab_link, webpage_1, webpage_2, webpage_3 from professor dict,
    scrape each valid URL in-memory, and return combined research text.
    """
    if client is None:
        client = init_client()

    urls_to_scrape = []
    for key in ["lab_link", "webpage_1", "webpage_2", "webpage_3"]:
        val = prof.get(key)
        if val and isinstance(val, str) and val.strip().startswith(("http://", "https://")):
            if val.strip() not in [u[1] for u in urls_to_scrape]:
                urls_to_scrape.append((key, val.strip()))

    scraped_pages = []
    combined_text = []

    for key, url in urls_to_scrape:
        try:
            print(f"   [SCRAPE] Fetching {key}: {url}")
            page_data = fetch_and_analyze_site(url, client=client)
            scraped_pages.append(page_data)
            t = page_data.get("title") or ""
            c = page_data.get("content") or ""
            if c:
                combined_text.append(f"--- Webpage ({key}): {url} ---\nTitle: {t}\nContent:\n{c}")
        except Exception as e:
            print(f"   [WARNING] Failed scraping {url}: {e}")

    return {
        "prof_id": prof.get("id"),
        "prof_name": prof.get("professor_name"),
        "pages": scraped_pages,
        "combined_text": "\n\n".join(combined_text)
    }
