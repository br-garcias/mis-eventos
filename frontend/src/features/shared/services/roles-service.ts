import { APP_CONFIG } from '@/lib/config';
import { apiClient } from '@/lib/http/apiClient';
import type { UserRole } from '../types';

export interface RoleResponse {
  id: string;
  role: string;
  description?: string;
}

function normalizeRole(apiRole: RoleResponse) {
  return {
    id: apiRole.id,
    name: apiRole.role as UserRole,
    description: apiRole.description,
  };
}

export const rolesService = {
  async getAll() {
    const roles = await apiClient.get<RoleResponse[]>(APP_CONFIG.endpoints.roles);
    return roles.map(normalizeRole);
  },
} as const;
