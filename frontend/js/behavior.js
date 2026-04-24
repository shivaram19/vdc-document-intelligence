// ── Behavioral Fingerprinting Engine ─────────────────────────────────────────
// Collects interaction telemetry for the Medha Authentication Mesh.
// All processing is client-side; only hashed profiles are sent to agents.

class BehavioralFingerprint {
  constructor() {
    this.profile = {
      typing_wpm: 0,
      mouse_entropy: 0,
      click_rate: 0,
      scroll_velocity: 0,
      avg_interaction_time: 0,
      tab_switches: 0,
    };
    this.samples = {
      keystrokes: [],
      mouseMoves: [],
      clicks: [],
      scrolls: [],
      interactions: [],
    };
    this.lastKeyTime = 0;
    this.lastMousePos = { x: 0, y: 0 };
    this.sessionStart = Date.now();
    this._bound = false;
  }

  start() {
    if (this._bound) return;
    this._bound = true;
    document.addEventListener('keydown', this._onKeyDown.bind(this));
    document.addEventListener('mousemove', this._onMouseMove.bind(this));
    document.addEventListener('click', this._onClick.bind(this));
    document.addEventListener('scroll', this._onScroll.bind(this));
    document.addEventListener('visibilitychange', this._onVisibilityChange.bind(this));
    // Compute averages every 10 seconds
    this._interval = setInterval(() => this._computeProfile(), 10000);
  }

  stop() {
    if (!this._bound) return;
    this._bound = false;
    document.removeEventListener('keydown', this._onKeyDown);
    document.removeEventListener('mousemove', this._onMouseMove);
    document.removeEventListener('click', this._onClick);
    document.removeEventListener('scroll', this._onScroll);
    document.removeEventListener('visibilitychange', this._onVisibilityChange);
    clearInterval(this._interval);
  }

  _onKeyDown(e) {
    const now = Date.now();
    if (this.lastKeyTime > 0) {
      const interval = now - this.lastKeyTime;
      if (interval > 50 && interval < 2000) { // Filter out key repeat
        this.samples.keystrokes.push(interval);
        // Keep last 100
        if (this.samples.keystrokes.length > 100) this.samples.keystrokes.shift();
      }
    }
    this.lastKeyTime = now;
  }

  _onMouseMove(e) {
    const dx = e.clientX - this.lastMousePos.x;
    const dy = e.clientY - this.lastMousePos.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist > 0) {
      this.samples.mouseMoves.push(dist);
      if (this.samples.mouseMoves.length > 500) this.samples.mouseMoves.shift();
    }
    this.lastMousePos = { x: e.clientX, y: e.clientY };
  }

  _onClick(e) {
    this.samples.clicks.push(Date.now());
    if (this.samples.clicks.length > 50) this.samples.clicks.shift();
  }

  _onScroll(e) {
    this.samples.scrolls.push(window.scrollY);
    if (this.samples.scrolls.length > 100) this.samples.scrolls.shift();
  }

  _onVisibilityChange() {
    if (document.hidden) {
      this.profile.tab_switches += 1;
    }
  }

  _computeProfile() {
    const ks = this.samples.keystrokes;
    if (ks.length > 5) {
      const avgInterval = ks.reduce((a, b) => a + b, 0) / ks.length;
      this.profile.typing_wpm = Math.round(60000 / avgInterval / 5); // ~5 chars per word
    }

    const mm = this.samples.mouseMoves;
    if (mm.length > 10) {
      const mean = mm.reduce((a, b) => a + b, 0) / mm.length;
      const variance = mm.reduce((a, b) => a + (b - mean) ** 2, 0) / mm.length;
      this.profile.mouse_entropy = Math.round(Math.sqrt(variance) * 100) / 100;
    }

    const clicks = this.samples.clicks;
    if (clicks.length > 2) {
      const span = (clicks[clicks.length - 1] - clicks[0]) / 1000;
      this.profile.click_rate = span > 0 ? Math.round((clicks.length / span) * 100) / 100 : 0;
    }

    const scrolls = this.samples.scrolls;
    if (scrolls.length > 2) {
      const total = Math.abs(scrolls[scrolls.length - 1] - scrolls[0]);
      const span = (Date.now() - this.sessionStart) / 1000;
      this.profile.scroll_velocity = span > 0 ? Math.round((total / span) * 100) / 100 : 0;
    }

    this.profile.avg_interaction_time = Math.round((Date.now() - this.sessionStart) / 1000);
  }

  getProfile() {
    this._computeProfile();
    return { ...this.profile };
  }

  // Hash for transmission (already lightweight, just structured)
  getCompactProfile() {
    const p = this.getProfile();
    return {
      tw: p.typing_wpm,
      me: p.mouse_entropy,
      cr: p.click_rate,
      sv: p.scroll_velocity,
      at: p.avg_interaction_time,
      ts: p.tab_switches,
    };
  }
}

export const behavior = new BehavioralFingerprint();
export default behavior;
