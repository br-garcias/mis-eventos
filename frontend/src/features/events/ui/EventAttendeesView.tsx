import { EventService } from '@/features/events/services';
import type { Attendee } from '@/features/events/types';
import { Avatar, AvatarFallback } from '@/features/shared/ui/Avatar';
import { EmptyState } from '@/features/shared/ui/EmptyState';
import { Spinner } from '@/features/shared/ui/Spinner';
import { showToast } from '@/features/shared/utils/toast';
import { formatApiError } from '@/lib/apiError';
import { getInitials } from '@/lib/initials';
import { Clock, UserCheck, UserX } from 'lucide-react';
import { useEffect, useState } from 'react';

interface EventAttendeesViewProps {
  eventId: string;
}

export function EventAttendeesView({ eventId }: EventAttendeesViewProps) {
  const [attendees, setAttendees] = useState<Attendee[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (eventId) {
      loadAttendees();
    }
  }, [eventId]);

  const loadAttendees = async () => {
    setLoading(true);
    try {
      const data = await EventService.getAttendees(eventId);
      setAttendees(data.items);
    } catch (err) {
      showToast(formatApiError(err), 'error');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'confirmed':
        return <UserCheck size={14} className="text-green-400" />;
      case 'cancelled':
        return <UserX size={14} className="text-red-400" />;
      case 'waitlist':
        return <Clock size={14} className="text-amber-400" />;
      default:
        return null;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'Confirmado';
      case 'cancelled':
        return 'Cancelado';
      case 'waitlist':
        return 'Lista de espera';
      default:
        return status;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <Spinner />
      </div>
    );
  }

  if (attendees.length === 0) {
    return (
      <EmptyState
        icon="👥"
        title="Sin asistentes"
        description="Aún no hay personas registradas en este evento"
      />
    );
  }

  return (
    <div className="space-y-2 max-h-96 overflow-y-auto">
      {attendees.map((attendee) => (
        <div key={attendee.id} className="flex items-center justify-between p-3 glass rounded-xl">
          <div className="flex items-center gap-3">
            <Avatar>
              <AvatarFallback className="text-xs">{getInitials(attendee.user.name)}</AvatarFallback>
            </Avatar>
            <div>
              <p className="text-sm font-medium text-white">{attendee.user.name}</p>
              <p className="text-xs text-white/40">{attendee.user.email}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {getStatusIcon(attendee.status)}
            <span className="text-xs text-white/60">{getStatusLabel(attendee.status)}</span>
          </div>
        </div>
      ))}
      <div className="mt-4 pt-4 border-t border-white/10">
        <p className="text-sm text-white/40">
          Total: {attendees.filter((a) => a.status === 'confirmed').length} confirmados
          {attendees.filter((a) => a.status === 'waitlist').length > 0 &&
            ` · ${attendees.filter((a) => a.status === 'waitlist').length} en espera`}
        </p>
      </div>
    </div>
  );
}
