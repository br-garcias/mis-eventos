import { apiClient } from '@/lib/http/apiClient';
import type { CreateUserPayload, PaginatedUsers, Role, UpdateUserPayload, User } from '../types';

export interface ListUsersQuery {
  page?: number;
  size?: number;
  role_id?: string;
  is_active?: boolean;
  search?: string;
}

function toParams(q: ListUsersQuery = {}): Record<string, string> {
  const out: Record<string, string> = {};
  if (q.page) out.page = String(q.page);
  if (q.size) out.size = String(q.size);
  if (q.role_id) out.role_id = q.role_id;
  if (typeof q.is_active === 'boolean') out.is_active = String(q.is_active);
  if (q.search) out.search = q.search;
  return out;
}

/**
 * UsersService — handles administrative user management with real API.
 */
export const UsersService = {
  async getUsers(query: ListUsersQuery = {}): Promise<PaginatedUsers> {
    return apiClient.get<PaginatedUsers>('/users', { params: toParams(query) });
  },

  async getUserById(id: string): Promise<User> {
    return apiClient.get<User>(`/users/${id}`);
  },

  async createUser(payload: CreateUserPayload): Promise<User> {
    return apiClient.post<User>('/users', payload);
  },

  async updateUser(id: string, payload: UpdateUserPayload): Promise<User> {
    return apiClient.patch<User>(`/users/${id}`, payload);
  },

  async toggleUser(id: string): Promise<void> {
    return apiClient.post<void>(`/users/${id}/toggle`);
  },

  async getRoles(): Promise<Role[]> {
    const response = await apiClient.get<{ items: Role[] }>('/roles');
    return response.items;
  },
} as const;
