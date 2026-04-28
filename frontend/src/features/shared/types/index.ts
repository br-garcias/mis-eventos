export type UserRole = 'admin' | 'organizer' | 'attendee';

export type EventStatus = 'draft' | 'published' | 'cancelled' | 'finished';

export type RegistrationStatus = 'confirmed' | 'cancelled' | 'waitlist';

export interface StatusInfo {
  readonly label: string;
  readonly color: string;
}
