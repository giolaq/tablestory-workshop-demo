"""End-to-end checks for the TableStory pages, APIs and television mode."""

import re

import pytest

from app import wants_tv
from rails import RAIL_NAMES
from recipe_data import load_recipes

RECIPE_ID = "golden-oat-porridge"
RECIPE_TITLE = "Golden Oat Porridge"

# Terminology the rebrand forbids in customer-visible output (PRD brand direction).
BANNED_TERMS = (
    "pocket cinema",
    "movie",
    "film",
    "cinema",
    "watchlist",
    "poster",
    "runtime",
    "rating",
    "genre",
)

TV_USER_AGENT = "Mozilla/5.0 (Linux; Android 9; AFTKA) AppleWebKit/537.36"
PHONE_USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"


@pytest.fixture()
def collection():
    return load_recipes()


def assert_recipe_terminology(html: str) -> None:
    lowered = html.lower()
    for term in BANNED_TERMS:
        assert term not in lowered, f"customer-visible output still contains {term!r}"


# ---------- Browse ----------


def test_home_renders_the_tablestory_brand_and_every_recipe(client, collection):
    home = client.get("/")
    assert home.status_code == 200
    body = home.data.decode()
    assert "TableStory" in body
    assert "Good food, clearly told." in body
    assert body.count('class="recipe-card"') == len(collection.recipes)
    assert_recipe_terminology(body)


def test_cards_show_total_time_difficulty_labels_and_a_detail_link(client):
    body = client.get("/").data.decode()
    card = re.search(
        r'<article class="recipe-card".*?</article>', body, re.S
    ).group(0)
    assert "/recipe/golden-oat-porridge" in card
    assert "15 min" in card  # prep 5 + cook 10
    assert "Easy" in card
    assert "Breakfast" in card
    assert "My Cookbook" in card


def test_home_reports_the_recipe_count_and_carries_the_empty_state(client, collection):
    body = client.get("/").data.decode()
    assert f"{len(collection.recipes)} recipes" in body
    assert "No recipes found. Try another ingredient or dish." in body


# ---------- Detail ----------


def test_recipe_detail_shows_metadata_ingredients_and_ordered_steps(client, collection):
    recipe = collection.by_id[RECIPE_ID]
    response = client.get(f"/recipe/{RECIPE_ID}")
    assert response.status_code == 200
    body = response.data.decode()

    assert RECIPE_TITLE in body
    assert recipe["description"] in body
    assert recipe["category"] in body
    for tag in recipe["dietary_tags"]:
        assert tag in body
    assert f"{recipe['prep_minutes']} min" in body
    assert f"{recipe['cook_minutes']} min" in body
    assert recipe["difficulty"] in body
    assert str(recipe["servings"]) in body

    for ingredient in recipe["ingredients"]:
        assert ingredient in body
    positions = [body.index(step) for step in recipe["steps"]]
    assert positions == sorted(positions), "steps must render in stored order"
    assert body.index("<ol>") < positions[0], "steps must be a numbered list"
    assert_recipe_terminology(body)


def test_detail_offers_a_cookbook_control_and_a_way_back(client):
    body = client.get(f"/recipe/{RECIPE_ID}").data.decode()
    assert f"Add {RECIPE_TITLE} to My Cookbook" in body
    assert 'aria-pressed="false"' in body
    assert 'class="back" href="/"' in body


def test_detail_reflects_the_saved_state_in_its_label(client):
    client.post("/api/cookbook", json={"id": RECIPE_ID})
    body = client.get(f"/recipe/{RECIPE_ID}").data.decode()
    assert f"Remove {RECIPE_TITLE} from My Cookbook" in body
    assert 'aria-pressed="true"' in body


def test_unknown_recipe_page_is_not_found(client):
    assert client.get("/recipe/does-not-exist").status_code == 404


# ---------- Recipe collection API ----------


def test_collection_endpoint_returns_every_recipe(client, collection):
    payload = client.get("/api/recipes").get_json()
    assert [recipe["id"] for recipe in payload] == [
        recipe["id"] for recipe in collection.recipes
    ]


@pytest.mark.parametrize(
    "query, expected_id",
    [
        ("PORRIDGE", RECIPE_ID),  # title, case-insensitive
        ("rolled oats", RECIPE_ID),  # ingredient text
        ("dessert", "dark-chocolate-mousse"),  # category
        ("vegan", "sunrise-berry-smoothie-bowl"),  # dietary tag
    ],
)
def test_collection_search_spans_the_recipe_fields(client, query, expected_id):
    ids = [recipe["id"] for recipe in client.get(f"/api/recipes?q={query}").get_json()]
    assert expected_id in ids


def test_blank_query_restores_everything_and_a_miss_returns_nothing(client, collection):
    assert len(client.get("/api/recipes?q=").get_json()) == len(collection.recipes)
    assert client.get("/api/recipes?q=zzzz-not-a-dish").get_json() == []


