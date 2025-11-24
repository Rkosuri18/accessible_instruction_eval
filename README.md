# Accessible Instruction Evaluation (Django)

A clean, modular Django app that:
- This app allows participants to evaluate PDF or video-based appliance instructions.
- Collects 1–7 ratings across 7 accessibility dimensions
- Captures per-dimension reasons and improvement suggestions
- Stores all data in a relational schema (SQLite by default)


## requirements
asgiref==3.10.0
Django==5.1.13
python-dotenv==1.0.1
sqlparse==0.5.3
tzdata==2025.2


## Quickstart

```bash
## clone the repository
git clone https://github.com/Rkosuri18/accessible_instruction_eval.git
cd accessible_instruction_eval

# create virtual Environment
# Windows
python -m venv .venv313
. .\.venv313\Scripts\Activate.ps1

# Mac or Linux
python3 -m venv .venv313
source .venv313/bin/Activate

# Install Dependencies
pip install -r requirements.txt

# Create Your .env File
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=*

# Apply Migrations
python manage.py migrate


python manage.py seed_questions
# Put your PDFs in media/instructions/
python manage.py load_pdfs media/instructions
python manage.py runserver
```



## Admin

```bash
python manage.py createsuperuser
```
Then visit /admin to manage docs, questions, and sessions.

