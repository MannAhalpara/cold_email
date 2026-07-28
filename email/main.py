import json
import os
import re
from pathlib import Path
from dotenv import load_dotenv

import tinyfish_scraper
import openrouter
import send_email

load_dotenv()

WEBSITES_FILE = Path("websites.txt")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def read_urls() -> list[str]:
    """Read website URLs from websites.txt."""
    if WEBSITES_FILE.exists():
        with open(WEBSITES_FILE, "r", encoding="utf-8") as f:
            urls = [u.strip() for u in f if u.strip()]
        if urls:
            return urls
    return []


def main() -> None:
    if not os.getenv("OPENROUTER_API_KEY"):
        raise RuntimeError("Please set OPENROUTER_API_KEY in your .env file")

    sender_email = os.getenv("EMAIL_ADDRESS", "").strip()
    app_password = os.getenv("EMAIL_PASSWORD", "").strip()

    print("\n==============================================")
    print("      Cold Email Pipeline Automation          ")
    print("==============================================\n")

    # Ensure credentials are present
    if not sender_email:
        sender_email = input("Enter your Gmail address (Sender): ").strip()
    if not app_password:
        app_password = input("Enter your Gmail App Password: ").strip()

    urls = read_urls()
    if not urls:
        print(f"❌ No URLs found in {WEBSITES_FILE}. Please add URLs and try again.")
        return

    # Initialize TinyFish API client
    tf_client = tinyfish_scraper.init_client()

    for index, url in enumerate(urls, 1):
        print(f"\n[{index}/{len(urls)}] Processing Website: {url}")
        print("-" * 50)

        try:
            # 1. Fetch & Analyze site using tinyfish_scraper.py -> saves data into output/
            print("🔍 [1/3] Scraping & analyzing page with TinyFish...")
            page_data = tinyfish_scraper.fetch_and_analyze_site(url, client=tf_client, output_dir=OUTPUT_DIR)
            print(f"Saved analysis to {OUTPUT_DIR / tinyfish_scraper.filename_from_url(url)}")

            # 2. Generate Email using openrouter.py
            print("✍️  [2/3] Generating cold email via OpenRouter...")
            email_result = openrouter.generate_email(page_data)

            print("\n---------------- GENERATED EMAIL PREVIEW ----------------")
            print(f"Subject: {email_result['subject']}\n")
            print(email_result["body"])
            print("----------------------------------------------------------")

            # 3. Prompt terminal user for Receiver Email
            receiver_email = input("\nEnter receiver email address: ").strip()
            while not receiver_email:
                receiver_email = input("Receiver email is required. Enter receiver email: ").strip()

            # 4. Directly save email as draft inside Gmail
            print(f"Saving draft inside Gmail for {receiver_email}...")
            send_email.save_draft_gmail(
                sender_email=sender_email,
                app_password=app_password,
                receiver_email=receiver_email,
                subject=email_result["subject"],
                body=email_result["body"],
            )

        except Exception as err:
            print(f"❌ Failed processing for {url}: {err}")

    print("\n🎉 Pipeline completed for all websites.")


if __name__ == "__main__":
    main()
