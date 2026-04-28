import { useAuthStore } from '@/features/auth/store';
import type { UserRole } from '@/features/shared/types';
import { APP_CONFIG } from '@/lib/config';
import { Navigate, useLocation } from 'react-router-dom';

interface RequireAuthProps {
  children: React.ReactNode;
  roles?: UserRole[];
}

export function RequireAuth({ children, roles }: RequireAuthProps) {
  const status = useAuthStore((s) => s.status);
  const user = useAuthStore((s) => s.user);
  const location = useLocation();

  if (status !== 'authenticated') {
    return <Navigate to={APP_CONFIG.routes.login} state={{ from: location.pathname }} replace />;
  }

  if (roles && roles.length > 0) {
    const userRole = user?.role.name ?? '';
    const hasRole =
      roles.includes(userRole as UserRole) ||
      (roles.includes('organizer') && ['admin', 'organizer'].includes(userRole));

    if (!hasRole) {
      return <Navigate to={APP_CONFIG.routes.forbidden} replace />;
    }
  }

  return <>{children}</>;
}

export function RedirectIfAuth({ children }: { children: React.ReactNode }) {
  const status = useAuthStore((s) => s.status);
  const location = useLocation();
  const from = (location.state as { from?: string })?.from ?? APP_CONFIG.routes.home;

  if (status === 'authenticated') {
    return <Navigate to={from} replace />;
  }

  return <>{children}</>;
}
