// Simple hash-based router with parameterized route support
const routes = {};
const paramRoutes = [];

export function register(path, renderFn) {
  if (path.includes(':')) {
    const regex = new RegExp('^' + path.replace(/:([^/]+)/g, '([^/]+)') + '$');
    const keys = (path.match(/:([^/]+)/g) || []).map((k) => k.slice(1));
    paramRoutes.push({ regex, keys, renderFn });
  } else {
    routes[path] = renderFn;
  }
}

export function navigate(path) {
  window.location.hash = path;
}

export function currentRoute() {
  return window.location.hash.replace('#', '') || '/';
}

export function renderCurrentRoute() {
  const path = currentRoute();
  const outlet = document.getElementById('app-outlet');
  if (!outlet) return;

  // Check exact match first
  const exactFn = routes[path];
  if (exactFn) {
    outlet.innerHTML = '';
    exactFn(outlet);
    return;
  }

  // Check parameterized routes
  for (const pr of paramRoutes) {
    const match = path.match(pr.regex);
    if (match) {
      const params = {};
      pr.keys.forEach((key, i) => { params[key] = match[i + 1]; });
      outlet.innerHTML = '';
      pr.renderFn(outlet, params);
      return;
    }
  }

  // Fallback to home
  const fallback = routes['/'];
  if (fallback) {
    outlet.innerHTML = '';
    fallback(outlet);
  }
}

// Render initial route on load (not just on hashchange)
if (typeof window !== 'undefined') {
  window.addEventListener('DOMContentLoaded', renderCurrentRoute);
  window.addEventListener('hashchange', renderCurrentRoute);
}
