import Cookies from 'js-cookie';

export const AUTH_CONFIG = {
  COOKIE_NAMES: {
    ACCESS_TOKEN: 'access_token',
    REFRESH_TOKEN: 'refresh_token',
    SESSION_ID: 'session_id',
  },
  COOKIE_OPTIONS: {
    expires: 7,
    path: '/',
    sameSite: 'strict' as const,
  },
} as const;

export interface TokenData {
  access_token: string;
  access_token_expiry: number;
  refresh_token: string;
  refresh_token_expiry: number;
  session_id: string;
}

export interface ExtractedTokens {
  accessToken: string | null;
  refreshToken: string | null;
  sessionId: string | null;
}

export function extractTokens(): ExtractedTokens {
  const accessToken = Cookies.get(AUTH_CONFIG.COOKIE_NAMES.ACCESS_TOKEN) || null;
  const refreshToken = Cookies.get(AUTH_CONFIG.COOKIE_NAMES.REFRESH_TOKEN) || null;
  const sessionId = Cookies.get(AUTH_CONFIG.COOKIE_NAMES.SESSION_ID) || null;

  return { accessToken, refreshToken, sessionId };
}

export function setAuthCookies(tokens: TokenData): void {
  const now = Math.floor(Date.now() / 1000);

  Cookies.set(AUTH_CONFIG.COOKIE_NAMES.ACCESS_TOKEN, tokens.access_token, {
    ...AUTH_CONFIG.COOKIE_OPTIONS,
    expires: (tokens.access_token_expiry - now) / (60 * 60 * 24),
  });

  Cookies.set(AUTH_CONFIG.COOKIE_NAMES.SESSION_ID, tokens.session_id, {
    ...AUTH_CONFIG.COOKIE_OPTIONS,
    expires: (tokens.access_token_expiry - now) / (60 * 60 * 24),
  });

  Cookies.set(AUTH_CONFIG.COOKIE_NAMES.REFRESH_TOKEN, tokens.refresh_token, {
    ...AUTH_CONFIG.COOKIE_OPTIONS,
    expires: (tokens.refresh_token_expiry - now) / (60 * 60 * 24),
  });
}

export function clearAuthCookies(): void {
  Cookies.remove(AUTH_CONFIG.COOKIE_NAMES.ACCESS_TOKEN);
  Cookies.remove(AUTH_CONFIG.COOKIE_NAMES.REFRESH_TOKEN);
  Cookies.remove(AUTH_CONFIG.COOKIE_NAMES.SESSION_ID);
}

export function hasValidAuth(tokens: ExtractedTokens): boolean {
  return !!(tokens.accessToken && tokens.refreshToken && tokens.sessionId);
}

export function needsTokenRefresh(tokens: ExtractedTokens): boolean {
  return !!tokens.refreshToken && !tokens.accessToken;
}
