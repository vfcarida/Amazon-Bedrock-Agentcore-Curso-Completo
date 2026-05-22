/**
 * auth.js -- OAuth2 PKCE authentication module for Aria.
 *
 * Handles the full Cognito OAuth2 Authorization Code flow with PKCE:
 *   1. Generate code verifier and challenge
 *   2. Redirect to Cognito Hosted UI
 *   3. Handle callback, exchange code for tokens
 *   4. Store tokens in memory (never localStorage)
 *   5. Auto-refresh tokens before expiry
 *
 * Exports: login, handleCallback, getIdToken, refreshTokens, logout, getUserInfo
 */

// ---------------------------------------------------------------------------
// Configuration -- read from window.ARIA_CONFIG (injected by CDK at deploy)
// ---------------------------------------------------------------------------

const config = window.ARIA_CONFIG || {};
const COGNITO_DOMAIN  = config.COGNITO_DOMAIN  || '';
const CLIENT_ID       = config.CLIENT_ID       || '';
const REDIRECT_URI    = config.REDIRECT_URI    || window.location.origin;
const REGION          = config.REGION          || 'us-east-1';

const AUTHORIZE_URL = `${COGNITO_DOMAIN}/oauth2/authorize`;
const TOKEN_URL     = `${COGNITO_DOMAIN}/oauth2/token`;
const LOGOUT_URL    = `${COGNITO_DOMAIN}/logout`;

// ---------------------------------------------------------------------------
// Token storage -- closure-scoped, never persisted to disk
// ---------------------------------------------------------------------------

let idToken      = null;
let accessToken  = null;
let refreshToken = null;
let tokenExpiry  = 0;  // epoch ms when the id_token expires
let userPayload  = null;

// ---------------------------------------------------------------------------
// PKCE helpers
// ---------------------------------------------------------------------------

function generateCodeVerifier() {
    const array = new Uint8Array(64);
    crypto.getRandomValues(array);
    return base64UrlEncode(array);
}

async function generateCodeChallenge(verifier) {
    const encoder = new TextEncoder();
    const data = encoder.encode(verifier);
    const digest = await crypto.subtle.digest('SHA-256', data);
    return base64UrlEncode(new Uint8Array(digest));
}

function base64UrlEncode(buffer) {
    let str = '';
    for (const byte of buffer) {
        str += String.fromCharCode(byte);
    }
    return btoa(str)
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');
}

// ---------------------------------------------------------------------------
// JWT helpers
// ---------------------------------------------------------------------------

function decodeJwtPayload(jwt) {
    const parts = jwt.split('.');
    if (parts.length !== 3) return null;
    const payload = parts[1].replace(/-/g, '+').replace(/_/g, '/');
    try {
        return JSON.parse(atob(payload));
    } catch {
        return null;
    }
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Initiates the login flow. Generates PKCE verifier/challenge, stores the
 * verifier in sessionStorage, and redirects to the Cognito Hosted UI.
 */
export async function login() {
    const verifier = generateCodeVerifier();
    const challenge = await generateCodeChallenge(verifier);

    // Store verifier for the callback -- sessionStorage is acceptable here
    // because the value is ephemeral and deleted immediately after use.
    sessionStorage.setItem('pkce_verifier', verifier);

    const params = new URLSearchParams({
        response_type: 'code',
        client_id:     CLIENT_ID,
        redirect_uri:  REDIRECT_URI,
        scope:         'openid email profile',
        code_challenge_method: 'S256',
        code_challenge: challenge,
    });

    window.location.href = `${AUTHORIZE_URL}?${params.toString()}`;
}

/**
 * Handles the OAuth callback. Extracts the authorization code from the URL,
 * exchanges it for tokens, and stores them in memory.
 *
 * @returns {boolean} true if tokens were successfully obtained
 */
export async function handleCallback() {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    const error = params.get('error');

    if (error) {
        console.error('[auth] OAuth error:', error, params.get('error_description'));
        return false;
    }

    if (!code) {
        return false;
    }

    const verifier = sessionStorage.getItem('pkce_verifier');
    if (!verifier) {
        console.error('[auth] Missing PKCE verifier -- cannot exchange code');
        return false;
    }

    try {
        const response = await fetch(TOKEN_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({
                grant_type:    'authorization_code',
                client_id:     CLIENT_ID,
                redirect_uri:  REDIRECT_URI,
                code:          code,
                code_verifier: verifier,
            }),
        });

        if (!response.ok) {
            const text = await response.text();
            console.error('[auth] Token exchange failed:', response.status, text);
            return false;
        }

        const data = await response.json();
        storeTokens(data);

        // Clean up
        sessionStorage.removeItem('pkce_verifier');

        // Remove code from URL without triggering a reload
        window.history.replaceState({}, document.title, window.location.pathname);

        console.log('[auth] Authentication successful');
        return true;
    } catch (err) {
        console.error('[auth] Token exchange error:', err);
        return false;
    }
}

