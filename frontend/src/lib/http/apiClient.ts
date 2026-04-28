import { APP_CONFIG } from '@/lib/config';
import Cookies from 'js-cookie';

export class ApiError extends Error {
  status: number;
  data: unknown;
  isNetworkError: boolean;
  isTimeout: boolean;
  requestId?: string;

  constructor(init: {
    message: string;
    status?: number;
    data?: unknown;
    isNetworkError?: boolean;
    isTimeout?: boolean;
    requestId?: string;
  }) {
    super(init.message);
    this.name = 'ApiError';
    this.status = init.status ?? 0;
    this.data = init.data ?? null;
    this.isNetworkError = !!init.isNetworkError;
    this.isTimeout = !!init.isTimeout;
    this.requestId = init.requestId;
  }
}

interface FetchOptions extends RequestInit {
  params?: Record<string, string>;
  requireAuth?: boolean;
  timeoutMs?: number;
  skipAuthRetry?: boolean;
}

class ApiClient {
  private isRefreshing = false;
  private refreshTokenPromise: Promise<boolean> | null = null;
  private unauthorizedListeners = new Set<() => void>();

  onUnauthorized(cb: () => void): () => void {
    this.unauthorizedListeners.add(cb);
    return () => this.unauthorizedListeners.delete(cb);
  }

  private emitUnauthorized() {
    this.unauthorizedListeners.forEach((cb) => {
      try {
        cb();
      } catch {
        /* ignore */
      }
    });
    window.dispatchEvent(new Event('auth:unauthorized'));
  }

  private async fetchWithTimeout(url: string, init: RequestInit, ms: number): Promise<Response> {
    const ctrl = new AbortController();
    const id = setTimeout(() => ctrl.abort(), ms);
    try {
      return await fetch(url, { ...init, signal: ctrl.signal });
    } catch (e: unknown) {
      if ((e as Error)?.name === 'AbortError') {
        throw new ApiError({ message: 'Timeout', isTimeout: true, isNetworkError: true });
      }
      throw new ApiError({ message: 'Network error', isNetworkError: true });
    } finally {
      clearTimeout(id);
    }
  }

  private getHeaders(requireAuth: boolean): HeadersInit {
    const headers: HeadersInit = { 'Content-Type': 'application/json' };
    if (requireAuth) {
      const token = Cookies.get(APP_CONFIG.cookies.access);
      if (token) headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  private buildUrl(endpoint: string, params?: Record<string, string>): string {
    // Si endpoint empieza con http, lo consideramos absoluto (aunque no deberíamos según el uso estándar de este cliente)
    const url = endpoint.startsWith('http')
      ? new URL(endpoint)
      : new URL(`${APP_CONFIG.api.baseUrl}${endpoint}`, window.location.origin);

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, value);
        }
      });
    }
    return url.toString();
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const requestId = response.headers.get('x-request-id') ?? undefined;
      throw new ApiError({
        message:
          ((errorData as Record<string, unknown>)?.message as string) ||
          response.statusText ||
          'An error occurred',
        status: response.status,
        data: errorData,
        requestId,
      });
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  }

  public async refreshAccessToken(): Promise<boolean> {
    if (this.isRefreshing) {
      return this.refreshTokenPromise!;
    }

    const refreshToken = Cookies.get(APP_CONFIG.cookies.refresh);
    if (!refreshToken) return false;

    this.isRefreshing = true;
    this.refreshTokenPromise = (async () => {
      try {
        // Hacemos el POST de refresh directo para no entrar en bucle de intercepciones
        const response = await fetch(`${APP_CONFIG.api.baseUrl}${APP_CONFIG.endpoints.refresh}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (!response.ok) {
          this.clearTokens();
          return false;
        }

        const data = await response.json();
        this.setTokens({
          access_token: data.access_token,
          refresh_token: data.refresh_token,
          access_token_expiry: data.access_token_expiry,
          refresh_token_expiry: data.refresh_token_expiry,
          session_id: data.session_id,
        });
        return true;
      } catch (error) {
        this.clearTokens();
        return false;
      } finally {
        this.isRefreshing = false;
        this.refreshTokenPromise = null;
      }
    })();

    return this.refreshTokenPromise;
  }

  public setTokens(tokens: {
    access_token: string;
    refresh_token: string;
    access_token_expiry: number;
    refresh_token_expiry: number;
    session_id: string;
  }) {
    const accessExp = new Date(tokens.access_token_expiry * 1000);
    const refreshExp = new Date(tokens.refresh_token_expiry * 1000);
    Cookies.set(APP_CONFIG.cookies.access, tokens.access_token, {
      ...APP_CONFIG.cookies.options,
      expires: accessExp,
    });
    Cookies.set(APP_CONFIG.cookies.refresh, tokens.refresh_token, {
      ...APP_CONFIG.cookies.options,
      expires: refreshExp,
    });
    Cookies.set(
      APP_CONFIG.cookies.meta,
      JSON.stringify({
        accessExpiry: tokens.access_token_expiry,
        refreshExpiry: tokens.refresh_token_expiry,
        sessionId: tokens.session_id,
      }),
      { ...APP_CONFIG.cookies.options, expires: refreshExp },
    );
    window.dispatchEvent(new Event('auth:tokens-updated'));
  }

  public clearTokens() {
    const opts = { path: '/' };
    Cookies.remove(APP_CONFIG.cookies.access, opts);
    Cookies.remove(APP_CONFIG.cookies.refresh, opts);
    Cookies.remove(APP_CONFIG.cookies.meta, opts);
  }

  public getTokens() {
    return {
      accessToken: Cookies.get(APP_CONFIG.cookies.access),
      refreshToken: Cookies.get(APP_CONFIG.cookies.refresh),
    };
  }

  public async request<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
    const {
      params,
      requireAuth = true,
      timeoutMs = APP_CONFIG.api.timeoutMs,
      skipAuthRetry,
      ...customConfig
    } = options;

    const url = this.buildUrl(endpoint, params);
    const config: RequestInit = {
      ...customConfig,
      headers: { ...this.getHeaders(requireAuth), ...customConfig.headers },
    };

    let response = await this.fetchWithTimeout(url, config, timeoutMs);

    if (response.status === 401 && requireAuth && !skipAuthRetry) {
      const refreshed = await this.refreshAccessToken();
      if (refreshed) {
        config.headers = { ...config.headers, ...this.getHeaders(true) };
        response = await this.fetchWithTimeout(url, config, timeoutMs);
      } else {
        this.emitUnauthorized();
      }
    }

    return this.handleResponse<T>(response);
  }

  public get<T>(endpoint: string, options?: Omit<FetchOptions, 'method'>) {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  public post<T>(
    endpoint: string,
    body?: unknown,
    options?: Omit<FetchOptions, 'method' | 'body'>,
  ) {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  public put<T>(endpoint: string, body?: unknown, options?: Omit<FetchOptions, 'method' | 'body'>) {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  public patch<T>(
    endpoint: string,
    body?: unknown,
    options?: Omit<FetchOptions, 'method' | 'body'>,
  ) {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  public delete<T>(endpoint: string, options?: Omit<FetchOptions, 'method'>) {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();
