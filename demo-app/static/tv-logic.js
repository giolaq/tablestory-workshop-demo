// Pure focus arithmetic for the TV browse rails and the TV detail actions.
// No DOM access, so the remote-control rules can be tested directly.

const HORIZONTAL = {ArrowLeft: -1, ArrowRight: 1};
const VERTICAL = {ArrowUp: -1, ArrowDown: 1};

/** First focusable position, skipping empty rails; null when nothing is focusable. */
export function initialFocus(railLengths) {
  const rail = railLengths.findIndex((length) => length > 0);
  return rail === -1 ? null : {rail, card: 0};
}

function nearestOccupiedRail(railLengths, from, step) {
  for (let rail = from + step; rail >= 0 && rail < railLengths.length; rail += step) {
    if (railLengths[rail] > 0) return rail;
  }
  return null;
}

/**
 * Next focus position for a rail keypress.
 *
 * Left/Right clamp inside the current rail. Up/Down move to the nearest rail
 * that holds recipes and keep the closest sensible card position. An
 * unhandled key, or a move with nowhere to go, returns the position unchanged.
 */
export function moveFocus(position, key, railLengths) {
  const length = railLengths[position.rail] ?? 0;
  if (length === 0) return position;

  if (key in HORIZONTAL) {
    const card = Math.min(Math.max(position.card + HORIZONTAL[key], 0), length - 1);
    return card === position.card ? position : {rail: position.rail, card};
  }

  if (key in VERTICAL) {
    const rail = nearestOccupiedRail(railLengths, position.rail, VERTICAL[key]);
    if (rail === null) return position;
    return {rail, card: Math.min(position.card, railLengths[rail] - 1)};
  }

  return position;
}

/** Next index in a vertical list of actions, clamped at both ends. */
export function nextActionIndex(current, key, count) {
  if (!(key in VERTICAL) || count === 0) return current;
  return Math.min(Math.max(current + VERTICAL[key], 0), count - 1);
}
