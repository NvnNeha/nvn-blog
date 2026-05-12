# nvn-blog

A Django-based personal blog where registered users can publish, edit, and delete posts, save posts for later, and leave comments. The UI is styled with Tailwind CSS via `django-tailwind`.

## Features

- User registration, login, and logout (Django auth)
- Create / edit / delete posts (login-required, author-scoped)
- Image upload for post cover art (Pillow)
- Tag-based post organization (many-to-many)
- Public comments on posts (name + email + text)
- "Save for later" list backed by the session — no DB write needed
- Slugged post detail URLs auto-generated from the title
- Tailwind CSS styling with live browser reload in development

## Tech stack

- Python 3 / Django 6.0.5 (class-based views throughout)
- SQLite (default dev database)
- `django-tailwind` 4.4.2 + `pytailwindcss` for styles
- `django-browser-reload` for hot reload in DEBUG
- Pillow for `ImageField` support
- `whitenoise` for production static serving
- `gunicorn` as the WSGI server
- `python-decouple` for env-driven settings

## Project layout

```
nvn-blog/
├── manage.py
├── Procfile.tailwind          # runs django + tailwind together (honcho/foreman)
├── db.sqlite3                 # dev database
├── my_blog/                   # Django project (settings, root urls, wsgi/asgi)
├── blog/                      # main app: models, views, forms, urls, templates
│   ├── models.py              # Post, Tag, Comment
│   ├── views.py               # listing, detail, auth, CRUD, stored posts
│   ├── forms.py               # UserRegistrationForm, CommentModel, CreatePostForm
│   └── templates/blog/        # page + include templates
├── theme/                     # django-tailwind app (static_src, compiled CSS)
├── templates/                 # project-level templates (base.html, registration/)
├── static/                    # project-level static files
└── images/                    # MEDIA_ROOT — uploaded post images
```

## Data model

- **Post** — `user (FK User)`, `title`, `excerpt`, `image`, `date (auto_now)`, `slug (unique)`, `content (min 20 chars)`, `tags (M2M)`
- **Tag** — `caption`
- **Comment** — `user_name`, `user_email`, `text`, `post (FK)`

## URLs

| Path | Name | Purpose |
| --- | --- | --- |
| `/` | `starting_page` | Latest 3 posts |
| `/posts` | `all_posts` | Full post list |
| `/posts/<slug>` | `detailed_post` | Post detail + comment form |
| `/login/` | `user_login` | Login |
| `/register/` | `user_register` | Register + auto-login |
| `/stored-posts/` | `stored_posts` | Session-backed "save for later" list |
| `/create-post/` | `create_post` | Create post (login required) |
| `/edit-post/<slug>/` | `edit_post` | Edit own post |
| `/delete-post/<slug>/` | `delete_post` | Delete own post |
| `/admin/` | — | Django admin |

## Getting started

### 1. Clone and create a virtualenv

```bash
git clone <repo-url> nvn-blog
cd nvn-blog
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 2a. Configure environment

```bash
cp .env.example .env
# generate a real SECRET_KEY:
python -c "import secrets; print(secrets.token_urlsafe(60))"
# paste it into .env, set DEBUG=False + ALLOWED_HOSTS for prod
```

### 3. Apply migrations

```bash
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin
```

### 4. Install Tailwind dependencies (first run only)

```bash
python manage.py tailwind install
```

### 5. Run the dev servers

In two terminals:

```bash
# terminal 1 — Django
python manage.py runserver

# terminal 2 — Tailwind watcher
python manage.py tailwind start
```

Or run both at once with `honcho`/`foreman` using the included `Procfile.tailwind`:

```bash
honcho -f Procfile.tailwind start
```

Then open http://127.0.0.1:8000.

## Deploying to production

1. Provision a host (Railway / Render / Fly / a VPS) and set the env vars from `.env.example` — at minimum `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`.
2. Build assets and collect static:
   ```bash
   python manage.py tailwind build
   python manage.py collectstatic --noinput
   python manage.py migrate --noinput
   ```
3. Run with gunicorn (`Procfile` is wired up for Heroku-style platforms):
   ```bash
   gunicorn my_blog.wsgi --log-file -
   ```

When `DEBUG=False`, the following are enabled automatically: HSTS, secure cookies, SSL redirect, `X_FRAME_OPTIONS=DENY`, content-type-nosniff, and a same-origin referrer policy. WhiteNoise serves compressed, hashed static files.

## Notes

- The "save for later" list is stored in `request.session["stored_list"]`, so it's per-browser and doesn't persist across devices.
- Post editing/deletion is restricted to the post's author via `AuthorRequiredMixin` (`LoginRequiredMixin` + `UserPassesTestMixin`).
- Slugs are auto-deduplicated on create and edit (`-2`, `-3`, …) so duplicate titles don't crash.
- Uploaded images land in `images/upload/` (the `MEDIA_ROOT`) and are served at `/images/` while `DEBUG` is on. In production, point your reverse proxy (or object storage) at `MEDIA_ROOT`.
