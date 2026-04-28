import type { EventStatus } from '@/features/shared/types';

export interface OrganizerRef {
  id: string;
  name: string;
  email?: string;
}

export interface EventListItem {
  id: string;
  name: string;
  description: string;
  organizer: OrganizerRef;
  status: EventStatus;
  capacity: number;
  confirmed_attendees: number;
  available_spots: number;
  start_at: string;
  end_at: string;
  location: string;
  is_registered?: boolean;
}

export interface EventSession {
  id: string;
  event_id: string;
  title: string;
  description: string;
  speaker_name: string;
  speaker_bio: string;
  start_at: string;
  end_at: string;
  created_at: string;
  updated_at: string;
}

export interface EventDetail extends EventListItem {
  organizer_id: string;
  sessions: EventSession[];
  created_at: string;
  updated_at: string;
}

export interface EventListQuery {
  status?: EventStatus;
  page?: number;
  size?: number;
  sort_by?: 'start_at' | 'created_at' | 'name';
  q?: string;
  user_id?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}

export interface CreateEventDTO {
  name: string;
  description: string;
  capacity: number;
  start_at: string;
  end_at?: string;
  location: string;
}

export type UpdateEventDTO = Partial<CreateEventDTO>;

export interface CreateSessionDTO {
  title: string;
  description: string;
  speaker_name: string;
  speaker_bio: string;
  start_at: string;
  end_at: string;
}

export type UpdateSessionDTO = Partial<CreateSessionDTO>;

export interface Attendee {
  id: string;
  user: {
    id: string;
    name: string;
    email: string;
  };
  status: 'confirmed' | 'cancelled' | 'waitlist';
  created_at: string;
  updated_at: string;
}

/** Event store state shape. */
export interface EventState {
  items: EventListItem[];
  total: number;
  page: number;
  size: number;
  status: EventStatus | undefined;
  sortBy: EventListQuery['sort_by'];
  searchName: string;
  currentEvent: EventDetail | null;
  isLoading: boolean;
  error: string | null;
}

/** Event store actions. */
export interface EventActions {
  fetchEvents: () => Promise<void>;
  fetchEvent: (id: string) => Promise<void>;
  createEvent: (data: CreateEventDTO) => Promise<EventDetail>;
  updateEvent: (id: string, data: UpdateEventDTO) => Promise<void>;
  deleteEvent: (id: string) => Promise<void>;
  setPage: (page: number) => void;
  setStatus: (status: EventStatus | undefined) => void;
  setSortBy: (sortBy: EventListQuery['sort_by']) => void;
  setSearchName: (name: string) => void;
  createSession: (eventId: string, data: CreateSessionDTO) => Promise<EventSession>;
  updateSession: (
    eventId: string,
    sessionId: string,
    data: UpdateSessionDTO,
  ) => Promise<EventSession>;
  deleteSession: (eventId: string, sessionId: string) => Promise<void>;
  clearError: () => void;
}