/**
 * Returns the current ID token. If the token is within 60 seconds of expiry,
 * it is refreshed first. Returns null if not authenticated.
 *
 * @returns {Promise<string|null>}
 */
export async function getIdToken() {
    if (!idToken) return null;

    // Refresh if within 60 seconds of expiry
    const now = Date.now();
    if (tokenExpiry - now < 60_000) {
        const refreshed = await refreshTokens();
        if (!refreshed) return null;
    }

    return idToken;
}

/**
 * Refreshes the token set using the stored refresh token.
 *
 * @returns {Promise<boolean>} true if refresh succeeded
 */
export async function refreshTokens() {
    if (!refreshToken) {
        console.warn('[auth] No refresh token available');
        return false;
    }

    try {
        const response = await fetch(TOKEN_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({
                grant_type:    'refresh_token',
                client_id:     CLIENT_ID,
                refresh_token: refreshToken,
            }),
        });

        if (!response.ok) {
            console.error('[auth] Token refresh failed:', response.status);
            clearTokens();
            return false;
        }

        const data = await response.json();
        // Cognito does not return a new refresh_token on refresh -- keep the old one
        storeTokens({ ...data, refresh_token: data.refresh_token || refreshToken });
        console.log('[auth] Tokens refreshed');
        return true;
    } catch (err) {
        console.error('[auth] Token refresh error:', err);
        clearTokens();
        return false;
    }
}

/**
 * Logs the user out. Clears in-memory tokens and redirects to the Cognito
 * logout endpoint to invalidate the server-side session.
 */
export function logout() {
    clearTokens();
    const logoutRedirect = config.LOGOUT_URI || window.location.origin;
    const params = new URLSearchParams({
        client_id:  CLIENT_ID,
        logout_uri: logoutRedirect,
    });
    window.location.href = `${LOGOUT_URL}?${params.toString()}`;
}

/**
 * Returns the decoded user info from the ID token, or null if not
 * authenticated. Contains fields like email, sub, name, etc.
 *
 * @returns {object|null}
 */
export function getUserInfo() {
    return userPayload;
}

/**
 * Returns true if the user is currently authenticated with valid tokens.
 *
 * @returns {boolean}
 */
export function isAuthenticated() {
    return idToken !== null && Date.now() < tokenExpiry;
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

function storeTokens(data) {
    idToken      = data.id_token      || idToken;
    accessToken  = data.access_token  || accessToken;
    refreshToken = data.refresh_token || refreshToken;

    if (idToken) {
        userPayload = decodeJwtPayload(idToken);
        if (userPayload && userPayload.exp) {
            tokenExpiry = userPayload.exp * 1000;
        }
    }
}

function clearTokens() {
    idToken      = null;
    accessToken  = null;
    refreshToken = null;
    tokenExpiry  = 0;
    userPayload  = null;
}
