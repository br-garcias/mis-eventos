import type { EventListItem } from '@/features/events/types';
import type { EventStatus } from '@/features/shared/types';
import { EmptyState } from '@/features/shared/ui/EmptyState';
import { Skeleton } from '@/features/shared/ui/Skeleton';
import { EventCard } from './EventCard';

interface EventsGridProps {
  items: EventListItem[];
  isLoading: boolean;
  status: EventStatus | undefined;
  onClearStatus: () => void;
}

export function EventsGrid({ items, isLoading, status, onClearStatus }: EventsGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="space-y-3">
            <Skeleton className="h-48 w-full" />
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
            <Skeleton className="h-4 w-2/3" />
          </div>
        ))}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <EmptyState
        icon="🔍"
        title="No hay eventos"
        description={
          status
            ? `No hay eventos ${status === 'published' ? 'próximos' : 'pasados'}`
            : 'Vuelve más tarde para ver nuevos eventos'
        }
        action={
          status ? (
            <button
              onClick={onClearStatus}
              className="px-4 py-2 rounded-xl border border-white/10 text-white/60 hover:text-white text-sm"
            >
              Ver todos
            </button>
          ) : undefined
        }
      />
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {items.map((event, i) => (
        <div
          key={event.id}
          className="animate-fade-up"
          style={{ animationDelay: `${i * 0.07}s`, animationFillMode: 'both' }}
        >
          <EventCard event={event} />
        </div>
      ))}
    </div>
  );
}
