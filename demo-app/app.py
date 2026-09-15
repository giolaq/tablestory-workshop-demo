"""TableStory: recipe discovery for phones and televisions.

Wires the pure recipe modules (data, search, cookbook, rails) to HTTP. The
supported surface is recipe-domain only: recipe pages, the recipe collection
API, My Cookbook and the TV rails endpoint.
"""

from __future__ import annotations

from flask import Flask, abort, jsonify, render_template, request

from cookbook import CookbookStore, UnknownRecipeError
from rails import build_rails
from recipe_data import load_recipes
from recipe_search import filter_recipes, total_minutes

TAGLINE = "Good food, clearly told."
NO_MATCHES = "No recipes found. Try another ingredient or dish."
UNKNOWN_RECIPE = "Recipe not found"

TV_MODE = "tv"

# Substrings that identify a television browser. Lower-cased before comparison.
TV_USER_AGENT_HINTS = (
    "smart-tv",
    "smarttv",
    "googletv",
    "android tv",
    "appletv",
    "crkey",
    "hbbtv",
    "netcast",
    "viera",
    "bravia",
    "fire tv",
    "firetv",
    # Fire TV device codes are spelled out rather than matching a bare "aft",
    # which would also fire on unrelated words in desktop user agents.
    "aftb",
    "aftm",
    "afts",
    "aftt",
    "aftka",
    "web0s",
    "webos",
    "tizen",
)


def wants_tv(mode: str | None, user_agent: str | None) -> bool:
    """True when the television layout should be served.

    An explicit ``mode`` query value always decides, so ``?mode=mobile`` can
    override a television user agent. Otherwise the user agent is sniffed.
    """
    if mode:
        return mode.strip().casefold() == TV_MODE
    hint_source = (user_agent or "").casefold()
    return any(hint in hint_source for hint in TV_USER_AGENT_HINTS)


def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)
    collection = load_recipes()
    cookbook = CookbookStore(collection)
    app.config.update(TESTING=testing, COOKBOOK=cookbook)
    app.jinja_env.globals.update(total_minutes=total_minutes, TAGLINE=TAGLINE)

    def tv_requested() -> bool:
        return wants_tv(request.args.get("mode"), request.headers.get("User-Agent"))

    @app.get("/")
    def index():
        if tv_requested():
            return render_template(
                "tv.html",
                rails=build_rails(collection, cookbook.list()),
                saved_ids=cookbook.list(),
            )
        return render_template(
            "index.html",
            recipes=collection.recipes,
            saved_ids=cookbook.list(),
            no_matches=NO_MATCHES,
        )

    @app.get("/recipe/<recipe_id>")
    def detail(recipe_id: str):
        recipe = collection.by_id.get(recipe_id)
        if not recipe:
            abort(404)
        template = "tv_detail.html" if tv_requested() else "detail.html"
        return render_template(
            template, recipe=recipe, saved=recipe_id in cookbook
        )

    @app.get("/api/recipes")
    def recipes_api():
        return jsonify(filter_recipes(collection.recipes, request.args.get("q")))

    @app.get("/api/recipes/<recipe_id>")
    def recipe_api(recipe_id: str):
        recipe = collection.by_id.get(recipe_id)
        if not recipe:
            return jsonify({"error": UNKNOWN_RECIPE}), 404
        return jsonify(recipe)

    @app.get("/api/cookbook")
    def get_cookbook():
        return jsonify(cookbook.saved_recipes())

    @app.post("/api/cookbook")
    def add_to_cookbook():
        recipe_id = (request.get_json(silent=True) or {}).get("id")
        try:
            saved = cookbook.add(recipe_id)
        except UnknownRecipeError:
            return jsonify({"error": UNKNOWN_RECIPE}), 400
        except TypeError:  # unhashable id, e.g. a JSON list
            return jsonify({"error": UNKNOWN_RECIPE}), 400
        return jsonify({"recipe_ids": saved}), 201

    @app.delete("/api/cookbook/<recipe_id>")
    def remove_from_cookbook(recipe_id: str):
        return jsonify({"recipe_ids": cookbook.remove(recipe_id)})

    @app.get("/api/rails")
    def rails_api():
        return jsonify(
            [
                {key: value for key, value in rail.items() if key != "recipes"}
                for rail in build_rails(collection, cookbook.list())
            ]
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
