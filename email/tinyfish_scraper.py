import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv
from tinyfish import TinyFish

load_dotenv()

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def init_client() -> TinyFish:
    """Initialize and return a TinyFish API client."""
    return TinyFish()


def filename_from_url(url: str) -> str:
    """Generate a clean JSON filename from a website URL."""
    parsed = urlparse(url)
    name = parsed.netloc + parsed.path
    name = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    return name + ".json"


def fetch_and_analyze_site(url: str, client: TinyFish = None, output_dir: Path = OUTPUT_DIR) -> dict:
    """Fetch website content via TinyFish, format clean structure, and save JSON into output directory."""
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

    clean_data = {
        "url": page.get("final_url") or page.get("url"),
        "title": page.get("title"),
        "description": page.get("description"),
        "author": page.get("author"),
        "published_date": page.get("published_date"),
        "content": page.get("text"),
    }

    output_dir.mkdir(exist_ok=True)
    outfile = output_dir / filename_from_url(url)
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, indent=4, ensure_ascii=False)

    return clean_data


if __name__ == "__main__":
    websites_file = Path("websites.txt")
    if websites_file.exists():
        with open(websites_file, "r", encoding="utf-8") as f:
            urls = [u.strip() for u in f if u.strip()]
        tf_client = init_client()
        for u in urls:
            print(f"Analyzing {u}...")
            data = fetch_and_analyze_site(u, tf_client)
            print(f"Saved: {data.get('title')}")
