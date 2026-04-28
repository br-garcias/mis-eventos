import { useAuthStore } from '@/features/auth/store';
import type { EventFormData } from '@/features/events/schemas';
import { EventService } from '@/features/events/services';
import { useEventStore } from '@/features/events/store';
import { showToast } from '@/features/shared/utils/toast';
import { formatApiError } from '@/lib/apiError';
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { EventForm } from './EventForm';

export function EditEventPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { fetchEvent, currentEvent } = useEventStore();
  const { user, isOrganizer } = useAuthStore();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (id) fetchEvent(id);
  }, [id, fetchEvent]);

  if (!user || !isOrganizer()) {
    navigate('/login');
    return null;
  }

  const handleSubmit = async (data: EventFormData) => {
    if (!id) return;
    setLoading(true);
    try {
      await EventService.update(id, data);
      showToast('Evento actualizado ✓', 'success');
      navigate(`/eventos/${id}`);
    } catch (err) {
      showToast(formatApiError(err), 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen pt-28 pb-20">
      <div className="max-w-2xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="font-display font-black text-3xl text-white">Editar evento</h1>
          <p className="text-white/40 font-body text-sm mt-1">{currentEvent?.name}</p>
        </div>
        <div className="glass rounded-2xl p-6 sm:p-8">
          {currentEvent ? (
            <EventForm
              initialData={currentEvent}
              onSubmit={handleSubmit}
              onCancel={() => navigate(-1)}
              isLoading={loading}
            />
          ) : (
            <div className="flex justify-center py-12">
              <div className="animate-spin h-8 w-8 rounded-full border-2 border-white/10 border-t-brand-400" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
