const API_URL = (import.meta.env.VITE_API_URL ?? '/api/v1').replace(/\/$/, '');

export const APP_CONFIG = {
  api: {
    baseUrl: API_URL,
    timeoutMs: 30_000,
    authTimeoutMs: 8_000,
  },
  endpoints: {
    login: '/auth/login',
    register: '/auth/register',
    refresh: '/auth/refresh',
    logout: '/auth/logout',
    me: '/auth/me',
    roles: '/roles',
  },
  routes: {
    login: '/login',
    register: '/registro',
    home: '/',
    forbidden: '/403',
  },
  cookies: {
    access: 'access_token',
    refresh: 'refresh_token',
    meta: 'session_meta',
    options: {
      secure: import.meta.env.PROD,
      sameSite: 'strict' as const,
      path: '/',
    },
  },
  auth: {
    refreshSkewSeconds: 60,
    bootstrapMaxRetries: 1,
    bootstrapRetryDelayMs: 800,
    broadcastChannelName: 'mis-eventos-auth',
  },
  storage: {
    authStateKey: 'mis-eventos-auth',
  },
} as const;

export type AppConfig = typeof APP_CONFIG;
