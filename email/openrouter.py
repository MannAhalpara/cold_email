import json
import os
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
INPUT_DIR = Path("output")
OUTPUT_DIR = Path("emails")
OUTPUT_DIR.mkdir(exist_ok=True)

MODEL = "google/gemma-4-26b-a4b-it:free"


def generate_email(page: dict) -> dict:
    """
    Generate a personalized cold email using OpenRouter API based on analyzed website data.
    Returns a dict with 'subject' and 'body'.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set in environment variables or .env file.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    content = page.get("content", "")
    title = page.get("title", "")

    prompt = f"""
You are an expert cold email writer.

Your task is to carefully analyze the following webpage.

The webpage may belong to
- a professor
- a researcher
- a startup founder
- a company
- a CTO
- a CEO

Understand
- who they are
- what they work on
- their research
- achievements
- recent work
- interests
- projects
- publications
- technologies

Then write a highly personalized cold email.

Rules:
- Start the response with a line starting with "Subject: <Your Email Subject Line>".
- Never hallucinate.
- Mention only facts present in the webpage.
- Sound natural.
- No generic compliments.
- Maximum 220 words.
- Professional tone.
- End with a call to action.

Page Title:
{title}

Website Content:
{content}
"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "reasoning": {
                "enabled": True
            }
        }
    )

    response.raise_for_status()
    data = response.json()
    raw_result = data["choices"][0]["message"]["content"].strip()

    subject = "Cold Email Opportunity"
    body = raw_result

    # Parse subject line if returned by LLM
    if raw_result.lower().startswith("subject:"):
        lines = raw_result.split("\n", 1)
        subject_line = lines[0]
        # Remove prefix "Subject:" case-insensitively
        if ":" in subject_line:
            subject = subject_line.split(":", 1)[1].strip()
        body = lines[1].strip() if len(lines) > 1 else raw_result

    return {
        "subject": subject,
        "body": body,
        "raw": raw_result
    }


if __name__ == "__main__":
    for file in INPUT_DIR.glob("*.json"):
        print(f"Processing {file.name}")
        with open(file, "r", encoding="utf8") as f:
            page_data = json.load(f)
        try:
            email_res = generate_email(page_data)
            save_path = OUTPUT_DIR / (file.stem + "_email.md")
            with open(save_path, "w", encoding="utf8") as f:
                f.write(f"Subject: {email_res['subject']}\n\n{email_res['body']}")
            print("Saved:", save_path)
        except Exception as err:
            print(f"Failed for {file.name}: {err}")
    print("\nDone.")