import type { EventListItem } from '@/features/events/types';
import { EVENT_STATUSES } from '@/features/shared/constants';
import { Badge } from '@/features/shared/ui/Badge';
import { cn } from '@/lib/cn';
import { formatDateShort } from '@/lib/formatters';
import { Calendar, MapPin } from 'lucide-react';
import { Link } from 'react-router-dom';

interface MyEventCardProps {
  event: EventListItem;
  isRegistered: boolean;
  onUnregister?: (eventId: string) => void;
}

export function MyEventCard({ event, isRegistered, onUnregister }: MyEventCardProps) {
  const statusInfo = EVENT_STATUSES[event.status];

  return (
    <div className={cn('glass-card rounded-xl overflow-hidden flex', 'hover:border-brand-400/30')}>
      {/* Color strip */}
      <div className="w-2 shrink-0 bg-linear-to-b from-violet-600/30 via-blue-600/20 to-cyan-500/30" />

      <div className="flex-1 p-4 flex flex-col sm:flex-row sm:items-center gap-4">
        {/* Emoji */}
        <div className="hidden sm:flex w-12 h-12 rounded-xl bg-linear-to-br from-violet-600/30 via-blue-600/20 to-cyan-500/30 shrink-0 items-center justify-center text-2xl">
          🚀
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <Badge variant={(statusInfo?.color as 'default') || 'default'} className="text-xs">
              {statusInfo?.label}
            </Badge>
          </div>
          <Link to={`/eventos/${event.id}`}>
            <h3 className="font-display font-bold text-white text-sm hover:text-brand-400 transition-colors line-clamp-1">
              {event.name}
            </h3>
          </Link>
          <div className="flex flex-wrap gap-3 mt-1.5 text-xs text-white/40">
            <span className="flex items-center gap-1">
              <Calendar size={11} />
              {formatDateShort(event.start_at)}
            </span>
            <span className="flex items-center gap-1">
              <MapPin size={11} />
              {event.location}
            </span>
            <span className="font-medium text-green-400">Gratis</span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 shrink-0">
          {isRegistered && onUnregister && (
            <button
              onClick={() => onUnregister(event.id)}
              className="text-xs text-red-400 hover:text-red-300 px-3 py-1.5 rounded-lg border border-red-500/20 hover:bg-red-500/10 transition-all"
            >
              Cancelar
            </button>
          )}
          <Link to={`/eventos/${event.id}`}>
            <button className="text-xs text-brand-400 hover:text-brand-300 px-3 py-1.5 rounded-lg border border-brand-400/20 hover:bg-brand-400/10 transition-all">
              Ver evento →
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
}
