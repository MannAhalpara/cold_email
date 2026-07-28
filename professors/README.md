# Professors Database & Web Application (Neon PostgreSQL Integration)

This application provides a web UI and FastAPI backend to manage professor records directly in a **Neon PostgreSQL** database.

## Database Table Schema

The application automatically connects to your Neon database using the `DATABASE_URL` in `.env` and initializes the following schema:

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
    lab_name TEXT,
    lab_link TEXT,
    webpage_1 TEXT,
    webpage_2 TEXT,
    webpage_3 TEXT
);
```

## How to Run

1. Open your terminal in `c:\Project\COLD_EMAIL\professors`.
2. Run the application:
   ```bash
   ..\.venv\Scripts\python.exe main.py
   ```
3. Open your browser and navigate to:
   **http://localhost:8000**

## Features

- 🟢 **Live Database Connection**: Connected directly to Neon DB.
- ✨ **Add / Edit Professor Form**: Comprehensive input form with auto-ID or custom ID generation.
- 📚 **Directory View**: Search and filter by name, university, department, research area, designation, or country.
- 🎲 **Sample Data Filler**: Easily test form submission with prefilled top AI researchers.
- 📋 **Quick Actions**: Copy email, visit lab link / webpages, edit, or delete records directly.
