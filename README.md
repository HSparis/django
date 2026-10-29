# Neo Niigata

Neo Niigata is a Django magazine for sharing discoveries about Japan, games, culture and technology. Visitors can browse and filter published articles; registered authors can create, edit and delete their own posts.

## Requirements

- Python 3.12
- PostgreSQL

## Local setup

1. Create and activate a virtual environment:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install the project dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Create a local environment file and set its values:

   ```powershell
   Copy-Item .env.example .env
   ```

   Generate a secret key with:

   ```powershell
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

   Put the generated value in `SECRET_KEY` in `.env`, then configure the local PostgreSQL database values.

4. Apply migrations and start the development server:

   ```powershell
   python manage.py migrate
   python manage.py runserver
   ```

   The development configuration reads `.env`. Keep `DEBUG=True` only for local development.

## Sample articles

To add ten original, English-language sample articles with locally generated cover
images, first create an account if you do not already have one:

```powershell
python manage.py createsuperuser
```

Then run the seed command with that account's username:

```powershell
python manage.py seed_initial_posts --author your_username
```

The command publishes the articles and leaves existing articles unchanged when
run again.

## Tests

The project test settings use an isolated in-memory SQLite database and do not require the local PostgreSQL database or `.env`:

```powershell
python manage.py check --settings=config.test_settings
python manage.py test blog --settings=config.test_settings
```

## Production deployment

Use a Python host that supports Django and Gunicorn. Install dependencies, then configure these environment variables in the host dashboard; do not commit `.env` or production credentials:

- `SECRET_KEY`: a newly generated, private Django secret key
- `DEBUG=False`
- `ALLOWED_HOSTS`: comma-separated hostnames, without schemes (for example, `example.com,www.example.com`)
- `CSRF_TRUSTED_ORIGINS`: comma-separated HTTPS origins (for example, `https://example.com,https://www.example.com`)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: the host's PostgreSQL connection details
- `SECURE_SSL_REDIRECT=True` when HTTPS is terminated by the host or a correctly configured trusted proxy
- After confirming the entire site is served over HTTPS, set `SECURE_HSTS_SECONDS=31536000` to enable one year of HSTS
- Set `SECURE_HSTS_INCLUDE_SUBDOMAINS=True` only if every subdomain uses HTTPS; set `SECURE_HSTS_PRELOAD=True` only if the domain meets the browser preload requirements
- `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, and `DEFAULT_FROM_EMAIL` when password-reset email should be sent through an SMTP provider

Run these commands as part of the release:

```sh
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

Start the application with:

```sh
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

WhiteNoise serves collected static assets. User-uploaded article covers are stored under `MEDIA_ROOT`; configure durable object storage or a persistent media volume on the hosting platform before deploying, because many application hosts erase local files during redeploys. Keep `DEBUG=False` in production so Django uses the custom 404 and 500 pages and does not expose debug details.

## Project layout

- `blog/`: articles, categories, authentication views, templates and static assets
- `config/`: Django settings, URL routing and WSGI/ASGI entry points
- `media/`: local development uploads (ignored by Git)
