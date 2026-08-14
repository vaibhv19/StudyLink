# StudyLink Backend API

This is the Django REST API server for StudyLink.

## Technology Stack
- Django 5.0
- Django REST Framework 3.15
- SimpleJWT 5.3
- Supabase PostgreSQL (via dj-database-url)
- django-storages S3 compatible client

## Getting Started

### Prerequisites
- Python 3.12+ (Python 3.14 recommended/local)
- Virtual Environment (.venv)

### Setup & Run
1. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy environment template and fill in settings:
   ```bash
   cp .env.example .env
   ```
4. Run system checks and database migrations:
   ```bash
   python manage.py check
   python manage.py migrate
   ```
5. Launch the local API server:
   ```bash
   python manage.py runserver
   ```
