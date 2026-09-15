import {nextActionIndex} from './tv-logic.js';
import {bindCookbookToggles} from './cookbook-ui.js';

const actions = [...document.querySelectorAll('.tv-action')];
const browseUrl = document.body.dataset.browseUrl ?? '/?mode=tv';

let index = 0;

function focusCurrent() {
  const action = actions[index];
  action?.focus({preventScroll: true});
  action?.scrollIntoView({block: 'nearest', behavior: 'smooth'});
}

bindCookbookToggles();
if (actions.length) focusCurrent();

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' || event.key === 'Backspace') {
    event.preventDefault();
    window.location.assign(browseUrl);
    return;
  }

  if (event.key === 'Enter') {
    event.preventDefault();
    actions[index]?.click();
    return;
  }

  const next = nextActionIndex(index, event.key, actions.length);
  if (next === index) return;
  event.preventDefault();
  index = next;
  focusCurrent();
});
