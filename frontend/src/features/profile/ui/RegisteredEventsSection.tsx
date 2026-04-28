import { EventService } from '@/features/events/services';
import { RegistrationService } from '@/features/registrations/services';
import type { Registration } from '@/features/registrations/types';
import { Badge } from '@/features/shared/ui/Badge';
import { Button } from '@/features/shared/ui/Button';
import { EmptyState } from '@/features/shared/ui/EmptyState';
import { Skeleton } from '@/features/shared/ui/Skeleton';
import { showToast } from '@/features/shared/utils/toast';
import { formatApiError } from '@/lib/apiError';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { MyEventCard } from './MyEventCard';

export function RegisteredEventsSection() {
  const [registrations, setRegistrations] = useState<Registration[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await RegistrationService.getMyRegistrations();
        if (!cancelled) setRegistrations(res.items);
      } catch {
        if (!cancelled) showToast('Error al cargar registros', 'error');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleUnregister = async (eventId: string) => {
    try {
      await EventService.unregister(eventId);
      setRegistrations((prev) => (prev ?? []).filter((r) => r.event_id !== eventId));
      showToast('Registro cancelado', 'info');
    } catch (err) {
      showToast(formatApiError(err), 'error');
    }
  };

  return (
    <section className="mb-10">
      <h2 className="font-display font-bold text-xl text-white mb-4 flex items-center gap-2">
        Mis Registros
        <Badge variant="default">{registrations?.length ?? 0}</Badge>
      </h2>
      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
      ) : (registrations?.length ?? 0) === 0 ? (
        <EmptyState
          icon="🎫"
          title="Aún no te has registrado"
          description="Explora eventos y únete a los que más te interesen"
          action={
            <Link to="/">
              <Button variant="outline">Explorar eventos</Button>
            </Link>
          }
        />
      ) : (
        <div className="space-y-3">
          {(registrations ?? []).map(
            (reg) =>
              reg.event && (
                <MyEventCard
                  key={reg.id}
                  event={reg.event}
                  isRegistered
                  onUnregister={() => handleUnregister(reg.event_id)}
                />
              ),
          )}
        </div>
      )}
    </section>
  );
}
