import type { EventStatus, StatusInfo, UserRole } from '@/features/shared/types';

/** Event status display metadata (API keys → UI labels). */
export const EVENT_STATUSES: Record<EventStatus, StatusInfo> = {
  draft: { label: 'Borrador', color: 'default' },
  published: { label: 'Publicado', color: 'green' },
  cancelled: { label: 'Cancelado', color: 'red' },
  finished: { label: 'Finalizado', color: 'gray' },
} as const;

/** User role display labels (API keys → UI labels). */
export const ROLE_LABELS: Record<UserRole, string> = {
  admin: 'Administrador',
  organizer: 'Organizador',
  attendee: 'Asistente',
} as const;
