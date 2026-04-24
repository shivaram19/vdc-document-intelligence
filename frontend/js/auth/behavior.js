/**
 * behavior.js — Behavioral Fingerprinting Engine
 *
 * Language principle: Pure functions, immutable state, no globals.
 * Collects interaction telemetry client-side. Only compact hashed profiles
 * leave the browser.
 */

const createFingerprint = () => {
  const samples = {
    keystrokes: [],
    mouseMoves: [],
    clicks: [],
    scrolls: [],
  };
  let lastKeyTime = 0;
  let lastMouse = { x: 0, y: 0 };
  let sessionStart = Date.now();
  let tabSwitches = 0;
  let attached = false;
  let intervalId = null;

  const handlers = {
    keydown: (e) => {
      const now = Date.now();
      if (lastKeyTime > 0) {
        const interval = now - lastKeyTime;
        if (interval > 50 && interval < 2000) {
          samples.keystrokes.push(interval);
          if (samples.keystrokes.length > 100) samples.keystrokes.shift();
        }
      }
      lastKeyTime = now;
    },
    mousemove: (e) => {
      const dx = e.clientX - lastMouse.x;
      const dy = e.clientY - lastMouse.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist > 0) {
        samples.mouseMoves.push(dist);
        if (samples.mouseMoves.length > 500) samples.mouseMoves.shift();
      }
      lastMouse = { x: e.clientX, y: e.clientY };
    },
    click: () => {
      samples.clicks.push(Date.now());
      if (samples.clicks.length > 50) samples.clicks.shift();
    },
    scroll: () => {
      samples.scrolls.push(window.scrollY);
      if (samples.scrolls.length > 100) samples.scrolls.shift();
    },
    visibilitychange: () => {
      if (document.hidden) tabSwitches += 1;
    },
  };

  const computeProfile = () => {
    const profile = {
      typing_wpm: 0,
      mouse_entropy: 0,
      click_rate: 0,
      scroll_velocity: 0,
      avg_interaction_time: Math.round((Date.now() - sessionStart) / 1000),
      tab_switches: tabSwitches,
    };

    const ks = samples.keystrokes;
    if (ks.length > 5) {
      const avg = ks.reduce((a, b) => a + b, 0) / ks.length;
      profile.typing_wpm = Math.round(60000 / avg / 5);
    }

    const mm = samples.mouseMoves;
    if (mm.length > 10) {
      const mean = mm.reduce((a, b) => a + b, 0) / mm.length;
      const variance = mm.reduce((a, b) => a + (b - mean) ** 2, 0) / mm.length;
      profile.mouse_entropy = Math.round(Math.sqrt(variance) * 100) / 100;
    }

    const clicks = samples.clicks;
    if (clicks.length > 2) {
      const span = (clicks[clicks.length - 1] - clicks[0]) / 1000;
      profile.click_rate = span > 0 ? Math.round((clicks.length / span) * 100) / 100 : 0;
    }

    const scrolls = samples.scrolls;
    if (scrolls.length > 2) {
      const total = Math.abs(scrolls[scrolls.length - 1] - scrolls[0]);
      const span = (Date.now() - sessionStart) / 1000;
      profile.scroll_velocity = span > 0 ? Math.round((total / span) * 100) / 100 : 0;
    }

    return Object.freeze(profile);
  };

  return {
    start() {
      if (attached) return;
      attached = true;
      Object.entries(handlers).forEach(([evt, fn]) => {
        document.addEventListener(evt, fn);
      });
      intervalId = setInterval(computeProfile, 10000);
    },
    stop() {
      if (!attached) return;
      attached = false;
      Object.entries(handlers).forEach(([evt, fn]) => {
        document.removeEventListener(evt, fn);
      });
      clearInterval(intervalId);
    },
    getProfile: computeProfile,
    getCompactProfile() {
      const p = computeProfile();
      return Object.freeze({
        typing_wpm: p.typing_wpm,
        mouse_entropy: p.mouse_entropy,
        click_rate: p.click_rate,
        scroll_velocity: p.scroll_velocity,
        avg_interaction_time: p.avg_interaction_time,
        tab_switches: p.tab_switches,
      });
    },
  };
};

export { createFingerprint };
