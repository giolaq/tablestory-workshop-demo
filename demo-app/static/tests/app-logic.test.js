import test from 'node:test';
import assert from 'node:assert/strict';
import {
  cookbookActionLabel,
  matchesRecipe,
  nextCookbook,
  recipeCountLabel,
} from '../app-logic.js';

const HAYSTACK = 'Golden Oat Porridge Breakfast Vegetarian rolled oats whole milk';

test('recipe matching ignores case and surrounding whitespace', () => {
  assert.equal(matchesRecipe(HAYSTACK, '  ROLLED oats '), true);
  assert.equal(matchesRecipe(HAYSTACK, 'Vegetarian'), true);
  assert.equal(matchesRecipe(HAYSTACK, 'salmon'), false);
});

test('an empty query matches every recipe, as the server search does', () => {
  assert.equal(matchesRecipe(HAYSTACK, ''), true);
  assert.equal(matchesRecipe(HAYSTACK, '   '), true);
});

test('cookbook toggling keeps saved order and is reversible', () => {
  assert.deepEqual(nextCookbook(['plums'], 'mousse'), ['plums', 'mousse']);
  assert.deepEqual(nextCookbook(['plums', 'mousse'], 'plums'), ['mousse']);
});

test('the recipe count label is singular for exactly one recipe', () => {
  assert.equal(recipeCountLabel(0), '0 recipes');
  assert.equal(recipeCountLabel(1), '1 recipe');
  assert.equal(recipeCountLabel(13), '13 recipes');
});

test('the cookbook action label names the recipe and the direction', () => {
  assert.equal(
    cookbookActionLabel('Honey Roast Plums', false),
    'Add Honey Roast Plums to My Cookbook',
  );
  assert.equal(
    cookbookActionLabel('Honey Roast Plums', true),
    'Remove Honey Roast Plums from My Cookbook',
  );
});
