import { AuthService } from '@/features/auth/services';
import type { AuthActions, AuthState, AuthStatus } from '@/features/auth/types';
import { formatApiError } from '@/lib/apiError';
import { authBroadcast } from '@/lib/auth-broadcast';
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export const useAuthStore = create<AuthState & AuthActions>()(
  devtools(
    (set, get) => ({
      user: null,
      status: 'loading' as AuthStatus,
      isLoading: false,
      error: null,
      returnUrl: null,

      setReturnUrl: (url: string | null) => set({ returnUrl: url }),
      clearReturnUrl: () => set({ returnUrl: null }),

      login: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
          const user = await AuthService.login(email, password);
          set({ user, status: 'authenticated', isLoading: false });
          return true;
        } catch (err) {
          set({ isLoading: false, error: formatApiError(err) });
          return false;
        }
      },

      register: async (data) => {
        set({ isLoading: true, error: null });
        try {
          const user = await AuthService.register(data);
          set({ user, status: 'authenticated', isLoading: false });
          return true;
        } catch (err) {
          set({ isLoading: false, error: formatApiError(err) });
          return false;
        }
      },

      logout: async () => {
        try {
          await AuthService.logout();
        } finally {
          set({ user: null, status: 'unauthenticated', error: null });
          authBroadcast.send({ type: 'logout' });
        }
      },

      setUser: (user) => set({ user }),
      setStatus: (status) => set({ status }),
      reset: () => set({ user: null, status: 'unauthenticated', error: null }),

      isAuthenticated: () => get().status === 'authenticated',
      isAdmin: () => get().user?.role.name === 'admin',
      isOrganizer: () => ['admin', 'organizer'].includes(get().user?.role.name ?? ''),
      clearError: () => set({ error: null }),
    }),
    { name: 'auth-store' },
  ),
);
