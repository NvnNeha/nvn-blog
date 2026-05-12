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

- Python 3 / Django 6.0.5
- SQLite (default dev database)
- `django-tailwind` 4.4.2 + `pytailwindcss` for styles
- `django-browser-reload` for hot reload in DEBUG
- Pillow for `ImageField` support

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
pip install "django==6.0.5" django-tailwind pytailwindcss django-browser-reload pillow
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

## Notes

- `DEBUG = True` and the `SECRET_KEY` in `my_blog/settings.py` are dev values — replace before deploying.
- Uploaded images land in `images/upload/` (the `MEDIA_ROOT`) and are served at `/images/` while `DEBUG` is on.
- The "save for later" list is stored in `request.session["stored_list"]`, so it's per-browser and doesn't persist across devices.
- Post editing/deletion is restricted to the post's author via `get_object_or_404(Post, slug=..., user=request.user)`.
