import type { PaginatedRegistrations } from '@/features/registrations/types';
import { apiClient } from '@/lib/http/apiClient';

export const RegistrationService = {
  async getMyRegistrations(page = 1, size = 20): Promise<PaginatedRegistrations> {
    return apiClient.get<PaginatedRegistrations>('/me/registrations', {
      params: { page: String(page), size: String(size) },
    });
  },
} as const;
