# TableStory

**Good food, clearly told.**

TableStory is a recipe discovery app for home cooks. Browse the collection, search by
dish or ingredient, read ingredients and an ordered method, and save what you like to
**My Cookbook** — from a phone or from a television with a remote.

Saved recipes live in application memory and reset when the server restarts. There is
no database, no account, and no network access needed once dependencies are installed.

## Install

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r demo-app/requirements.txt
```

## Run the server

```bash
.venv/bin/python demo-app/app.py
```

The app listens on <http://127.0.0.1:8347>. Port 8347 stays clear of the ports
development tools usually claim; set `PORT` to move it:

```bash
PORT=9500 .venv/bin/python demo-app/app.py
```

## Open the two experiences

| Experience | URL | Notes |
| --- | --- | --- |
| Mobile / desktop | <http://127.0.0.1:8347/> | Designed for a 375 px viewport upwards |
| Television | <http://127.0.0.1:8347/?mode=tv> | Best at 1920×1080; also served automatically to TV browsers |

Add `?mode=mobile` to force the phone layout on a television.

### Remote control

- **Browse:** Arrow Left / Arrow Right move between recipes in a rail, Arrow Up /
  Arrow Down move between rails, Enter opens the focused recipe.
- **Recipe:** Arrow Up / Arrow Down move between the back and My Cookbook actions,
  Enter activates the focused action, Escape or Backspace returns to browse.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/recipes` | All recipes, optionally filtered by `?q=` |
| `GET` | `/api/recipes/<recipe_id>` | One recipe, or `404 {"error": "Recipe not found"}` |
| `GET` | `/api/cookbook` | Saved recipes, as complete recipe objects |
| `POST` | `/api/cookbook` | Save a recipe — body `{"id": "<recipe_id>"}`, returns `201` |
| `DELETE` | `/api/cookbook/<recipe_id>` | Remove a saved recipe (idempotent) |
| `GET` | `/api/rails` | The four named TV rails and their `recipe_ids` |

`q` uses the same case-insensitive match as the browse page, across title,
description, category, dietary tags and ingredient text.

## Tests

```bash
.venv/bin/python -m pytest -q demo-app/tests        # server, data, cookbook, rails, TV mode
node --test demo-app/static/tests/*.test.js         # client search and remote-control logic
```

## Layout

| File | Responsibility |
| --- | --- |
| `demo-app/app.py` | Flask routes, TV-mode detection, JSON API |
| `demo-app/recipes.json` | The 13-recipe collection |
| `demo-app/recipe_data.py` | Fixture loading and eager validation |
| `demo-app/recipe_search.py` | Query normalisation, matching, total time |
| `demo-app/cookbook.py` | In-memory My Cookbook store |
| `demo-app/rails.py` | Derived TV rail composition |
| `demo-app/static/tv-logic.js` | Pure remote-control focus arithmetic |
