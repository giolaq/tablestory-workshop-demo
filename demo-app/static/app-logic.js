// Pure browse-page helpers: client search parity, My Cookbook toggling and copy.

export function matchesRecipe(haystack, query) {
  return haystack.toLocaleLowerCase().includes(query.trim().toLocaleLowerCase());
}

// Toggle a recipe in My Cookbook, preserving the saved (insertion) order the
// server store uses so client and server agree on the collection.
export function nextCookbook(current, id) {
  return current.includes(id) ? current.filter((saved) => saved !== id) : [...current, id];
}

export function recipeCountLabel(count) {
  return `${count} recipe${count === 1 ? '' : 's'}`;
}

export function cookbookActionLabel(title, saved) {
  return saved ? `Remove ${title} from My Cookbook` : `Add ${title} to My Cookbook`;
}
