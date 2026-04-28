import { createSessionSchema, type SessionFormData } from '@/features/events/schemas/session';
import type { EventSession } from '@/features/events/types';
import { Button } from '@/features/shared/ui/Button';
import { Input } from '@/features/shared/ui/Input';
import { Textarea } from '@/features/shared/ui/Textarea';
import { getDefaultEndTime, getMinDateTime } from '@/lib/dates';
import { zodResolver } from '@hookform/resolvers/zod';
import { ArrowLeft, ArrowRight, Save, X } from 'lucide-react';
import { ChangeEvent, useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';

interface SessionFormProps {
  initialData?: EventSession;
  eventStartAt?: string;
  eventEndAt?: string;
  onSubmit: (data: SessionFormData) => void;
  onCancel?: () => void;
  isLoading: boolean;
}

export function SessionForm({
  initialData,
  eventStartAt,
  eventEndAt,
  onSubmit,
  onCancel,
  isLoading,
}: SessionFormProps) {
  const [step, setStep] = useState(1);
  const schema = createSessionSchema(eventStartAt, eventEndAt);
  const {
    register,
    handleSubmit,
    reset,
    trigger,
    watch,
    setValue,
    formState: { errors },
  } = useForm<SessionFormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      title: '',
      description: '',
      speaker_name: '',
      speaker_bio: '',
      start_at: '',
      end_at: '',
    },
  });

  useEffect(() => {
    if (initialData) {
      reset({
        title: initialData.title,
        description: initialData.description,
        speaker_name: initialData.speaker_name,
        speaker_bio: initialData.speaker_bio || '',
        start_at: initialData.start_at ? initialData.start_at.slice(0, 16) : '',
        end_at: initialData.end_at ? initialData.end_at.slice(0, 16) : '',
      });
    }
  }, [initialData, reset]);

  const handleNext = async () => {
    const isValid = await trigger(['title', 'description', 'start_at', 'end_at']);
    if (isValid) setStep(2);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Progress indicator */}
      <div className="flex items-center gap-2 mb-6">
        <div
          className={`flex items-center gap-2 ${step >= 1 ? 'text-orange-400' : 'text-white/30'}`}
        >
          <div
            className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${step >= 1 ? 'bg-orange-500 text-white' : 'bg-white/10'}`}
          >
            1
          </div>
          <span className="text-sm">Sesión</span>
        </div>
        <div className="flex-1 h-px bg-white/10" />
        <div
          className={`flex items-center gap-2 ${step >= 2 ? 'text-orange-400' : 'text-white/30'}`}
        >
          <div
            className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${step >= 2 ? 'bg-orange-500 text-white' : 'bg-white/10'}`}
          >
            2
          </div>
          <span className="text-sm">Ponente</span>
        </div>
      </div>

      {/* Step 1: Session Info */}
      {step === 1 && (
        <div className="space-y-5">
          <div>
            <h3 className="font-display text-base font-semibold text-white mb-4">
              Información de la sesión
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-white/70 mb-1.5">Título de la sesión</label>
                <Input
                  placeholder="Ej: Taller de FastAPI"
                  error={errors.title?.message}
                  {...register('title')}
                />
              </div>
              <div>
                <label className="block text-sm text-white/70 mb-1.5">Descripción</label>
                <Textarea
                  placeholder="Descripción detallada de la sesión, temas a cubrir..."
                  rows={3}
                  error={errors.description?.message}
                  {...register('description')}
                />
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-display text-base font-semibold text-white mb-4">Horario</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-white/70 mb-1.5">Hora de inicio</label>
                <Input
                  type="datetime-local"
                  min={getMinDateTime()}
                  error={errors.start_at?.message}
                  {...register('start_at', {
                    onChange: (e: ChangeEvent<HTMLInputElement>) => {
                      const endAt = watch('end_at');
                      if (!endAt) {
                        setValue('end_at', getDefaultEndTime(e.target.value));
                      }
                    },
                  })}
                />
              </div>
              <div>
                <label className="block text-sm text-white/70 mb-1.5">Hora de fin</label>
                <Input
                  type="datetime-local"
                  min={getMinDateTime()}
                  error={errors.end_at?.message}
                  {...register('end_at')}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Step 2: Speaker Info */}
      {step === 2 && (
        <div className="space-y-5">
          <div>
            <h3 className="font-display text-base font-semibold text-white mb-4">
              Información del ponente
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-white/70 mb-1.5">Nombre del ponente</label>
                <Input
                  placeholder="Ej: Carlos Martínez"
                  error={errors.speaker_name?.message}
                  {...register('speaker_name')}
                />
              </div>
              <div>
                <label className="block text-sm text-white/70 mb-1.5">
                  Biografía <span className="text-white/30">(opcional)</span>
                </label>
                <Textarea
                  placeholder="Breve descripción del ponente, experiencia, empresa..."
                  rows={3}
                  error={errors.speaker_bio?.message}
                  {...register('speaker_bio')}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-3 pt-4 border-t border-white/10">
        {step === 1 ? (
          <Button
            type="button"
            onClick={handleNext}
            className="flex-1 bg-orange-500 hover:bg-orange-400 text-white"
            rightIcon={<ArrowRight size={16} />}
          >
            Siguiente
          </Button>
        ) : (
          <>
            <Button
              type="button"
              variant="outline"
              onClick={() => setStep(1)}
              leftIcon={<ArrowLeft size={16} />}
            >
              Atrás
            </Button>
            <Button
              type="submit"
              isLoading={isLoading}
              leftIcon={<Save size={16} />}
              className="flex-1"
            >
              {initialData ? 'Guardar cambios' : 'Crear sesión'}
            </Button>
          </>
        )}
        {onCancel && step === 1 && (
          <Button type="button" variant="outline" onClick={onCancel} leftIcon={<X size={16} />}>
            Cancelar
          </Button>
        )}
      </div>
    </form>
  );
}
