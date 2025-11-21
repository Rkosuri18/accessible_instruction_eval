# Accessible Instruction Evaluation (Django)

A clean, modular Django app that:
- Shows a randomly selected instruction PDF
- Collects 1–7 ratings across 7 accessibility dimensions
- Captures per-dimension reasons and improvement suggestions
- Stores all data in a relational schema (SQLite by default)

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # edit SECRET_KEY in .env
python manage.py migrate
python manage.py seed_questions
# Put your PDFs in media/instructions/
python manage.py load_pdfs media/instructions
python manage.py runserver
```

Open http://127.0.0.1:8000

## Admin

```bash
python manage.py createsuperuser
```
Then visit /admin to manage docs, questions, and sessions.
