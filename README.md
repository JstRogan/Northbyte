# Northbyte

The Django framework project that related to the site "habr.com".
Articles with categories, ratings (1-5), bookmarks, moderation and user roles
(superadmin / admin / user / guest). Dark and light theme, RU/EN languages.

## How to run

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

`seed_demo` fills the site with demo articles and authors
(demo accounts password: `northbyte-demo`).
Superadmin can be created with `python manage.py createsuperuser`.
