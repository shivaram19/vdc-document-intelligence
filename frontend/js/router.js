// Simple hash-based router
const routes = {};

export function register(path, renderFn) {
  routes[path] = renderFn;
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

  const renderFn = routes[path] || routes['/'];
  if (renderFn) {
    outlet.innerHTML = '';
    renderFn(outlet);
  }
}

// Render initial route on load (not just on hashchange)
if (typeof window !== 'undefined') {
  window.addEventListener('DOMContentLoaded', renderCurrentRoute);
  window.addEventListener('hashchange', renderCurrentRoute);
}
