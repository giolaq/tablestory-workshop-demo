import {initialFocus, moveFocus} from './tv-logic.js';

const rails = [...document.querySelectorAll('.rail')].map((rail) => [
  ...rail.querySelectorAll('.tv-card'),
]);
const railLengths = rails.map((cards) => cards.length);

let position = initialFocus(railLengths);

function cardAt({rail, card}) {
  return rails[rail]?.[card];
}

function focusCurrent() {
  const card = position && cardAt(position);
  if (!card) return;
  card.focus({preventScroll: true});
  card.scrollIntoView({block: 'nearest', inline: 'nearest', behavior: 'smooth'});
}

if (position) focusCurrent();

document.addEventListener('keydown', (event) => {
  if (!position) return;

  if (event.key === 'Enter') {
    event.preventDefault();
    cardAt(position)?.click();
    return;
  }

  const next = moveFocus(position, event.key, railLengths);
  if (next === position) return;
  event.preventDefault();
  position = next;
  focusCurrent();
});
