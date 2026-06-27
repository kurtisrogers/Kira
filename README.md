# Kira

An extendable Jira clone built with **Django**, **HTMX**, **Alpine.js**, and **[Pico CSS](https://picocss.com/)**.

Lightweight by design: semantic HTML, minimal custom CSS, and progressive enhancement for interactivity.

## Features

- **Projects** with keys, members, and roles
- **Issues** with types, statuses, priorities, comments, and activity log
- **Kanban boards** with HTMX-powered status moves
- **Extension registry** for plugins (nav items, issue types, dashboard widgets, hooks)
- **Pico CSS** for clean, class-light styling

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_kira
python manage.py runserver
```

Open http://127.0.0.1:8000/ and log in with `admin` / `admin` or `demo` / `demo`.

## Extending Kira

Register extensions from any Django app's `AppConfig.ready()`:

```python
from apps.core.extensions import registry

registry.register(
    "nav_items",
    {"label": "Reports", "url_name": "myapp:reports", "icon": "chart"},
    key="reports",
    priority=50,
)
```

Available extension groups: `nav_items`, `issue_types`, `issue_fields`, `board_columns`, `dashboard_widgets`.

See `apps/core/extensions.py` for the registry API.

## Stack

| Layer | Choice |
|-------|--------|
| Backend | Django 5 |
| Interactivity | HTMX + Alpine.js |
| Styling | Pico CSS v2 |
| Database | SQLite (swap for Postgres in production) |

## Project structure

```
apps/
  accounts/   # Users & profiles
  boards/     # Kanban boards
  core/       # Extension registry, shared models
  issues/     # Issues, comments, workflows
  projects/   # Projects & membership
```

## License

MIT
