# Library Management System

A Django application for browsing and maintaining a small library catalog. It includes account registration and login, searchable book listings, category assignment, book status and rental pricing fields, and permission-controlled catalog editing.

## Features

- User registration, login, and POST-only logout using Django authentication.
- Public book listing with case-insensitive title search.
- Authenticated dashboard with catalog counts and rental/sales summaries.
- Book create and update forms with numeric validation and optional images.
- Role access through Django permissions: users with `add_books` can add, `change_books` can edit, and `delete_books` can delete books. Category creation uses `add_category`.
- Django admin for staff who have admin access.

The application stores book rental information (`retal_price_day`, `retal_period`, and `total_rental`); it does not implement checkout, due dates, or rental transactions.

## Stack and layout

- Python 3.11+
- Django 5.2 LTS
- SQLite for local development by default; MySQL can be selected through environment variables.
- Bootstrap/AdminLTE templates and static assets.

`library/` contains project configuration and URL setup. `APP/` contains catalog models, forms, views, routes, migrations, and tests. `templates/` contains the existing page templates. New uploads under `media/` are excluded from version control; older checked-in sample images remain in the repository.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies: `python -m pip install -r requirements.txt`.
3. Set variables listed in `.env.example` in your shell or IDE configuration. Django does not load `.env` files automatically; set a stable, unique `DJANGO_SECRET_KEY` in persistent environments.
4. Apply migrations: `python manage.py migrate`.
5. Create an administrator: `python manage.py createsuperuser`.
6. Start the server: `python manage.py runserver`.

SQLite is the default and uses `db.sqlite3` in the project root. Set `DB_ENGINE=mysql` to use MySQL, then configure `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`. Keep `.env` out of source control. `DJANGO_DEBUG` defaults to false; set it to `true` for local development. `DJANGO_ALLOWED_HOSTS` accepts a comma-separated host list.

## User permissions

Registration creates a regular Django user. Assign catalog permissions through Django admin or the shell. A typical Worker can receive `add_books` and `change_books` (and `add_category` if category entry is needed). Grant `delete_books` only to administrators. Customers can browse and search the catalog; the dashboard requires login. Django superusers bypass permission checks.

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