def test_one_recipe_lookup_and_its_missing_recipe_error(client):
    assert client.get(f"/api/recipes/{RECIPE_ID}").get_json()["title"] == RECIPE_TITLE
    missing = client.get("/api/recipes/does-not-exist")
    assert missing.status_code == 404
    assert missing.get_json() == {"error": "Recipe not found"}


def test_retired_endpoints_are_gone(client):
    for path in ("/api/movies", "/api/movies/golden-oat-porridge", "/api/watchlist"):
        assert client.get(path).status_code == 404
    assert client.get("/movie/golden-oat-porridge").status_code == 404


# ---------- My Cookbook ----------


def test_cookbook_round_trip(client):
    assert client.get("/api/cookbook").get_json() == []

    added = client.post("/api/cookbook", json={"id": RECIPE_ID})
    assert added.status_code == 201
    assert added.get_json() == {"recipe_ids": [RECIPE_ID]}

    saved = client.get("/api/cookbook").get_json()
    assert [recipe["id"] for recipe in saved] == [RECIPE_ID]
    assert saved[0]["ingredients"], "saved entries are complete recipe objects"

    removed = client.delete(f"/api/cookbook/{RECIPE_ID}")
    assert removed.get_json() == {"recipe_ids": []}


def test_saving_an_unknown_recipe_is_rejected_with_a_recipe_error(client):
    response = client.post("/api/cookbook", json={"id": "does-not-exist"})
    assert response.status_code == 400
    assert response.get_json() == {"error": "Recipe not found"}


def test_removing_an_absent_recipe_still_succeeds(client):
    assert client.delete("/api/cookbook/does-not-exist").status_code == 200


# ---------- Rails ----------


def test_rails_endpoint_names_every_rail_and_uses_recipe_ids(client):
    rails = client.get("/api/rails").get_json()
    assert [rail["name"] for rail in rails] == list(RAIL_NAMES)
    for rail in rails:
        assert "recipe_ids" in rail
        assert "movie_ids" not in rail
    for rail in rails[:-1]:
        assert len(rail["recipe_ids"]) >= 2, f"{rail['name']} needs at least two recipes"


def test_cookbook_rail_follows_the_saved_collection(client):
    client.post("/api/cookbook", json={"id": RECIPE_ID})
    rails = client.get("/api/rails").get_json()
    assert rails[-1]["name"] == "My Cookbook"
    assert rails[-1]["recipe_ids"] == [RECIPE_ID]


# ---------- Television mode ----------


@pytest.mark.parametrize(
    "mode, user_agent, expected",
    [
        ("tv", None, True),
        ("TV", None, True),
        (None, TV_USER_AGENT, True),
        (None, "Mozilla/5.0 (SMART-TV; Linux; Tizen 6.0)", True),
        (None, PHONE_USER_AGENT, False),
        (None, None, False),
        ("mobile", TV_USER_AGENT, False),  # an explicit mode always wins
    ],
)
def test_tv_mode_detection(mode, user_agent, expected):
    assert wants_tv(mode, user_agent) is expected


def test_tv_browse_renders_the_four_named_rails(client):
    body = client.get("/?mode=tv").data.decode()
    for name in RAIL_NAMES:
        assert name in body
    assert body.count('class="rail"') == len(RAIL_NAMES)
    assert "No saved recipes yet." in body  # empty My Cookbook rail
    assert_recipe_terminology(body)


def test_tv_cards_are_focusable_and_keep_tv_mode_in_their_links(client):
    body = client.get("/?mode=tv").data.decode()
    assert 'class="tv-card"' in body
    assert 'tabindex="-1"' in body
    assert f"/recipe/{RECIPE_ID}?mode=tv" in body
    assert "tv.js" in body


def test_a_tv_user_agent_gets_the_tv_browse_page_without_a_query(client):
    body = client.get("/", headers={"User-Agent": TV_USER_AGENT}).data.decode()
    assert 'class="rail"' in body


def test_tv_detail_exposes_back_and_cookbook_actions(client):
    body = client.get(f"/recipe/{RECIPE_ID}?mode=tv").data.decode()
    assert body.count("data-action=") == 2
    assert 'href="/?mode=tv"' in body
    assert f"Add {RECIPE_TITLE} to My Cookbook" in body
    assert 'data-browse-url="/?mode=tv"' in body
    assert "tv-detail.js" in body
    assert_recipe_terminology(body)


def test_tv_detail_keeps_the_ingredients_and_method_on_the_page(client, collection):
    recipe = collection.by_id[RECIPE_ID]
    body = client.get(f"/recipe/{RECIPE_ID}?mode=tv").data.decode()
    for ingredient in recipe["ingredients"]:
        assert ingredient in body
    for step in recipe["steps"]:
        assert step in body
