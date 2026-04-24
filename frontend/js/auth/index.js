/**
 * auth/index.js — Frontend Authentication Facade
 *
 * Language principle: Barrel export / Facade pattern.
 * External modules import ONLY from this file. Internal auth module
 * structure is hidden. This is the sole dependency surface.
 */

export { createFingerprint } from './behavior.js';
export { TokenManager } from './token_manager.js';
export { ChallengeHandler } from './challenge_handler.js';
export { AuthMiddleware } from './auth_middleware.js';
