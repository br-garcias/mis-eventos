import { useAuthStore } from '@/features/auth/store';
import type { EventFormData } from '@/features/events/schemas';
import { EventService } from '@/features/events/services';
import { showToast } from '@/features/shared/utils/toast';
import { formatApiError } from '@/lib/apiError';
import { Plus } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { EventForm } from './EventForm';

export function CreateEventPage() {
  const navigate = useNavigate();
  const { user, isOrganizer } = useAuthStore();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user || !isOrganizer()) navigate('/login');
  }, [user]);

  const handleSubmit = async (data: EventFormData) => {
    setLoading(true);
    try {
      const newEvent = await EventService.create(data);
      showToast('¡Evento creado exitosamente! 🎉', 'success');
      navigate(`/eventos/${newEvent.id}`);
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
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-brand-400/10 border border-brand-400/20 flex items-center justify-center">
              <Plus size={20} className="text-brand-400" />
            </div>
            <h1 className="font-display font-black text-3xl text-white">Crear evento</h1>
          </div>
          <p className="text-white/40 font-body text-sm ml-13">
            Completa la información para publicar tu evento
          </p>
        </div>

        <div className="glass rounded-2xl p-6 sm:p-8">
          <EventForm onSubmit={handleSubmit} onCancel={() => navigate(-1)} isLoading={loading} />
        </div>
      </div>
    </div>
  );
}
