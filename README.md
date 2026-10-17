# Library Management System

A Django application for browsing and maintaining a small library catalog. It includes account registration and login, searchable book listings, category assignment, book status and rental pricing fields, and permission-controlled catalog editing.

## Features

- User registration, login, and POST-only logout using Django authentication.
- Public book listing with case-insensitive title search.
- Authenticated dashboard with catalog counts and rental/sales summaries.
- Book create and update forms with numeric validation and optional images.
- Role access through Django permissions: users with `add_books` can add, `change_books` can edit book details and status, and `delete_books` can delete books. Category creation uses `add_category`.
- Django admin for staff who have admin access.

The application stores book rental information (`retal_price_day`, `retal_period`, and `total_rental`); it does not implement checkout, due dates, or rental transactions.

## Stack and layout

- Python 3.11+
- Django 5.2 LTS
- SQLite for local development by default; MySQL can be selected through environment variables.
- Bootstrap/AdminLTE templates and static assets.

`library/` contains project configuration and URL setup. `APP/` contains catalog models, forms, views, routes, migrations, and tests. `templates/` contains the existing page templates. New uploads under `media/` are excluded from version control; older checked-in sample images remain in the repository.

## Setup

Use the pip workflow below; `requirements.txt` is the project's dependency source. `pyproject.toml` contains pytest and Ruff configuration, not package dependencies, so `uv run` alone does not install Django or the requirements file.

In Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:DJANGO_SECRET_KEY = (python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
$env:DJANGO_DEBUG = "true"
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Generate the key once and keep it stable in your local environment if you want sessions to persist between server restarts. `.env.example` lists the supported settings, but Django does not load `.env` files automatically; set the variables in the shell or IDE run configuration. `DJANGO_DEBUG` defaults to false. Local development can omit `DJANGO_SECRET_KEY` when debug is true, but that generates a temporary key each process start. In production/non-debug mode, `DJANGO_SECRET_KEY` is required and startup fails clearly if it is missing. Existing keys are never rotated by the application.

For SQLite, no database variables are needed; the default database is `db.sqlite3` in the project root. To use MySQL, set `DB_ENGINE=mysql` and configure `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`.

`DJANGO_ALLOWED_HOSTS` accepts a comma-separated host list and should be set to the deployment's hostnames. HTTPS redirect remains enabled by default when debug is false; configure `DJANGO_SECURE_SSL_REDIRECT=false` only where HTTPS is terminated elsewhere and the application must not redirect.

## User permissions

Registration creates a regular Django user. Assign catalog permissions through Django admin or the shell. A typical Worker can receive `add_books` and `change_books` (and `add_category` if category entry is needed). `change_books` includes changing a book's status; `can_change_book_status` is not required. Grant `delete_books` only to administrators. Customers can browse and search the catalog; the dashboard requires login. Django superusers bypass permission checks.

## Tests and CI

Run tests with `pytest`. Run project checks with:

```sh
ruff check .
python manage.py check
python manage.py makemigrations --check --dry-run
pytest
```

GitHub Actions runs the same lint, Django checks, migration consistency check, and tests on pushes to `mahmoud` and pull requests targeting `main`, using an in-memory SQLite database.

## Limitations and next steps

- Rental data is descriptive only; there is no rental lifecycle, inventory count, or payment workflow.
- Role assignments are managed through Django permissions and are not provisioned automatically at signup.
- The current templates include legacy UI assets and Arabic text with some encoding artifacts.
- Add rental transaction models and dedicated role setup only when product requirements define those workflows.

No deployment or production operation is included in this repository.
