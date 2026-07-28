import os
import sys
import requests
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

FALLBACK_MODELS = [
    "google/gemma-4-26b-a4b-it:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
    "qwen/qwen-2.5-72b-instruct:free",
]


def generate_personalized_paragraph(
    prof: dict,
    combined_web_data: dict = None,
    resume_text: str = ""
) -> str:
    """
    Generate ONLY the single personalized research alignment paragraph using OpenRouter API.
    Returns a string containing the single paragraph.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set in environment variables or .env file.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    prof_info = prof or {}
    prof_name = prof_info.get("professor_name", "Professor")
    university = prof_info.get("university", "")
    department = prof_info.get("department", "")
    designation = prof_info.get("designation", "")
    research_area = prof_info.get("research_area", "")
    lab_name = prof_info.get("lab_name", "")
    web_text = (combined_web_data.get("combined_text", "") if combined_web_data else "").strip()
    if len(web_text) > 6000:
        web_text = web_text[:6000] + "\n...[truncated for length]"

    prompt = f"""
You are an expert cold email assistant. Your task is to write EXACTLY ONE focused, highly personalized academic research alignment paragraph (70 to 120 words).

CANDIDATE (SENDER):
Name: Mann Ahalpara
Resume Summary & Background:
{resume_text}

RECIPIENT (PROFESSOR):
Name: {prof_name}
Designation: {designation}
University: {university}
Department: {department}
Lab Name: {lab_name}
Primary Research Area: {research_area}

SCRAPED WEBPAGES & RESEARCH DATA:
{web_text if web_text else "No additional webpage text available."}

INSTRUCTIONS:
1. Write EXACTLY ONE concise, compelling paragraph (70 to 120 words).
2. Connect Mann Ahalpara's technical skills, project background, or research experience directly to {prof_name}'s specific research focus, lab work, or published papers.
3. DO NOT include greetings (like 'Dear Professor'), subject lines, introductions, or sign-offs (like 'Sincerely').
4. Return ONLY the single paragraph. No extra commentary or quotes.
"""

    paragraph_result = ""
    last_error = None

    for model_candidate in FALLBACK_MODELS:
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": model_candidate,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                },
                timeout=45
            )
            response.raise_for_status()
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                paragraph_result = data["choices"][0]["message"]["content"].strip()
                if paragraph_result:
                    break
            else:
                last_error = f"Model '{model_candidate}' returned no choices: {data}"
        except Exception as e:
            last_error = f"Model '{model_candidate}' failed: {e}"

    if not paragraph_result:
        raise RuntimeError(f"All OpenRouter models failed. Last error: {last_error}")

    # Remove quotes if surrounded by quotes
    if paragraph_result.startswith('"') and paragraph_result.endswith('"'):
        paragraph_result = paragraph_result[1:-1].strip()

    return paragraph_result


# Alias for backward compatibility
def generate_email(prof: dict = None, combined_web_data: dict = None, resume_text: str = "", page: dict = None) -> dict:
    if prof:
        para = generate_personalized_paragraph(prof, combined_web_data, resume_text)
        return {
            "subject": f"Research Inquiry & Opportunity - {prof.get('professor_name', 'Professor')}",
            "body": para,
            "raw": para
        }
    return {
        "subject": "Research Inquiry",
        "body": "Personalized research paragraph",
        "raw": "Personalized research paragraph"
    }