// Shared My Cookbook toggle behaviour for the mobile and TV pages.

import {cookbookActionLabel} from './app-logic.js';

const SAVED_TEXT = '✓ Saved in My Cookbook';
const UNSAVED_TEXT = '+ Add to My Cookbook';

function paint(button, saved) {
  button.classList.toggle('saved', saved);
  button.setAttribute('aria-pressed', String(saved));
  button.setAttribute('aria-label', cookbookActionLabel(button.dataset.recipeTitle, saved));
  const glyph = button.querySelector('span');
  if (glyph) {
    glyph.textContent = saved ? '✓' : '+';
  } else {
    button.textContent = saved ? SAVED_TEXT : UNSAVED_TEXT;
  }
}

async function sync(recipeId, saved) {
  const response = await fetch(saved ? '/api/cookbook' : `/api/cookbook/${recipeId}`, {
    method: saved ? 'POST' : 'DELETE',
    headers: {'Content-Type': 'application/json'},
    body: saved ? JSON.stringify({id: recipeId}) : undefined,
  });
  return response.ok;
}

export function bindCookbookToggles(root = document) {
  for (const button of root.querySelectorAll('.cookbook-toggle')) {
    button.addEventListener('click', async () => {
      const saved = button.getAttribute('aria-pressed') !== 'true';
      paint(button, saved);
      if (!(await sync(button.dataset.recipeId, saved))) {
        paint(button, !saved); // The server refused; show the true state again.
      }
    });
  }
}
