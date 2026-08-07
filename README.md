# Cold Email Automation & Multi-User Professor Database Platform

deployed : [cold-email](https://cold-email-1.vercel.app/)

A high-performance, multi-user full-stack application designed to manage academic professor databases with user data isolation, automate web scraping of lab research data, generate personalized AI outreach alignment paragraphs using OpenRouter LLMs, and synchronize email drafts directly with Gmail.

---

## Key Features

- **Multi-User Architecture**: Secure Email OTP authentication, database-backed 60-day session cookies, and strict per-user data isolation across all records.
- **Centralized Database Management**: Professor record keeping (Name, Email, Designation, University, Department, Country, Research Area, Web Links) with search, filtering, and Excel export.
- **Automated Web Scraping**: Fetches and parses faculty web pages and lab sites using TinyFish API.
- **OpenRouter AI Alignment Engine**: Generates concise personalized research paragraphs for outreach emails.
- **Direct Gmail Synchronization**: Formats emails using custom templates and saves drafts directly to Gmail `[Gmail]/Drafts` via IMAP.

---

## Architecture Overview

```
c:\Project\COLD_EMAIL\
├── frontend/
│   └── index.html                Single-page application (UI, routing, OTP login, GSAP animations)
├── backend/
│   ├── main.py                   FastAPI backend server, auth, and API endpoints
│   ├── openrouter.py             OpenRouter AI research paragraph generator
│   ├── send_email.py             SMTP OTP transmission & IMAP Gmail draft engine
│   └── tinyfish_scraper.py       In-memory web scraping module
├── main.py                       Root application entry point
├── Dockerfile                    Container deployment configuration
├── requirements.txt              Python package dependencies
├── .env                          Environment variable configuration (Git-ignored)
└── .gitignore                    Version control exclusion rules
```

---

## Technology Stack

- **Backend Framework**: Python 3.11+, FastAPI, Uvicorn
- **Database**: PostgreSQL (Neon Serverless PostgreSQL), Psycopg2
- **Authentication**: Email OTP, SHA-256 Hashing, Database User Sessions (HttpOnly Cookie)
- **AI / LLM Integration**: OpenRouter API
- **Web Scraping**: TinyFish API Client
- **Security**: Cryptography (Fernet symmetric key encryption)
- **Frontend Engine**: HTML5, Vanilla JavaScript (ES6+), Vanilla CSS
- **Animation**: GSAP 3.12 (GreenSock Animation Platform)
- **Excel Generation**: OpenPyXL

---

## Database Schema

The platform initializes the following tables in PostgreSQL:

- **`users`**: User account details (`id`, `email`, `created_at`).
- **`otp_codes`**: Temporary 6-digit OTP verification hashes (`id`, `email`, `otp_hash`, `expires_at`).
- **`user_sessions`**: Active login sessions (`id`, `user_id`, `token_hash`, `expires_at`).
- **`professors`**: Faculty database scoped by `user_id`.
- **`email_settings`**: Encrypted email credentials scoped by `user_id`.
- **`email_template`**: Custom user templates scoped by `user_id`.
- **`email_attachments`**: Attachment file binaries scoped by `user_id`.
- **`email_logs`**: Outreach history and status scoped by `user_id`.

---

## API Endpoints

### Authentication
- `POST /api/auth/send-otp` – Send 6-digit verification code to email via Gmail SMTP.
- `POST /api/auth/verify-otp` – Verify OTP, create user if missing, and issue HttpOnly session cookie.
- `GET /api/auth/me` – Retrieve active logged-in user profile.
- `POST /api/auth/logout` – Terminate session and clear authentication cookie.

### Professors
- `GET /api/professors` – List current user's professors with optional search query (`?q=`).
- `POST /api/professors` – Add new professor record.
- `PUT /api/professors/{prof_id}` – Update professor details.
- `DELETE /api/professors/{prof_id}` – Remove professor record.
- `GET /api/professors/export` – Export user's professor records as Excel file.
- `GET /api/weekly-stats` – Retrieve weekly professor creation metrics.

### Email & AI Pipeline
- `POST /api/send-email/{prof_id}` – SSE stream for scraping, AI generation, and draft assembly.
- `POST /api/save-draft` – Save email draft to Gmail via IMAP.
- `GET /api/email-stats` – Retrieve professor and email counts for current user.
- `GET /api/email-logs` – Retrieve outreach email history.

---

## Local Setup

1. **Environment Variables**:
   Create a `.env` file in the root folder:
   ```ini
   DATABASE_URL=postgresql://user:password@ep-example.neon.tech/neondb?sslmode=require
   OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key
   ENCRYPTION_KEY=your-fernet-base64-encryption-key
   authentication_email=your-gmail@gmail.com
   authentication_password=xxxx xxxx xxxx xxxx
   PORT=8000
   ```

2. **Install Dependencies & Run**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

3. Open `http://localhost:8000` in your browser.
