import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { UserRole } from '../types';

export interface Role {
  id: string;
  name: UserRole;
  description?: string;
}

interface RolesState {
  roles: Role[];
  isLoading: boolean;
}

interface RolesActions {
  setRoles: (roles: Role[]) => void;
  setLoading: (loading: boolean) => void;
  getRoleById: (id: string) => Role | undefined;
  getRoleByName: (name: UserRole) => Role | undefined;
}

type RolesStore = RolesState & RolesActions;

export const useRolesStore = create<RolesStore>()(
  persist(
    devtools(
      (set, get) => ({
        roles: [],
        isLoading: false,

        setRoles: (roles) => set({ roles }),

        setLoading: (isLoading) => set({ isLoading }),

        getRoleById: (id) => get().roles.find((r) => r.id === id),

        getRoleByName: (name) => get().roles.find((r) => r.name === name),
      }),
      { name: 'roles-store' },
    ),
    {
      name: 'roles-storage',
      partialize: (state) => ({ roles: state.roles }),
    },
  ),
);
