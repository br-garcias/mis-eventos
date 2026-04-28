import type { ReactNode } from 'react';

/** Display configuration for each user role. */
export interface RoleConfig {
  label: string;
  color: string;
  icon: ReactNode;
}
