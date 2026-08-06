# Cold Email Automation & Professor Database Platform

A high-performance, full-stack application designed to manage academic professor databases, automate web scraping of lab research data, generate personalized AI outreach alignment paragraphs using OpenRouter LLMs, and synchronize draft emails directly with Gmail.

---

## Architecture Overview

The project is structured into clear, functional modules separating frontend presentation logic from backend processing pipelines.

```
c:\Project\COLD_EMAIL\
├── frontend/
│   └── index.html                Single-page application (UI, routing, GSAP animations)
├── backend/
│   ├── main.py                   FastAPI backend server and API endpoints
│   ├── openrouter.py             OpenRouter AI research paragraph generator
│   ├── send_email.py             SMTP transmission and IMAP Gmail draft engine
│   └── tinyfish_scraper.py       In-memory web scraping module
├── main.py                       Root application entry point
├── Dockerfile                    Container deployment configuration
├── requirements.txt              Python package dependencies
├── .env                          Environment variable configuration (Git-ignored)
└── .gitignore                    Version control exclusion rules
```

---

## Core Capabilities

### 1. Centralized Database Management
- Comprehensive professor record keeping (Name, Email, Designation, University, Department, Country, Research Area, Web Links).
- Real-time search, multi-parameter filtering, pagination, and one-click Microsoft Excel (`.xlsx`) report export.
- Activity tracking with weekly interaction graphs and status badges.

### 2. Automated In-Memory Web Scraping
- Fetches and parses professor faculty web pages, laboratory sites, and publication links.
- Uses TinyFish API to extract relevant text and markdown in memory without storing temporary local files.

### 3. OpenRouter AI Alignment Engine
- Uses OpenRouter LLM endpoints (`google/gemma-4-26b-a4b-it:free`, `meta-llama/llama-3.3-70b-instruct:free`, `google/gemini-2.0-flash-exp:free`, `qwen/qwen-2.5-72b-instruct:free`).
- Generates 2 to 3 concise, impactful lines highlighting the professor's most recent or highly effective research findings.
- Automatically tailors candidate skills and experience to recipient lab focus areas.

### 4. Direct Gmail Draft Synchronization
- Formats personalized emails using customizable user templates.
- Saves drafts directly to the user's Gmail `[Gmail]/Drafts` folder via IMAP.
- Supports encrypted credentials via Fernet symmetric encryption and multiple attachment management directly inside the UI.

### 5. Single-Page Application (SPA) Frontend
- Vanilla JavaScript SPA with smooth HTML5 history routing (`/`, `/professors`, `/email-dashboard`, `/email-setup`, `/email-settings`, `/completed`).
- GSAP 3.12 hero entrance animations.
- Centered, expanded modal view for email composing with real-time SSE progress step tracking.

---

## Technology Stack

- **Backend Framework**: Python 3.11+, FastAPI, Uvicorn
- **Database**: PostgreSQL (Neon Serverless PostgreSQL), Psycopg2
- **AI / LLM Integration**: OpenRouter API
- **Web Scraping**: TinyFish API Client
- **Security**: Cryptography (Fernet symmetric key encryption)
- **Frontend Engine**: HTML5, Vanilla JavaScript (ES6+), Vanilla CSS
- **Animation**: GSAP 3.12 (GreenSock Animation Platform)
- **Excel Generation**: OpenPyXL

---

## Database Schema

The platform connects to PostgreSQL using `DATABASE_URL` and initializes four primary tables:

### 1. `professors`
Stores records of faculty members.
```sql
CREATE TABLE IF NOT EXISTS professors (
    id TEXT PRIMARY KEY,
    professor_name TEXT NOT NULL,
    email TEXT NOT NULL,
    university TEXT,
    department TEXT,
    designation TEXT,
    country TEXT,
    research_area TEXT,
    webpage_1 TEXT,
    webpage_2 TEXT,
    webpage_3 TEXT,
    lab_link TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2. `email_logs`
Tracks email generation and draft history.
```sql
CREATE TABLE IF NOT EXISTS email_logs (
    id TEXT PRIMARY KEY,
    professor_id TEXT,
    professor_name TEXT,
    university TEXT,
    subject TEXT,
    body TEXT,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 3. `email_attachments`
Stores attachments associated with email drafts.
```sql
CREATE TABLE IF NOT EXISTS email_attachments (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_data BYTEA NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type TEXT DEFAULT 'application/octet-stream',
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4. `user_credentials`
Stores encrypted sender email addresses and app passwords.
```sql
CREATE TABLE IF NOT EXISTS user_credentials (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    sender_email TEXT NOT NULL,
    encrypted_password TEXT NOT NULL,
    user_name TEXT DEFAULT '',
    user_bio TEXT DEFAULT '',
    email_template TEXT DEFAULT '',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## Setup and Installation

### Prerequisites
- Python 3.11 or higher
- PostgreSQL Database Connection String (e.g., Neon PostgreSQL)
- OpenRouter API Key
- Gmail Account with App Password enabled

### 1. Environment Configuration
Create a `.env` file in the project root directory:

```ini
DATABASE_URL=postgresql://user:password@ep-example.neon.tech/neondb?sslmode=require
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key
ENCRYPTION_KEY=your-fernet-base64-encryption-key
PORT=8000
```

To generate a valid Fernet encryption key, run:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 2. Installation
Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/your-username/COLD_EMAIL.git
cd COLD_EMAIL

python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Running the Server Locally
Start the application using the root entry script:

```bash
python main.py
```
Or run directly via Uvicorn:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Access the application in your browser at `http://localhost:8000`.

---

## API Endpoint Reference

### Professors Endpoints
- `GET /api/professors` – List professors with optional search query (`?q=`).
- `POST /api/professors` – Create a new professor entry.
- `PUT /api/professors/{prof_id}` – Update professor details.
- `DELETE /api/professors/{prof_id}` – Delete a professor entry.
- `GET /api/export-excel` – Export database records as formatted `.xlsx`.
- `GET /api/weekly-stats` – Retrieve weekly professor addition metrics.

### Email & AI Pipeline Endpoints
- `POST /api/send-email/{prof_id}` – Server-Sent Events (SSE) stream for web scraping, AI generation, and draft preparation.
- `POST /api/save-draft` – Save generated email draft into Gmail `[Gmail]/Drafts` folder via IMAP.
- `GET /api/email-stats` – Retrieve total professor count versus emailed count.
- `GET /api/email-completed` – List all saved drafts and sent email history.

### Attachment Endpoints
- `GET /api/attachments` – List all uploaded email attachments.
- `POST /api/attachments` – Upload a new attachment file into database storage.
- `DELETE /api/attachments/{att_id}` – Remove an attachment from storage.

### Credentials & Settings Endpoints
- `GET /api/email-settings` – Retrieve configuration status and saved user template.
- `POST /api/email-settings` – Save sender email, Gmail App password, bio, and custom email template.

---

## Docker Deployment

Build and run the application container:

```bash
# Build the Docker image
docker build -t cold-email-platform .

# Run the container
docker run -d -p 8000:8000 --env-file .env cold-email-platform
```

---

## Security Practices

- **Zero Hardcoded Secrets**: Secrets and credentials are stored strictly in environment variables.
- **Fernet Symmetric Encryption**: User Gmail App Passwords stored in the database are encrypted at rest using AES-128 in CBC mode with PKCS7 padding.
- **Git Exclusions**: `.env`, `.venv/`, `__pycache__/`, and build logs are explicitly excluded via `.gitignore`.

---

## License

Distributed under the MIT License. See `LICENSE` for details.
