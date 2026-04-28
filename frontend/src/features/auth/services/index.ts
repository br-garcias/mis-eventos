import type { RegisterDTO, User } from '@/features/auth/types';
import type { UserRole } from '@/features/shared/types';
import { APP_CONFIG } from '@/lib/config';
import { apiClient } from '@/lib/http/apiClient';

interface AuthTokens {
  session_id: string;
  access_token: string;
  access_token_expiry: number;
  refresh_token: string;
  refresh_token_expiry: number;
}

interface ApiUser {
  id: string;
  name: string;
  email: string;
  is_active: boolean;
  role: { id: string; role: string };
  created_at: string;
  updated_at: string;
}

function normalizeUser(apiUser: ApiUser): User {
  return {
    ...apiUser,
    role: {
      id: apiUser.role.id,
      name: apiUser.role.role as UserRole,
    },
  };
}

/**
 * AuthService — handles authentication logic with real API.
 */
export const AuthService = {
  async login(email: string, password: string): Promise<User> {
    const tokens = await apiClient.post<AuthTokens>(
      APP_CONFIG.endpoints.login,
      { email, password },
      { requireAuth: false },
    );
    apiClient.setTokens(tokens);
    const apiUser = await apiClient.get<ApiUser>(APP_CONFIG.endpoints.me);
    return normalizeUser(apiUser);
  },

  async register(data: Omit<RegisterDTO, 'confirmPassword'>): Promise<User> {
    const tokens = await apiClient.post<AuthTokens>(APP_CONFIG.endpoints.register, data, {
      requireAuth: false,
    });
    apiClient.setTokens(tokens);
    const apiUser = await apiClient.get<ApiUser>(APP_CONFIG.endpoints.me);
    return normalizeUser(apiUser);
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post(APP_CONFIG.endpoints.logout, undefined, { skipAuthRetry: true });
    } catch {
      /* idempotente: ignorar errores del backend */
    } finally {
      apiClient.clearTokens();
    }
  },
} as const;
