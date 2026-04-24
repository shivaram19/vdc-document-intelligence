import { WS_URL } from './config.js';
import { TokenManager } from './auth/token_manager.js';
import { AuthMiddleware } from './auth/auth_middleware.js';
import { ChallengeHandler } from './auth/challenge_handler.js';

/**
 * ws.js — WebSocket Agent Bridge Client
 *
 * Research basis for design:
 *   - Fathima & Saravanan (2024): Continuous auth requires persistent
 *     connection with periodic re-verification. WebSocket > polling.
 *   - Mondal & Bours (2015): Trust function must update on every
 *     user action, not just login. Hence behavioral_profile sent
 *     with every message.
 *   - SOLID-D (Dependency Inversion): This module depends on
 *     AuthMiddleware abstraction, not concrete auth logic.
 */

let ws = null;
let reconnectTimer = null;
let msgQueue = [];
let pendingRequests = new Map();
let listeners = [];
let getBehavioralProfile = null;

export const wsState = {
  connected: false,
  connecting: false,
  authenticated: false,
  lastError: null,
};

export function onWsEvent(fn) {
  listeners.push(fn);
  return () => { listeners = listeners.filter((l) => l !== fn); };
}

function emit(event) {
  listeners.forEach((fn) => {
    try { fn(event); } catch (e) { console.error(e); }
  });
}

export function setBehavioralProfileGetter(fn) {
  getBehavioralProfile = fn;
  AuthMiddleware.getBehavioralProfile = fn;
}

export function connect() {
  if (ws?.readyState === WebSocket.OPEN || wsState.connecting) return;
  wsState.connecting = true;
  wsState.lastError = null;

  try {
    ws = new WebSocket(WS_URL);
  } catch (e) {
    wsState.lastError = e.message;
    wsState.connecting = false;
    scheduleReconnect();
    return;
  }

  ws.onopen = () => {
    wsState.connected = true;
    wsState.connecting = false;
    console.log('[ws] Connected to agent fleet');
    emit({ type: 'ws_connected' });
  };

  ws.onmessage = (ev) => {
    try {
      const data = JSON.parse(ev.data);

      // Auth flow interception
      if (data.type === 'auth_required') {
        wsState.authenticated = false;
        emit({ type: 'auth_required', ...data });
        return;
      }
      if (data.type === 'auth_challenge') {
        ChallengeHandler.receiveChallenge(data);
        return;
      }
      if (data.type === 'auth_success') {
        wsState.authenticated = true;
        ChallengeHandler.handleAuthSuccess(data);
        emit({ type: 'auth_success', ...data });
        // Flush queued messages now that we're authenticated
        flushQueue();
        return;
      }
      if (data.type === 'auth_failed') {
        wsState.authenticated = false;
        ChallengeHandler.handleAuthFailed(data);
        emit({ type: 'auth_failed', ...data });
        return;
      }
      if (data.type === 'auth_required' && data.rechallenge) {
        wsState.authenticated = false;
        TokenManager.clear();
        ChallengeHandler.handleRechallenge(data.reason);
        emit({ type: 'rechallenge_required', reason: data.reason });
        return;
      }

      // Resolve pending requests
      if (data.request_id && pendingRequests.has(data.request_id)) {
        const { resolve } = pendingRequests.get(data.request_id);
        pendingRequests.delete(data.request_id);
        resolve(data);
      }
      emit(data);
    } catch (e) {
      console.error('[ws] Parse error:', e);
    }
  };

  ws.onclose = () => {
    wsState.connected = false;
    wsState.connecting = false;
    wsState.authenticated = false;
    console.log('[ws] Disconnected');
    emit({ type: 'ws_disconnected' });
    scheduleReconnect();
  };

  ws.onerror = () => {
    wsState.lastError = 'Connection failed';
    wsState.connected = false;
    wsState.connecting = false;
    emit({ type: 'ws_error', error: wsState.lastError });
  };
}

function scheduleReconnect() {
  if (reconnectTimer) return;
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null;
    connect();
  }, 3000);
}

export function disconnect() {
  if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null; }
  if (ws) { ws.close(); ws = null; }
}

function sendRaw(msg) {
  if (ws?.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(msg));
  } else {
    msgQueue.push(msg);
    if (!wsState.connecting) connect();
  }
}

function flushQueue() {
  while (msgQueue.length) {
    const m = msgQueue.shift();
    sendRaw(m);
  }
}

/**
 * Core send function. Attaches auth middleware (token + behavioral profile)
 * to every message per Mondal & Bours (2015) continuous auth model.
 */
function send(msg) {
  const enriched = AuthMiddleware.attach({ ...msg });
  sendRaw(enriched);
}

export function requestChallenge(project, difficulty = 'medium') {
  sendRaw({ action: 'auth_challenge', project, difficulty, request_id: `auth_ch_${Date.now()}` });
}

export function submitAnswer(challengeId, answer, profile) {
  const payload = ChallengeHandler.buildAnswerPayload(answer, profile);
  sendRaw(payload);
}

export function sendCommand(action, params = {}, awaitResponse = true) {
  const request_id = `req_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
  const msg = { action, request_id, ...params };

  if (!awaitResponse) {
    send(msg);
    return Promise.resolve();
  }

  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      pendingRequests.delete(request_id);
      reject(new Error('Request timeout'));
    }, 60000);
    pendingRequests.set(request_id, {
      resolve: (data) => { clearTimeout(timer); resolve(data); },
      reject: (err) => { clearTimeout(timer); reject(err); },
    });
    send(msg);
  });
}

// Convenience helpers
export const listProjects = () => sendCommand('list_projects', {}, true);
export const createProject = (name, client) => sendCommand('create_project', { name, client }, true);
export const queryProject = (project, query, top_k = 5) => sendCommand('query', { project, query, top_k }, false);
export const draftRFI = (project, question, number) => sendCommand('rfi', { project, question, number }, false);
export const scanContradictions = (project, query = '') => sendCommand('scan', { project, query }, false);
