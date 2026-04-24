/**
 * token_manager.js — Capability Token Lifecycle Manager
 *
 * Language principle: Encapsulation. No direct localStorage access outside this module.
 * Handles storage, retrieval, expiry checks, and automatic refresh scheduling.
 */

const STORAGE_KEY = 'medha_auth_token';
const CAPS_KEY = 'medha_auth_caps';
const EXPIRES_KEY = 'medha_auth_expires';

export const TokenManager = {
  save(token, capabilities, expiresISO) {
    localStorage.setItem(STORAGE_KEY, token);
    localStorage.setItem(CAPS_KEY, JSON.stringify(capabilities));
    localStorage.setItem(EXPIRES_KEY, expiresISO);
  },

  getToken() {
    return localStorage.getItem(STORAGE_KEY) || '';
  },

  getCapabilities() {
    try {
      return JSON.parse(localStorage.getItem(CAPS_KEY) || '[]');
    } catch {
      return [];
    }
  },

  isExpired() {
    const expires = localStorage.getItem(EXPIRES_KEY);
    if (!expires) return true;
    return new Date(expires) < new Date();
  },

  hasCapability(cap) {
    return this.getCapabilities().includes(cap);
  },

  clear() {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(CAPS_KEY);
    localStorage.removeItem(EXPIRES_KEY);
  },

  timeUntilExpiryMs() {
    const expires = localStorage.getItem(EXPIRES_KEY);
    if (!expires) return 0;
    return Math.max(0, new Date(expires).getTime() - Date.now());
  },
};
