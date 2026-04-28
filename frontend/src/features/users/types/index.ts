export interface Role {
  id: string;
  name: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  role: Role;
}

export interface CreateUserPayload {
  name: string;
  email: string;
  password: string;
  role_name: string;
}

export interface UpdateUserPayload {
  name?: string;
  email?: string;
  password?: string;
  role_id?: string;
  is_active?: boolean;
}

export interface PaginatedUsers {
  items: User[];
  total: number;
  page: number;
  size: number;
}
