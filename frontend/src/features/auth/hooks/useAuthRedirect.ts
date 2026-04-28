import { useAuthStore } from '@/features/auth/store';
import { APP_CONFIG } from '@/lib/config';
import { useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

/**
 * Encapsula el flujo de retorno post-login/registro.
 *
 * - `redirectToAuth(path)`: guarda la URL actual y navega a /login o /registro.
 * - `resolveReturnUrl()`: retorna la URL de retorno (store > location.state > home).
 */
export function useAuthRedirect() {
  const navigate = useNavigate();
  const location = useLocation();
  const setReturnUrl = useAuthStore((s) => s.setReturnUrl);
  const clearReturnUrl = useAuthStore((s) => s.clearReturnUrl);

  const redirectToAuth = useCallback(
    (path: '/login' | '/registro') => {
      setReturnUrl(window.location.pathname);
      navigate(path);
    },
    [navigate, setReturnUrl],
  );

  const resolveReturnUrl = useCallback((): string => {
    const stored = useAuthStore.getState().returnUrl;
    clearReturnUrl();
    const fromState = (location.state as { from?: string } | null)?.from;
    return stored || fromState || APP_CONFIG.routes.home;
  }, [clearReturnUrl, location.state]);

  return { redirectToAuth, resolveReturnUrl };
}
