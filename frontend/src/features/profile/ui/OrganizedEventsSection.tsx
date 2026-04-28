import { EventService } from '@/features/events/services';
import type { EventListItem } from '@/features/events/types';
import { useDebouncedValue } from '@/features/shared/hooks/useDebouncedValue';
import { Badge } from '@/features/shared/ui/Badge';
import { Button } from '@/features/shared/ui/Button';
import { EmptyState } from '@/features/shared/ui/EmptyState';
import { Skeleton } from '@/features/shared/ui/Skeleton';
import { Spinner } from '@/features/shared/ui/Spinner';
import { showToast } from '@/features/shared/utils/toast';
import { Search } from 'lucide-react';
import { useEffect, useState, useTransition } from 'react';
import { Link } from 'react-router-dom';
import { MyEventCard } from './MyEventCard';

export function OrganizedEventsSection() {
  const [events, setEvents] = useState<EventListItem[] | null>(null);
  const [input, setInput] = useState('');
  const [isPending, startTransition] = useTransition();
  const debounced = useDebouncedValue(input, 350);

  useEffect(() => {
    let cancelled = false;
    const run = () =>
      EventService.listMyEvents({ size: 100, q: debounced || undefined })
        .then((res) => {
          if (!cancelled) setEvents(res.items);
        })
        .catch(() => {
          if (!cancelled) showToast('Error al cargar eventos', 'error');
        });
    startTransition(() => {
      run();
    });
    return () => {
      cancelled = true;
    };
  }, [debounced]);

  const isInitial = events === null;
  const list = events ?? [];

  return (
    <section>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <h2 className="font-display font-bold text-xl text-white flex items-center gap-2">
          Eventos organizados
          <Badge variant="secondary">{list.length}</Badge>
        </h2>
        <div className="relative w-full sm:w-56">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30" />
          <input
            type="text"
            placeholder="Buscar mis eventos..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="w-full pl-9 pr-9 py-1.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/30 text-sm focus:outline-none focus:border-brand-400/50 transition-all"
          />
          {(isPending || (isInitial && input)) && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              <Spinner size="sm" />
            </div>
          )}
        </div>
      </div>

      {isInitial ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
      ) : list.length === 0 ? (
        <EmptyState
          icon="📅"
          title={debounced ? 'Sin resultados' : 'No has creado eventos'}
          description={
            debounced
              ? `No hay eventos que coincidan con "${debounced}"`
              : 'Crea tu primer evento y empieza a gestionar asistentes'
          }
          action={
            !debounced ? (
              <Link to="/eventos/crear">
                <Button>Crear mi primer evento</Button>
              </Link>
            ) : undefined
          }
        />
      ) : (
        <div className={`space-y-3 transition-opacity ${isPending ? 'opacity-60' : ''}`}>
          {list.map((event) => (
            <MyEventCard key={event.id} event={event} isRegistered={false} />
          ))}
        </div>
      )}
    </section>
  );
}
