import test from 'node:test';
import assert from 'node:assert/strict';
import {initialFocus, moveFocus, nextActionIndex} from '../tv-logic.js';

// Popular, Ready in 30, Vegetarian, My Cookbook (empty until something is saved).
const RAILS = [4, 9, 6, 0];

test('focus starts on the first recipe of the first populated rail', () => {
  assert.deepEqual(initialFocus(RAILS), {rail: 0, card: 0});
  assert.deepEqual(initialFocus([0, 0, 3]), {rail: 2, card: 0});
  assert.equal(initialFocus([0, 0]), null);
});

test('left and right move within a rail and stop at its ends', () => {
  assert.deepEqual(moveFocus({rail: 0, card: 0}, 'ArrowRight', RAILS), {rail: 0, card: 1});
  assert.deepEqual(moveFocus({rail: 0, card: 1}, 'ArrowLeft', RAILS), {rail: 0, card: 0});
  assert.deepEqual(moveFocus({rail: 0, card: 0}, 'ArrowLeft', RAILS), {rail: 0, card: 0});
  assert.deepEqual(moveFocus({rail: 0, card: 3}, 'ArrowRight', RAILS), {rail: 0, card: 3});
});

test('up and down move between rails and keep the nearest card position', () => {
  assert.deepEqual(moveFocus({rail: 0, card: 2}, 'ArrowDown', RAILS), {rail: 1, card: 2});
  assert.deepEqual(moveFocus({rail: 1, card: 2}, 'ArrowUp', RAILS), {rail: 0, card: 2});
  // A shorter destination rail clamps to its last recipe rather than losing focus.
  assert.deepEqual(moveFocus({rail: 1, card: 8}, 'ArrowUp', RAILS), {rail: 0, card: 3});
});

test('vertical movement skips empty rails and holds at the edges', () => {
  assert.deepEqual(moveFocus({rail: 2, card: 0}, 'ArrowDown', RAILS), {rail: 2, card: 0});
  assert.deepEqual(moveFocus({rail: 0, card: 0}, 'ArrowUp', RAILS), {rail: 0, card: 0});
  assert.deepEqual(moveFocus({rail: 0, card: 1}, 'ArrowDown', [4, 0, 6, 0]), {
    rail: 2,
    card: 1,
  });
});

test('unhandled keys leave the focus position untouched', () => {
  const position = {rail: 1, card: 3};
  assert.equal(moveFocus(position, 'Enter', RAILS), position);
  assert.equal(moveFocus(position, 'a', RAILS), position);
});

test('detail actions step vertically and clamp at both ends', () => {
  assert.equal(nextActionIndex(0, 'ArrowDown', 2), 1);
  assert.equal(nextActionIndex(1, 'ArrowDown', 2), 1);
  assert.equal(nextActionIndex(1, 'ArrowUp', 2), 0);
  assert.equal(nextActionIndex(0, 'ArrowUp', 2), 0);
  assert.equal(nextActionIndex(0, 'ArrowRight', 2), 0);
  assert.equal(nextActionIndex(0, 'ArrowDown', 0), 0);
});
