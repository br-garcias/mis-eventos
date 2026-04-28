import { useAuthRedirect } from '@/features/auth/hooks/useAuthRedirect';
import { useAuthStore } from '@/features/auth/store';
import type { SessionFormData } from '@/features/events/schemas/session';
import { EventService } from '@/features/events/services';
import { useEventStore } from '@/features/events/store';
import type { EventSession } from '@/features/events/types';
import { EVENT_STATUSES } from '@/features/shared/constants';
import { useUIStore } from '@/features/shared/stores/ui-store';
import { Avatar, AvatarFallback } from '@/features/shared/ui/Avatar';
import { Badge } from '@/features/shared/ui/Badge';
import { Button } from '@/features/shared/ui/Button';
import { EmptyState } from '@/features/shared/ui/EmptyState';
import { Spinner } from '@/features/shared/ui/Spinner';
import { showToast } from '@/features/shared/utils/toast';
import { formatApiError } from '@/lib/apiError';
import { getAvailableSpots, getCapacityBarColor, getCapacityPercent } from '@/lib/capacity';
import { cn } from '@/lib/cn';
import { formatDate } from '@/lib/formatters';
import { getInitials } from '@/lib/initials';
import {
  ArrowLeft,
  Calendar,
  CheckCircle,
  Edit,
  MapPin,
  Plus,
  Share2,
  Trash2,
  Users,
  XCircle,
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { EventAttendeesView } from './EventAttendeesView';
import { SessionCard } from './SessionCard';
import { SessionForm } from './SessionForm';

export function EventDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const currentEvent = useEventStore((s) => s.currentEvent);
  const isLoading = useEventStore((s) => s.isLoading);
  const fetchEvent = useEventStore((s) => s.fetchEvent);
  const deleteEvent = useEventStore((s) => s.deleteEvent);
  const createSession = useEventStore((s) => s.createSession);
  const updateSession = useEventStore((s) => s.updateSession);
  const deleteSession = useEventStore((s) => s.deleteSession);
  const user = useAuthStore((s) => s.user);
  const isOrganizer = useAuthStore((s) => s.isOrganizer);
  const isAdmin = useAuthStore((s) => s.isAdmin);
  const openDialog = useUIStore((s) => s.openDialog);
  const confirmDialog = useUIStore((s) => s.confirmDialog);
  const { redirectToAuth } = useAuthRedirect();

  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (id) {
      fetchEvent(id);
      window.scrollTo(0, 0);
    }
  }, [id, fetchEvent]);

  if (isLoading)
    return (
      <div className="min-h-screen flex items-center justify-center pt-20">
        <div className="text-center">
          <Spinner size="lg" className="mx-auto mb-4" />
          <p className="text-white/40 font-body text-sm">Cargando evento...</p>
        </div>
      </div>
    );

  if (!currentEvent)
    return (
      <div className="min-h-screen flex items-center justify-center pt-20">
        <EmptyState
          icon="😕"
          title="Evento no encontrado"
          description="El evento que buscas no existe o fue eliminado."
          action={<Button onClick={() => navigate('/')}>Volver al inicio</Button>}
        />
      </div>
    );

  const e = currentEvent;
  const isSoldOut = e.confirmed_attendees >= e.capacity;
  const userIsOrganizer = isOrganizer();
  const userIsAdmin = isAdmin();
  const eventOrganizerId = e.organizer?.id ?? e.organizer_id;
  const isOwner = user?.id === eventOrganizerId;
  const canEdit = userIsOrganizer && (userIsAdmin || isOwner);

  const isCancelled = e.status === 'cancelled';
  const canRegister = !canEdit && !isOwner;
  const statusInfo = EVENT_STATUSES[e.status];
  const percent = getCapacityPercent(e.confirmed_attendees, e.capacity);

  const handleRegister = async () => {
    if (!user) {
      navigate('/login');
      return;
    }
    setActionLoading(true);
    try {
      if (e.is_registered) {
        await EventService.unregister(e.id);
        await fetchEvent(e.id);
        showToast('Registro cancelado exitosamente', 'info');
      } else {
        if (isSoldOut) {
          showToast('El evento está agotado', 'error');
          setActionLoading(false);
          return;
        }
        if (!canRegister) {
          showToast('No puedes registrarte a este evento', 'error');
          setActionLoading(false);
          return;
        }
        await EventService.register(e.id);
        await fetchEvent(e.id);
        showToast('¡Te registraste exitosamente! 🎉', 'success');
      }
    } catch (err) {
      showToast(formatApiError(err), 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    await deleteEvent(e.id);
    showToast('Evento eliminado', 'info');
    navigate('/');
  };

  const handleOpenAttendees = () => {
    openDialog('Asistentes', '', <EventAttendeesView eventId={e.id} />, 'sm:max-w-lg');
  };

  const handleShare = () => {
    navigator.clipboard?.writeText(window.location.href);
    showToast('¡Enlace copiado!', 'success');
  };

  const handlePublish = async () => {
    confirmDialog(
      '¿Publicar evento?',
      `El evento "${e.name}" será visible para todos los asistentes.`,
      async () => {
        setActionLoading(true);
        try {
          await EventService.publish(e.id);
          await fetchEvent(e.id);
          showToast('Evento publicado', 'success');
        } catch (err) {
          showToast(formatApiError(err), 'error');
        } finally {
          setActionLoading(false);
        }
      },
    );
  };

  const handleCancelEvent = async () => {
    confirmDialog(
      '¿Cancelar evento?',
      `El evento "${e.name}" ya no será visible para los asistentes.`,
      async () => {
        setActionLoading(true);
        try {
          await EventService.cancel(e.id);
          await fetchEvent(e.id);
          showToast('Evento cancelado', 'info');
        } catch (err) {
          showToast(formatApiError(err), 'error');
        } finally {
          setActionLoading(false);
        }
      },
    );
  };

  const handleOpenCreateSession = () => {
    openDialog(
      'Nueva sesión',
      'Agrega los detalles de la sesión',
      <SessionForm
        eventStartAt={e.start_at}
        eventEndAt={e.end_at}
        onSubmit={async (data: SessionFormData) => {
          try {
            await createSession(e.id, {
              ...data,
              start_at: data.start_at ? `${data.start_at}:00` : '',
              end_at: data.end_at ? `${data.end_at}:00` : '',
              speaker_bio: data.speaker_bio || '',
            });
            await fetchEvent(e.id);
            showToast('Sesión creada exitosamente', 'success');
            useUIStore.getState().closeDialog();
          } catch (err) {
            showToast(formatApiError(err), 'error');
          }
        }}
        onCancel={() => useUIStore.getState().closeDialog()}
        isLoading={isLoading}
      />,
      'sm:max-w-lg',
    );
  };

  const handleOpenEditSession = (session: EventSession) => {
    openDialog(
      'Editar sesión',
      'Actualiza los detalles de la sesión',
      <SessionForm
        initialData={session}
        eventStartAt={e.start_at}
        eventEndAt={e.end_at}
        onSubmit={async (data: SessionFormData) => {
          try {
            await updateSession(e.id, session.id, {
              ...data,
              start_at: data.start_at ? `${data.start_at}:00` : '',
              end_at: data.end_at ? `${data.end_at}:00` : '',
            });
            await fetchEvent(e.id);
            showToast('Sesión actualizada exitosamente', 'success');
            useUIStore.getState().closeDialog();
          } catch (err) {
            showToast(formatApiError(err), 'error');
          }
        }}
        onCancel={() => useUIStore.getState().closeDialog()}
        isLoading={isLoading}
      />,
      'sm:max-w-lg',
    );
  };

  const handleOpenDeleteSession = (session: EventSession) => {
    confirmDialog(
      '¿Eliminar sesión?',
      `La sesión "${session.title}" será eliminada permanentemente.`,
      async () => {
        try {
          await deleteSession(e.id, session.id);
          await fetchEvent(e.id);
          showToast('Sesión eliminada', 'info');
        } catch (err) {
          showToast(formatApiError(err), 'error');
        }
      },
    );
  };

  return (
    <div className="min-h-screen pb-10">
      {/* ——— HERO BANNER ——— */}
      <div className="relative h-56 sm:h-72 bg-linear-to-br from-violet-600/30 via-blue-600/20 to-cyan-500/30 overflow-hidden">
        <div className="absolute inset-0 hero-grid opacity-40" />
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-[180px] opacity-10">🚀</span>
        </div>
        <div className="absolute inset-0 bg-linear-to-t from-surface to-transparent" />

        <div className="absolute top-32 left-1/2 -translate-x-40">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 glass px-4 py-2 rounded-xl text-white/70 hover:text-white text-sm font-medium transition-all"
          >
            <ArrowLeft size={16} /> Volver
          </button>
        </div>

        {canEdit && (
          <div className="absolute top-32 left-1/2 translate-x-8 flex gap-2">
            {e.status === 'draft' && (
              <button
                onClick={handlePublish}
                disabled={actionLoading}
                className="flex items-center gap-2 glass px-4 py-2 rounded-xl text-brand-400 hover:text-brand-300 hover:border-brand-400/30 text-sm font-medium transition-all disabled:opacity-50"
              >
                {actionLoading ? (
                  '...'
                ) : (
                  <>
                    <CheckCircle size={14} /> Publicar
                  </>
                )}
              </button>
            )}
            {e.status === 'published' && (
              <button
                onClick={handleCancelEvent}
                disabled={actionLoading}
                className="flex items-center gap-2 glass px-4 py-2 rounded-xl text-red-400 hover:text-red-300 hover:border-red-400/30 text-sm font-medium transition-all disabled:opacity-50"
              >
                {actionLoading ? (
                  '...'
                ) : (
                  <>
                    <XCircle size={14} /> Cancelar
                  </>
                )}
              </button>
            )}
            <Link
              to={`/eventos/${e.id}/editar`}
              className="flex items-center gap-2 glass px-4 py-2 rounded-xl text-white/70 hover:text-white text-sm font-medium transition-all"
            >
              <Edit size={14} /> Editar
            </Link>
            <button
              onClick={() =>
                confirmDialog(
                  '¿Eliminar evento?',
                  `Esta acción es irreversible. Se eliminará el evento "${e.name}" y todos sus datos.`,
                  handleDelete,
                )
              }
              className="flex items-center gap-2 glass px-4 py-2 rounded-xl text-red-400 hover:text-red-300 hover:border-red-400/30 text-sm font-medium transition-all"
            >
              <Trash2 size={14} /> Eliminar
            </button>
          </div>
        )}
      </div>

      {/* ——— CONTENT ——— */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <Badge variant={(statusInfo?.color as 'default') || 'default'} dot>
                  {statusInfo?.label}
                </Badge>
              </div>
              <h1 className="font-display font-black text-3xl sm:text-4xl text-white leading-tight">
                {e.name}
              </h1>
              <div className="flex flex-wrap gap-4 text-sm text-white/50">
                <span className="flex items-center gap-1.5">
                  <Calendar size={14} className="text-brand-400" /> {formatDate(e.start_at)}
                  {e.end_at && e.end_at !== e.start_at ? ` — ${formatDate(e.end_at)}` : ''}
                </span>
                <span className="flex items-center gap-1.5">
                  <MapPin size={14} className="text-brand-400" /> {e.location}
                </span>
              </div>
            </div>

            <div className="glass rounded-2xl p-6">
              <h2 className="font-display font-bold text-lg text-white mb-4">Sobre el evento</h2>
              <p className="text-white/60 font-body leading-relaxed text-sm whitespace-pre-line">
                {e.description}
              </p>
            </div>

            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-display font-bold text-xl text-white flex items-center gap-2">
                  Sesiones
                  {e.sessions.length > 0 && <Badge variant="default">{e.sessions.length}</Badge>}
                </h2>
                {canEdit && !isCancelled && (
                  <Button
                    size="sm"
                    leftIcon={<Plus size={14} />}
                    onClick={handleOpenCreateSession}
                    className="rounded-lg bg-orange-500 hover:bg-orange-400 text-white border-orange-500 hover:border-orange-400"
                  >
                    Agregar sesión
                  </Button>
                )}
              </div>
              {e.sessions.length === 0 ? (
                <div className="glass rounded-2xl p-8 text-center">
                  <p className="text-white/30 font-body text-sm">
                    Las sesiones aún no han sido publicadas.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {e.sessions.map((session) => (
                    <SessionCard
                      key={session.id}
                      session={session}
                      onEdit={canEdit && !isCancelled ? handleOpenEditSession : undefined}
                      onDelete={canEdit && !isCancelled ? handleOpenDeleteSession : undefined}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* ——— SIDEBAR ——— */}
          <div className="space-y-4">
            <div className="glass rounded-2xl p-6 space-y-5 sticky top-24">
              <div>
                <p className="text-white/40 text-xs font-body mb-1">Precio</p>
                <p className="font-display font-black text-3xl text-green-400">Gratis</p>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-white/50 font-body flex items-center gap-1.5">
                    <Users size={14} /> Asistentes
                  </span>
                  {canEdit ? (
                    <button
                      onClick={handleOpenAttendees}
                      className="text-white font-medium hover:text-brand-400 transition-colors"
                    >
                      {e.confirmed_attendees} / {e.capacity}
                    </button>
                  ) : (
                    <span className="text-white font-medium">
                      {e.confirmed_attendees} / {e.capacity}
                    </span>
                  )}
                </div>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className={cn(
                      'h-full rounded-full transition-all',
                      getCapacityBarColor(percent),
                    )}
                    style={{ width: `${percent}%` }}
                  />
                </div>
                <p
                  className={cn(
                    'text-xs font-body',
                    isSoldOut
                      ? 'text-red-400'
                      : percent >= 70
                        ? 'text-amber-400'
                        : 'text-green-400',
                  )}
                >
                  {getAvailableSpots(e.confirmed_attendees, e.capacity)}
                </p>
              </div>

              {e.status === 'cancelled' ? (
                <div className="flex items-center gap-2 p-3 bg-red-500/10 rounded-xl border border-red-500/20">
                  <XCircle size={16} className="text-red-400" />
                  <span className="text-sm text-red-400 font-body">Evento cancelado</span>
                </div>
              ) : e.is_registered ? (
                <div className="space-y-3">
                  <div className="flex items-center gap-2 p-3 bg-green-500/10 rounded-xl border border-green-500/20">
                    <CheckCircle size={16} className="text-green-400" />
                    <span className="text-sm text-green-400 font-body">¡Estás registrado!</span>
                  </div>
                  <Button
                    variant="destructive"
                    className="w-full bg-red-500/10 hover:bg-red-500/20 text-red-400 border-red-500/20"
                    isLoading={actionLoading}
                    onClick={handleRegister}
                  >
                    Cancelar registro
                  </Button>
                </div>
              ) : !user ? (
                <div className="space-y-2">
                  <p className="text-sm text-white/50 font-body text-center">
                    Inicia sesión para registrarte
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      className="flex-1"
                      onClick={() => redirectToAuth('/login')}
                    >
                      Iniciar sesión
                    </Button>
                    <Button
                      className="flex-1 bg-brand-400 hover:bg-brand-300 text-white border-0"
                      onClick={() => redirectToAuth('/registro')}
                    >
                      Registrarse
                    </Button>
                  </div>
                </div>
              ) : !canRegister ? (
                <div className="p-3 bg-white/5 rounded-xl border border-white/10 text-center">
                  <p className="text-sm text-white/50 font-body">
                    {canEdit ? 'Eres el organizador' : 'No puedes registrarte'}
                  </p>
                </div>
              ) : (
                <Button
                  className="w-full bg-brand-400 hover:bg-brand-300 text-white border-0"
                  disabled={isSoldOut || e.status !== 'published'}
                  isLoading={actionLoading}
                  onClick={handleRegister}
                >
                  {isSoldOut ? 'Evento Agotado' : 'Registrarme'}
                </Button>
              )}

              <Button
                variant="ghost"
                className="w-full text-white/60 hover:text-white hover:bg-white/5"
                leftIcon={<Share2 size={14} />}
                onClick={handleShare}
              >
                Compartir evento
              </Button>

              <hr className="border-white/10" />

              <div>
                <p className="text-xs text-white/40 font-body mb-3">Organizado por</p>
                <div className="flex items-center gap-3">
                  <Avatar>
                    <AvatarFallback className="text-xs">
                      {getInitials(e.organizer.name)}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="text-sm font-semibold text-white">{e.organizer.name}</p>
                    <p className="text-xs text-white/40">Organizador</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
