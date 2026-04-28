import type { EventSession } from '@/features/events/types';
import { Avatar, AvatarFallback } from '@/features/shared/ui/Avatar';
import { Button } from '@/features/shared/ui/Button';
import { formatDateTime } from '@/lib/formatters';
import { getInitials } from '@/lib/initials';
import { Edit, Trash2 } from 'lucide-react';

interface SessionCardProps {
  session: EventSession;
  onEdit?: (session: EventSession) => void;
  onDelete?: (session: EventSession) => void;
}

export function SessionCard({ session, onEdit, onDelete }: SessionCardProps) {
  const { title, description, speaker_name, speaker_bio, start_at, end_at } = session;
  const hasActions = onEdit || onDelete;

  return (
    <div className="glass-card rounded-xl p-5 flex flex-col gap-4 relative">
      {/* Action buttons */}
      {hasActions && (
        <div className="absolute top-3 right-3 flex gap-1">
          {onEdit && (
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={() => onEdit(session)}
              className="text-white/40 hover:text-brand-400"
            >
              <Edit size={14} />
            </Button>
          )}
          {onDelete && (
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={() => onDelete(session)}
              className="text-white/40 hover:text-red-400"
            >
              <Trash2 size={14} />
            </Button>
          )}
        </div>
      )}

      {/* Time strip */}
      <div className="flex items-center gap-3">
        <div className="flex flex-col items-center bg-brand-400/10 border border-brand-400/20 rounded-lg px-3 py-2 shrink-0">
          <span className="text-brand-400 font-display font-bold text-base leading-none">
            {formatDateTime(start_at)}
          </span>
          <span className="text-white/30 text-xs mt-0.5">— {formatDateTime(end_at)}</span>
        </div>
        <div className="flex-1">
          <h4 className="font-display font-semibold text-white text-sm leading-snug pr-16">
            {title}
          </h4>
        </div>
      </div>

      {/* Description */}
      <p className="text-white/50 text-xs font-body leading-relaxed line-clamp-2">{description}</p>

      {/* Speaker */}
      <div className="flex items-center gap-3 p-3 bg-white/3 rounded-lg border border-white/5">
        <Avatar>
          <AvatarFallback className="text-xs">{getInitials(speaker_name)}</AvatarFallback>
        </Avatar>
        <div>
          <p className="text-sm font-semibold text-white leading-none">{speaker_name}</p>
          {speaker_bio && <p className="text-xs text-white/40 mt-0.5">{speaker_bio}</p>}
        </div>
      </div>
    </div>
  );
}
