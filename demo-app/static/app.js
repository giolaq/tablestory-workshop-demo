import {matchesRecipe, recipeCountLabel} from './app-logic.js';
import {bindCookbookToggles} from './cookbook-ui.js';

const search = document.querySelector('#search');
const cards = [...document.querySelectorAll('.recipe-card')];

search?.addEventListener('input', () => {
  let visible = 0;
  for (const card of cards) {
    const show = matchesRecipe(card.dataset.search, search.value);
    card.hidden = !show;
    visible += Number(show);
  }
  document.querySelector('#count').textContent = recipeCountLabel(visible);
  document.querySelector('#empty').hidden = visible !== 0;
});

bindCookbookToggles();
