import type { EventListItem } from '@/features/events/types';
import type { RegistrationStatus } from '@/features/shared/types';

export interface Registration {
  id: string;
  user_id: string;
  event_id: string;
  status: RegistrationStatus;
  registered_at: string;
  event?: EventListItem;
}

export interface PaginatedRegistrations {
  items: Registration[];
  total: number;
  page: number;
  size: number;
}
