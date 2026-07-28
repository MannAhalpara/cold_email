import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import pypdf

# Ensure Windows console handles UTF-8 characters gracefully
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import tinyfish_scraper
import openrouter
import send_email

# Load environment variables from .env in email directory
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)

# Also check professors/.env if DATABASE_URL is missing
if not os.getenv("DATABASE_URL"):
    prof_env = BASE_DIR.parent / "professors" / ".env"
    if prof_env.exists():
        load_dotenv(dotenv_path=prof_env)

RESUME_PATH = BASE_DIR / "Mann_Ahalpara_Resume.pdf"

# ==============================================================================
# MASTER COLD EMAIL DRAFT TEMPLATE
# You can customize the static email text below.
# Placeholder {personalized_paragraph} will be filled by OpenRouter LLM analysis.
# ==============================================================================
MASTER_EMAIL_TEMPLATE = """Dear {last_name},

I hope you are doing well.

I am Mann Ahalpara, a final-year Artificial Intelligence & Data Science student at ICT (ranked 1st in my department). I am writing to express my strong interest in joining your research group at {university} for potential research opportunities or graduate studies.

{personalized_paragraph}

In my academic journey, I have worked extensively on LLM-based and applied AI systems:

    • Mini-RAG System – Built a Retrieval-Augmented Generation pipeline to improve factual grounding and reduce hallucinations in LLM outputs.

    • Learnistic – AI Learning Platform – Designed a personalized learning system with AI-driven recommendations and conversational support.

    • Local AI System & AXON – Developed locally deployed AI assistants integrating open-source LLMs with optimized inference pipelines.

Additionally, I co-authored and presented a research paper at ICIDS 2025 analyzing Indian stock markets using statistical correlation techniques, which strengthened my quantitative reasoning and analytical foundation.

Through these experiences, I have developed strong proficiency in Python, machine learning, LLM integration, and retrieval-based architectures. I am eager to deepen my understanding of sentiment representation, commonsense knowledge integration, and explainable AI — particularly through neurosymbolic approaches.

I would be extremely grateful if you would consider me for a research internship, remote collaboration, or any opportunity to contribute to your research group. I am highly motivated to engage rigorously in research and contribute meaningfully to advancing interpretable and emotionally intelligent AI systems.

I have attached my resume for your reference.

LinkedIn: https://www.linkedin.com/in/mannahalpara/
GitHub: https://github.com/MannAhalpara

Thank you very much for your time and consideration. I sincerely hope for the opportunity to learn from and contribute to your research.

Warm regards,
Mann Ahalpara
B.Tech ICT, Adani University
Ahmedabad, India
mannahalpara@gmail.com
+91 99044 45765
"""


def get_db_connection():
    db_url = os.getenv("DATABASE_URL", "").strip()
    if not db_url:
        raise RuntimeError("DATABASE_URL environment variable is missing.")
    return psycopg2.connect(db_url, cursor_factory=RealDictCursor)


