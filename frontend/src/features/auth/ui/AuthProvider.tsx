import { useAuthStore } from '@/features/auth/store';
import type { User } from '@/features/auth/types';
import type { UserRole } from '@/features/shared/types';
import { PageLoader } from '@/features/shared/ui/PageLoader';
import { authBroadcast } from '@/lib/auth-broadcast';
import { APP_CONFIG } from '@/lib/config';
import { apiClient } from '@/lib/http/apiClient';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

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

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const setUser = useAuthStore((s) => s.setUser);
  const setStatus = useAuthStore((s) => s.setStatus);
  const reset = useAuthStore((s) => s.reset);
  const status = useAuthStore((s) => s.status);
  const navigate = useNavigate();

  useEffect(() => {
    const offUnauthorized = apiClient.onUnauthorized(() => {
      reset();
      navigate(APP_CONFIG.routes.login, { replace: true });
    });

    const offBroadcast = authBroadcast.onMessage((msg) => {
      if (msg.type === 'logout') {
        apiClient.clearTokens();
        reset();
        navigate(APP_CONFIG.routes.login, { replace: true });
      }
    });

    return () => {
      offUnauthorized();
      offBroadcast();
    };
  }, [reset, navigate]);

  useEffect(() => {
    if (status !== 'loading') return;

    const bootstrap = async () => {
      const { accessToken, refreshToken } = apiClient.getTokens();
      if (!accessToken && !refreshToken) {
        setStatus('unauthenticated');
        return;
      }

      for (let attempt = 0; attempt <= APP_CONFIG.auth.bootstrapMaxRetries; attempt++) {
        try {
          const apiUser = await apiClient.get<ApiUser>(APP_CONFIG.endpoints.me);
          setUser(normalizeUser(apiUser));
          setStatus('authenticated');
          return;
        } catch (e: unknown) {
          const err = e as { status?: number; isNetworkError?: boolean };
          const isRetryable = err?.isNetworkError && attempt < APP_CONFIG.auth.bootstrapMaxRetries;
          if (!isRetryable) {
            setStatus('unauthenticated');
            return;
          }
          await sleep(APP_CONFIG.auth.bootstrapRetryDelayMs * (attempt + 1));
        }
      }
    };

    bootstrap();
  }, [status, setUser, setStatus]);

  if (status === 'loading') return <PageLoader />;

  return <>{children}</>;
}
