import type { EventListItem } from '@/features/events/types';
import { EVENT_STATUSES } from '@/features/shared/constants';
import { Badge } from '@/features/shared/ui/Badge';
import { getCapacityBarColor, getCapacityPercent, getDaysUntil } from '@/lib/capacity';
import { cn } from '@/lib/cn';
import { formatDateShort } from '@/lib/formatters';
import { ArrowRight, Calendar, MapPin, Users } from 'lucide-react';
import { memo } from 'react';
import { Link } from 'react-router-dom';

interface EventCardProps {
  event: EventListItem;
  className?: string;
}

function EventCardImpl({ event, className }: EventCardProps) {
  const {
    id,
    name,
    description,
    status,
    start_at,
    capacity,
    confirmed_attendees,
    location,
    organizer,
  } = event;

  const percent = getCapacityPercent(confirmed_attendees, capacity);
  const barColor = getCapacityBarColor(percent);
  const statusInfo = EVENT_STATUSES[status];
  const daysUntil = getDaysUntil(start_at);
  const isSoldOut = confirmed_attendees >= capacity;

  return (
    <Link to={`/eventos/${id}`} className={cn('block group', className)}>
      <article className="glass-card rounded-2xl overflow-hidden h-full flex flex-col">
        <div className="relative h-44 bg-linear-to-br from-violet-600/30 via-blue-600/20 to-cyan-500/30 overflow-hidden">
          <div className="absolute top-3 left-3 right-3 flex items-start justify-between">
            <Badge variant={(statusInfo?.color as 'default') || 'default'} dot>
              {statusInfo?.label}
            </Badge>
          </div>

          <div className="absolute bottom-0 left-0 right-0 bg-linear-to-t from-black/60 to-transparent p-3">
            <div className="flex items-center gap-1.5 text-white/80 text-xs">
              <Calendar size={12} />
              <span className="font-medium">{formatDateShort(start_at)}</span>
              <span className="text-white/40">•</span>
              <span>{daysUntil}</span>
            </div>
          </div>
        </div>

        <div className="p-5 flex flex-col flex-1 gap-3">
          <h3 className="font-display font-bold text-white text-base leading-snug group-hover:text-brand-400 transition-colors line-clamp-2">
            {name}
          </h3>

          <p className="text-white/50 text-sm font-body leading-relaxed line-clamp-2">
            {description}
          </p>

          <div className="flex flex-col gap-1.5 mt-auto">
            <div className="flex items-center gap-1.5 text-xs text-white/40">
              <MapPin size={12} className="shrink-0" />
              <span className="truncate">{location}</span>
            </div>

            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-1 text-white/40">
                  <Users size={11} />
                  <span>
                    {confirmed_attendees}/{capacity}
                  </span>
                </div>
                <span
                  className={cn(
                    'font-medium',
                    getCapacityBarColor(percent).replace('bg-', 'text-'),
                  )}
                >
                  {isSoldOut ? '🔴 Agotado' : `${percent}%`}
                </span>
              </div>
              <div className="h-1 bg-white/10 rounded-full overflow-hidden">
                <div
                  className={cn('h-full rounded-full transition-all duration-1000', barColor)}
                  style={{ width: `${percent}%` }}
                />
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-3 border-t border-white/5">
            <span className="text-xs text-white/40 truncate">Por {organizer.name}</span>
            <span className="flex items-center gap-1 text-brand-400 text-sm font-medium group-hover:gap-2 transition-all">
              Ver más <ArrowRight size={14} />
            </span>
          </div>
        </div>
      </article>
    </Link>
  );
}

export const EventCard = memo(EventCardImpl);
