import { useAuthStore } from '@/features/auth/store';
import { EventService } from '@/features/events/services';
import type {
  CreateSessionDTO,
  EventActions,
  EventState,
  UpdateSessionDTO,
} from '@/features/events/types';
import { create } from 'zustand';

export const useEventStore = create<EventState & EventActions>()((set, get) => ({
  items: [],
  total: 0,
  page: 1,
  size: 10,
  status: undefined,
  sortBy: 'start_at',
  searchName: '',
  currentEvent: null,
  isLoading: false,
  error: null,

  fetchEvents: async () => {
    set({ isLoading: true, error: null });
    const { page, size, status, sortBy, searchName } = get();
    try {
      const query = {
        page,
        size,
        status,
        sort_by: sortBy,
        q: searchName || undefined,
      };
      const response = await EventService.list(query);
      set({ items: response.items, total: response.total, isLoading: false });
    } catch (e) {
      set({ isLoading: false, error: (e as Error).message });
    }
  },

  fetchEvent: async (id) => {
    set({ isLoading: true, error: null });
    const user = useAuthStore.getState().user;
    try {
      const event = await EventService.getById(id, user?.id);
      set({ currentEvent: event, isLoading: false });
    } catch (e) {
      set({ isLoading: false, error: (e as Error).message });
    }
  },

  createEvent: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const newEvent = await EventService.create(data);
      set((state) => ({
        items: [newEvent, ...state.items],
        total: state.total + 1,
        isLoading: false,
      }));
      return newEvent;
    } catch (e) {
      set({ isLoading: false, error: (e as Error).message });
      throw e;
    }
  },

  updateEvent: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const updated = await EventService.update(id, data);
      set((state) => ({
        items: state.items.map((e) => (e.id === id ? updated : e)),
        currentEvent: updated,
        isLoading: false,
      }));
    } catch (e) {
      set({ isLoading: false, error: (e as Error).message });
      throw e;
    }
  },

  deleteEvent: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await EventService.remove(id);
      set((state) => ({
        items: state.items.filter((e) => e.id !== id),
        total: state.total - 1,
        isLoading: false,
      }));
    } catch (e) {
      set({ isLoading: false, error: (e as Error).message });
      throw e;
    }
  },

  setPage: (page) => {
    set({ page });
    get().fetchEvents();
  },

  setStatus: (status) => {
    set({ status, page: 1 });
    get().fetchEvents();
  },

  setSortBy: (sortBy) => {
    set({ sortBy, page: 1 });
    get().fetchEvents();
  },

  setSearchName: (name) => {
    set({ searchName: name, page: 1 });
    get().fetchEvents();
  },

  createSession: async (eventId: string, data: CreateSessionDTO) => {
    set({ error: null });
    try {
      const newSession = await EventService.createSession(eventId, data);
      const currentEvent = get().currentEvent;
      if (currentEvent && currentEvent.id === eventId) {
        set({
          currentEvent: {
            ...currentEvent,
            sessions: [...currentEvent.sessions, newSession],
          },
        });
      }
      return newSession;
    } catch (e) {
      set({ error: (e as Error).message });
      throw e;
    }
  },

  updateSession: async (eventId: string, sessionId: string, data: UpdateSessionDTO) => {
    set({ error: null });
    try {
      const updatedSession = await EventService.updateSession(eventId, sessionId, data);
      const currentEvent = get().currentEvent;
      if (currentEvent && currentEvent.id === eventId) {
        set({
          currentEvent: {
            ...currentEvent,
            sessions: currentEvent.sessions.map((s) => (s.id === sessionId ? updatedSession : s)),
          },
        });
      }
      return updatedSession;
    } catch (e) {
      set({ error: (e as Error).message });
      throw e;
    }
  },

  deleteSession: async (eventId: string, sessionId: string) => {
    set({ error: null });
    try {
      await EventService.deleteSession(eventId, sessionId);
      const currentEvent = get().currentEvent;
      if (currentEvent && currentEvent.id === eventId) {
        set({
          currentEvent: {
            ...currentEvent,
            sessions: currentEvent.sessions.filter((s) => s.id !== sessionId),
          },
        });
      }
    } catch (e) {
      set({ error: (e as Error).message });
      throw e;
    }
  },

  clearError: () => set({ error: null }),
}));
