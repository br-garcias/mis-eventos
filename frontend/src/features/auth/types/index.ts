import type { UserRole } from '@/features/shared/types';

export interface User {
  id: string;
  name: string;
  email: string;
  is_active: boolean;
  role: {
    id: string;
    name: UserRole;
  };
  created_at: string;
  updated_at: string;
}

export interface LoginDTO {
  email: string;
  password: string;
}

export interface RegisterDTO {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated';

/** Auth store state shape. */
export interface AuthState {
  user: User | null;
  status: AuthStatus;
  isLoading: boolean;
  error: string | null;
  returnUrl: string | null;
}

/** Auth store actions. */
export interface AuthActions {
  login: (email: string, password: string) => Promise<boolean>;
  register: (data: Omit<RegisterDTO, 'confirmPassword'>) => Promise<boolean>;
  logout: () => Promise<void>;
  setUser: (user: User | null) => void;
  setStatus: (status: AuthStatus) => void;
  reset: () => void;
  isAuthenticated: () => boolean;
  isAdmin: () => boolean;
  isOrganizer: () => boolean;
  clearError: () => void;
  setReturnUrl: (url: string | null) => void;
  clearReturnUrl: () => void;
}
