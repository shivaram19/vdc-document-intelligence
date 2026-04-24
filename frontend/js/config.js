// Agent-driven VDC — No APIs. Pure WebSocket event bridge.
const WS_URL = (typeof window !== 'undefined')
  ? (window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host + '/ws'
  : 'ws://localhost:8765/ws';
const API_KEY_STORAGE = 'vdc_api_key';

export function getApiKey() { return localStorage.getItem(API_KEY_STORAGE) || ''; }
export function setApiKey(key) { localStorage.setItem(API_KEY_STORAGE, key); }
export function clearApiKey() { localStorage.removeItem(API_KEY_STORAGE); }

export { WS_URL };
