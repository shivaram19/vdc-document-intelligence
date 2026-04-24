/**
 * auth_middleware.js — WebSocket Auth Attachment Layer
 *
 * Language principle: Functional composition. Every outbound message gets
 * token + behavioral profile injected without mutating the original message.
 */

import { TokenManager } from './token_manager.js';

export const AuthMiddleware = {
  getBehavioralProfile: null, // injected by caller

  attach(msg) {
    const token = TokenManager.getToken();
    if (token) {
      msg.token = token;
    }
    if (this.getBehavioralProfile) {
      msg.behavioral_profile = this.getBehavioralProfile();
    }
    return msg;
  },

  isAuthenticated() {
    return TokenManager.getToken() && !TokenManager.isExpired();
  },

  needsCapability(action) {
    const CAP_MAP = {
      query: 'can_query',
      rfi: 'can_draft_rfi',
      scan: 'can_scan_contradictions',
      ingest: 'can_upload',
      create_project: 'can_manage_projects',
    };
    const required = CAP_MAP[action];
    if (!required) return true;
    return TokenManager.hasCapability(required);
  },
};
