import { useEventStore } from '@/features/events/store';
import { useEffect } from 'react';
import { EventsFilters } from './EventsFilters';
import { EventsGrid } from './EventsGrid';
import { EventsPagination } from './EventsPagination';

export function HomePage() {
  const items = useEventStore((s) => s.items);
  const total = useEventStore((s) => s.total);
  const page = useEventStore((s) => s.page);
  const size = useEventStore((s) => s.size);
  const status = useEventStore((s) => s.status);
  const searchName = useEventStore((s) => s.searchName);
  const isLoading = useEventStore((s) => s.isLoading);
  const fetchEvents = useEventStore((s) => s.fetchEvents);
  const setPage = useEventStore((s) => s.setPage);
  const setStatus = useEventStore((s) => s.setStatus);
  const setSearchName = useEventStore((s) => s.setSearchName);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const totalPages = Math.ceil(total / size);
  const isInitialLoading = isLoading && items.length === 0;
  const isFiltering = isLoading && items.length > 0;

  return (
    <div className="min-h-screen">
      {/* ——— HERO ——— */}
      <section className="relative pt-28 pb-20 px-4 overflow-hidden">
        <div className="absolute inset-0 hero-grid opacity-30" />
        <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-brand-400/8 rounded-full blur-[120px]" />
        <div className="absolute top-40 right-1/4 w-[300px] h-[200px] bg-accent-teal/5 rounded-full blur-[80px]" />

        <div className="relative max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 glass px-4 py-2 rounded-full mb-6 animate-fade-up">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-sm text-white/60 font-body">
              Plataforma activa · {total} eventos
            </span>
          </div>

          <h1
            className="font-display font-black text-3xl sm:text-5xl lg:text-6xl text-white leading-[0.95] tracking-tight mb-6 animate-fade-up"
            style={{ animationDelay: '0.1s' }}
          >
            Descubre eventos
            <br />
            <span className="gradient-text">extraordinarios</span>
          </h1>

          <p
            className="text-white/50 font-body text-lg sm:text-xl max-w-2xl mx-auto leading-relaxed mb-10 animate-fade-up"
            style={{ animationDelay: '0.2s' }}
          >
            Tecnología, cultura, negocios y más. Conecta con la comunidad más vibrante de Colombia.
          </p>
        </div>
      </section>

      {/* ——— EVENTS SECTION ——— */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="font-display font-bold text-xl text-white">
              {status === 'published'
                ? 'Próximos eventos'
                : status === 'finished'
                  ? 'Eventos pasados'
                  : 'Todos los eventos'}
            </h2>
            <p className="text-white/40 text-sm font-body mt-1">
              {total} {total === 1 ? 'evento disponible' : 'eventos disponibles'}
            </p>
          </div>

          <EventsFilters
            status={status}
            initialSearch={searchName}
            isFiltering={isFiltering}
            onStatusChange={setStatus}
            onSearchChange={setSearchName}
          />
        </div>

        <div
          className={`transition-opacity ${isFiltering ? 'opacity-60 pointer-events-none' : ''}`}
        >
          <EventsGrid
            items={items}
            isLoading={isInitialLoading}
            status={status}
            onClearStatus={() => setStatus(undefined)}
          />
          <EventsPagination page={page} totalPages={totalPages} onChange={setPage} />
        </div>
      </section>
    </div>
  );
}
