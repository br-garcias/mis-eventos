import type {
  Attendee,
  CreateEventDTO,
  CreateSessionDTO,
  EventDetail,
  EventListItem,
  EventListQuery,
  EventSession,
  PaginatedResponse,
  UpdateEventDTO,
  UpdateSessionDTO,
} from '@/features/events/types';
import { apiClient } from '@/lib/http/apiClient';

function toParams(q: EventListQuery): Record<string, string> {
  const params: Record<string, string> = {};
  if (q.status) params.status = q.status;
  if (q.page && q.page > 1) params.page = String(q.page);
  if (q.size && q.size !== 20) params.size = String(q.size);
  if (q.sort_by) params.sort_by = q.sort_by;
  if (q.q) params.q = q.q;
  if (q.user_id) params.user_id = q.user_id;
  return params;
}

/**
 * EventService — handles event CRUD with real API contracts.
 */
export const EventService = {
  async list(query: EventListQuery = {}): Promise<PaginatedResponse<EventListItem>> {
    return apiClient.get<PaginatedResponse<EventListItem>>('/events', {
      params: toParams(query),
      requireAuth: false,
    });
  },

  async listMyEvents(query: EventListQuery = {}): Promise<PaginatedResponse<EventListItem>> {
    return apiClient.get<PaginatedResponse<EventListItem>>('/events/me/list', {
      params: toParams(query),
    });
  },

  async getById(id: string, userId?: string): Promise<EventDetail> {
    const params: Record<string, string> = {};
    if (userId) params.user_id = userId;
    return apiClient.get<EventDetail>(`/events/${id}`, { requireAuth: false, params });
  },

  async create(data: CreateEventDTO): Promise<EventDetail> {
    return apiClient.post<EventDetail>('/events', data);
  },

  async update(id: string, data: UpdateEventDTO): Promise<EventDetail> {
    return apiClient.patch<EventDetail>(`/events/${id}`, data);
  },

  async remove(id: string): Promise<void> {
    return apiClient.delete(`/events/${id}`);
  },

  async publish(id: string): Promise<EventDetail> {
    return apiClient.post<EventDetail>(`/events/${id}/publish`);
  },

  async cancel(id: string): Promise<EventDetail> {
    return apiClient.post<EventDetail>(`/events/${id}/cancel`);
  },

  async register(eventId: string): Promise<void> {
    await apiClient.post(`/events/${eventId}/register`);
  },

  async unregister(eventId: string): Promise<void> {
    await apiClient.delete(`/events/${eventId}/register`);
  },

  async createSession(eventId: string, data: CreateSessionDTO): Promise<EventSession> {
    return apiClient.post<EventSession>(`/events/${eventId}/sessions`, data);
  },

  async updateSession(
    eventId: string,
    sessionId: string,
    data: UpdateSessionDTO,
  ): Promise<EventSession> {
    return apiClient.patch<EventSession>(`/events/${eventId}/sessions/${sessionId}`, data);
  },

  async deleteSession(eventId: string, sessionId: string): Promise<void> {
    return apiClient.delete(`/events/${eventId}/sessions/${sessionId}`);
  },

  async getAttendees(eventId: string): Promise<PaginatedResponse<Attendee>> {
    return apiClient.get<PaginatedResponse<Attendee>>(`/events/${eventId}/attendees`);
  },
} as const;
