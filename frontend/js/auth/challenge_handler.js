/**
 * challenge_handler.js — Knowledge-Provenance Challenge Orchestrator
 *
 * Language principle: Async/await over callbacks. Single responsibility:
 * coordinate the challenge→answer→authenticate flow with the agent mesh.
 */

import { TokenManager } from './token_manager.js';

export const ChallengeHandler = {
  currentChallenge: null,
  onChallengeReceived: null,
  onAuthSuccess: null,
  onAuthFailed: null,

  receiveChallenge(challenge) {
    this.currentChallenge = challenge;
    if (this.onChallengeReceived) {
      this.onChallengeReceived(challenge);
    }
  },

  buildAnswerPayload(answer, behavioralProfile) {
    if (!this.currentChallenge) {
      throw new Error('No active challenge');
    }
    return {
      action: 'auth_answer',
      challenge_id: this.currentChallenge.id,
      answer,
      behavioral_profile: behavioralProfile,
      request_id: `auth_${Date.now()}`,
    };
  },

  handleAuthSuccess(response) {
    TokenManager.save(response.token, response.capabilities, response.expires);
    this.currentChallenge = null;
    if (this.onAuthSuccess) {
      this.onAuthSuccess(response);
    }
  },

  handleAuthFailed(response) {
    this.currentChallenge = null;
    if (this.onAuthFailed) {
      this.onAuthFailed(response.reason || 'Authentication failed');
    }
  },

  handleRechallenge(reason) {
    TokenManager.clear();
    this.currentChallenge = null;
    if (this.onAuthFailed) {
      this.onAuthFailed(reason);
    }
  },
};