def fetch_professors_from_db() -> list[dict]:
    """Fetch all professor records from Neon PostgreSQL database."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM professors ORDER BY professor_name ASC;")
            rows = cur.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()


def extract_resume_text(pdf_path: Path) -> str:
    """Extract full text from candidate resume PDF."""
    if not pdf_path.exists():
        print(f"[WARNING] Resume file not found at {pdf_path}. Email will be generated without resume text.")
        return ""
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        print(f"[INFO] Resume text loaded from {pdf_path.name} ({len(text)} characters).")
        return text
    except Exception as e:
        print(f"[WARNING] Error reading resume PDF: {e}")
        return ""


def get_last_name(full_name: str) -> str:
    """Helper to extract last name or professor name for greeting."""
    name_parts = full_name.strip().split()
    if not name_parts:
        return "Professor"
    # Remove titles if present
    clean_parts = [p for p in name_parts if p.lower() not in ["dr.", "dr", "prof.", "prof", "professor"]]
    if clean_parts:
        return clean_parts[-1]
    return name_parts[-1]


def main() -> None:
    if not os.getenv("OPENROUTER_API_KEY"):
        raise RuntimeError("Please set OPENROUTER_API_KEY in your .env file")

    sender_email = os.getenv("EMAIL_ADDRESS", "").strip()
    app_password = os.getenv("EMAIL_PASSWORD", "").strip()

    print("\n=======================================================")
    print("   Database-Driven Cold Email Pipeline Automation      ")
    print("=======================================================\n")

    if not sender_email:
        sender_email = input("Enter your Gmail address (Sender): ").strip()
    if not app_password:
        app_password = input("Enter your Gmail App Password: ").strip()

    # 1. Load candidate resume
    resume_text = extract_resume_text(RESUME_PATH)

    # 2. Fetch professors from Neon Postgres DB
    print("\n[DB] Fetching professors from database...")
    try:
        professors = fetch_professors_from_db()
        print(f"[DB] Loaded {len(professors)} professor(s) from database.")
    except Exception as err:
        print(f"[ERROR] Failed to fetch professors from database: {err}")
        return

    if not professors:
        print("[WARNING] No professors found in database table 'professors'.")
        return

    # 3. Initialize TinyFish client
    tf_client = tinyfish_scraper.init_client()

    # 4. Process each professor
    for index, prof in enumerate(professors, 1):
        prof_name = prof.get("professor_name", "Unknown Professor")
        receiver_email = prof.get("email", "").strip()
        university = prof.get("university", "your institution")
        department = prof.get("department", "")

        print(f"\n[{index}/{len(professors)}] Processing Professor: {prof_name} ({university})")
        print("-" * 65)
        print(f"   Email: {receiver_email}")
        print(f"   Dept: {department} | Research: {prof.get('research_area', '')}")

        if not receiver_email:
            print("   [WARNING] No receiver email specified in database record. Skipping...")
            continue

        try:
            # Step A: Scrape & combine all available webpage URLs into 1 in-memory context
            print("   [1/3] Scraping webpages (lab_link, webpage_1/2/3) in-memory via TinyFish...")
            combined_web_data = tinyfish_scraper.fetch_and_combine_prof_sites(
                prof=prof,
                client=tf_client
            )
            scraped_count = len(combined_web_data.get("pages", []))
            print(f"   [INFO] Scraped {scraped_count} webpage(s) in-memory.")

            # Step B: Generate ONLY the single personalized research paragraph via OpenRouter
            print("   [2/3] Generating personalized research paragraph via OpenRouter...")
            personalized_paragraph = openrouter.generate_personalized_paragraph(
                prof=prof,
                combined_web_data=combined_web_data,
                resume_text=resume_text
            )

            # Step C: Assemble the single master email draft
            last_name = get_last_name(prof_name)
            subject = f"Research Inquiry & Opportunities - {prof_name} ({university})"
            email_body = MASTER_EMAIL_TEMPLATE.format(
                last_name=last_name,
                professor_name=prof_name,
                university=university,
                department=department,
                personalized_paragraph=personalized_paragraph
            )

            print("\n---------------- MASTER EMAIL DRAFT PREVIEW ----------------")
            print(f"Subject: {subject}\n")
            print(email_body)
            print("-------------------------------------------------------------\n")

            # Step D: Save 1 draft inside Gmail IMAP with resume attached
            print(f"   [3/3] Saving 1 draft inside Gmail for {receiver_email}...")
            send_email.save_draft_gmail(
                sender_email=sender_email,
                app_password=app_password,
                receiver_email=receiver_email,
                subject=subject,
                body=email_body,
                attachment_path=str(RESUME_PATH) if RESUME_PATH.exists() else None
            )

        except Exception as err:
            print(f"[ERROR] Failed processing for professor '{prof_name}': {err}")

    print("\n[SUCCESS] Pipeline completed for all database professors.")


if __name__ == "__main__":
    main()
