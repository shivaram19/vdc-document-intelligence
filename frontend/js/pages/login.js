import { navigate } from '../router.js';
import { requestChallenge, submitAnswer, onWsEvent } from '../ws.js';
import { createFingerprint } from '../auth/index.js';

/**
 * login.js — Knowledge-Provenance Authentication Portal
 *
 * [CITE: FathimaSaravanan2024] Knowledge-based challenges from user-specific
 * documents achieve 99.7% accuracy with 0.3% error rate.
 * [CITE: MondalBours2015] Behavioral biometrics: 0.5% FAR, 2.1% FRR.
 *
 * UX: The challenge feels like proving project knowledge, not memorizing a password.
 */

let fingerprint = null;

export function renderLogin(container) {
  container.innerHTML = `
    <div class="min-h-screen flex items-center justify-center p-4 blueprint-bg">
      <div class="card-structural max-w-md w-full p-8 border border-bp-light/30">
        <div class="text-center mb-6">
          <div class="w-12 h-12 rounded-sm bg-bp-accent flex items-center justify-center text-white font-bold text-xl mx-auto mb-4">M</div>
          <h1 class="text-2xl font-bold text-white font-mono">AUTHENTICATION MESH</h1>
          <p class="text-sm text-gray-500 mt-2 font-mono">NO PASSWORDS. PROJECT-KNOWLEDGE PROOF.</p>
        </div>

        <div id="auth-flow">
          <div id="auth-step-request" class="text-center">
            <p class="text-sm text-gray-400 mb-4">The fleet will ask a question based on your project documents. Only someone with legitimate access can answer correctly.</p>
            <button id="btn-request-challenge" class="w-full px-4 py-3 bg-bp-accent hover:bg-blue-500 text-white font-semibold rounded-sm transition font-mono">
              <i class="fas fa-shield-alt mr-2"></i> REQUEST CHALLENGE
            </button>
            <div class="mt-4 flex justify-center gap-4 text-[10px] text-gray-600 font-mono">
              <span><i class="fas fa-lock mr-1"></i>KNOWLEDGE</span>
              <span><i class="fas fa-fingerprint mr-1"></i>BEHAVIORAL</span>
              <span><i class="fas fa-network-wired mr-1"></i>CONSENSUS</span>
            </div>
          </div>

          <div id="auth-step-answer" class="hidden">
            <div class="mb-4">
              <span class="badge-info text-[10px]">
                <i class="fas fa-brain mr-1"></i>KNOWLEDGE-PROVENANCE CHALLENGE
              </span>
            </div>
            <p id="challenge-question" class="text-sm text-gray-200 mb-2 font-medium font-mono"></p>
            <p id="challenge-hint" class="text-xs text-gray-600 mb-4 font-mono"></p>
            <div class="flex gap-3">
              <input id="challenge-answer" type="text" placeholder="Your answer..."
                class="flex-1 bg-bp-dark border border-bp-light/50 text-white text-sm rounded-sm px-4 py-3 focus:outline-none focus:border-bp-accent font-mono">
              <button id="btn-submit-answer" class="px-5 py-3 bg-bp-accent hover:bg-blue-500 text-white rounded-sm transition">
                <i class="fas fa-arrow-right"></i>
              </button>
            </div>
            <p id="auth-error" class="text-xs text-safe-red mt-3 hidden font-mono"></p>
          </div>

          <div id="auth-step-success" class="hidden text-center">
            <i class="fas fa-check-circle text-safe-green text-4xl mb-3"></i>
            <h3 class="text-lg font-semibold text-white mb-1 font-mono">AUTHENTICATED</h3>
            <p class="text-sm text-gray-500 mb-4">Agent mesh verified identity via knowledge proof + behavioral fingerprint.</p>
            <button id="btn-enter-dashboard" class="px-6 py-3 bg-safe-green hover:bg-green-600 text-white font-semibold rounded-sm transition font-mono">
              <i class="fas fa-clipboard-check mr-2"></i> ENTER DASHBOARD
            </button>
          </div>
        </div>

        <div class="mt-6 pt-4 border-t border-bp-light/20 text-center">
          <p class="text-[10px] text-gray-600 font-mono">3-FACTOR AGENTIC AUTH: KNOWLEDGE-PROVENANCE + BEHAVIORAL FP + AGENT ATTESTATION</p>
        </div>
      </div>
    </div>
  `;

  wireLoginEvents();
  startFingerprinting();
}

function wireLoginEvents() {
  document.getElementById('btn-request-challenge')?.addEventListener('click', () => {
    requestChallenge('default', 'medium');
    showStep('auth-step-answer');
    document.getElementById('challenge-answer')?.focus();
  });

  document.getElementById('btn-submit-answer')?.addEventListener('click', submitChallengeAnswer);
  document.getElementById('challenge-answer')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') submitChallengeAnswer();
  });

  document.getElementById('btn-enter-dashboard')?.addEventListener('click', () => {
    navigate('/dashboard');
  });

  onWsEvent((ev) => {
    if (ev.type === 'auth_challenge') {
      const qEl = document.getElementById('challenge-question');
      const hEl = document.getElementById('challenge-hint');
      if (qEl) qEl.textContent = ev.question || 'Loading challenge...';
      if (hEl) hEl.textContent = ev.hint || '';
    }
    if (ev.type === 'auth_failed') {
      const errEl = document.getElementById('auth-error');
      if (errEl) {
        errEl.textContent = ev.reason || 'Incorrect answer. Try again.';
        errEl.classList.remove('hidden');
      }
      requestChallenge('default', 'medium');
    }
    if (ev.type === 'auth_success') {
      showStep('auth-step-success');
      stopFingerprinting();
    }
  });
}

function submitChallengeAnswer() {
  const input = document.getElementById('challenge-answer');
  const answer = input?.value.trim();
  if (!answer) return;
  const profile = fingerprint ? fingerprint.getCompactProfile() : {};
  submitAnswer(null, answer, profile);
  const errEl = document.getElementById('auth-error');
  if (errEl) errEl.classList.add('hidden');
}

function showStep(stepId) {
  ['auth-step-request', 'auth-step-answer', 'auth-step-success'].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.classList.add('hidden');
  });
  const target = document.getElementById(stepId);
  if (target) target.classList.remove('hidden');
}

function startFingerprinting() {
  if (!fingerprint) fingerprint = createFingerprint();
  fingerprint.start();
}
function stopFingerprinting() {
  if (fingerprint) fingerprint.stop();
}
