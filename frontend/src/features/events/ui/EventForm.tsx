import { eventSchema, type EventFormData } from '@/features/events/schemas';
import type { EventDetail } from '@/features/events/types';
import { Button } from '@/features/shared/ui/Button';
import { Input } from '@/features/shared/ui/Input';
import { Textarea } from '@/features/shared/ui/Textarea';
import { getDefaultEndTime, getMinDateTime } from '@/lib/dates';
import { zodResolver } from '@hookform/resolvers/zod';
import { Save, X } from 'lucide-react';
import { ChangeEvent, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

interface EventFormProps {
  initialData?: EventDetail;
  onSubmit: (data: EventFormData) => void;
  onCancel?: () => void;
  isLoading: boolean;
}

export function EventForm({ initialData, onSubmit, onCancel, isLoading }: EventFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    watch,
    setValue,
    formState: { errors },
  } = useForm<z.input<typeof eventSchema>>({
    resolver: zodResolver(eventSchema),
    defaultValues: {
      name: '',
      description: '',
      capacity: 100,
      start_at: '',
      end_at: '',
      location: '',
    },
  });

  useEffect(() => {
    if (initialData) {
      reset({
        name: initialData.name,
        description: initialData.description,
        capacity: initialData.capacity,
        start_at: initialData.start_at ? initialData.start_at.slice(0, 16) : '',
        end_at: initialData.end_at ? initialData.end_at.slice(0, 16) : '',
        location: initialData.location,
      });
    }
  }, [initialData, reset]);

  const handleSubmitForm = handleSubmit((data) => {
    onSubmit({
      ...data,
      capacity: Number(data.capacity),
    } as EventFormData);
  });

  return (
    <form onSubmit={handleSubmitForm} className="space-y-6">
      <div className="space-y-4">
        <h3 className="font-display text-base font-semibold text-white/80 pb-2 border-b border-white/10">
          Información básica
        </h3>
        <Input
          label="Título del evento"
          labelClassName="mb-1.5"
          placeholder="Ej: Colombia AI Summit 2025"
          error={errors.name?.message}
          required
          {...register('name')}
        />
        <Textarea
          label="Descripción"
          labelClassName="mb-1.5"
          placeholder="Descripción detallada del evento, agenda, ponentes destacados..."
          rows={5}
          error={errors.description?.message}
          required
          {...register('description')}
        />
      </div>

      <div className="space-y-4">
        <h3 className="font-display text-base font-semibold text-white/80 pb-2 border-b border-white/10">
          Fecha y lugar
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Fecha y hora de inicio"
            labelClassName="mb-1.5"
            type="datetime-local"
            min={getMinDateTime()}
            error={errors.start_at?.message}
            required
            {...register('start_at', {
              onChange: (e: ChangeEvent<HTMLInputElement>) => {
                const endAt = watch('end_at');
                if (!endAt) {
                  setValue('end_at', getDefaultEndTime(e.target.value));
                }
              },
            })}
          />
          <Input
            label="Fecha y hora de fin"
            labelClassName="mb-1.5"
            type="datetime-local"
            min={getMinDateTime()}
            error={errors.end_at?.message}
            {...register('end_at')}
          />
        </div>
        <Input
          label="Lugar / Venue"
          labelClassName="mb-1.5"
          placeholder="Ej: Centro de Convenciones Ágora, Bogotá"
          error={errors.location?.message}
          required
          {...register('location')}
        />
      </div>

      <div className="space-y-4">
        <h3 className="font-display text-base font-semibold text-white/80 pb-2 border-b border-white/10">
          Capacidad
        </h3>
        <Input
          label="Capacidad máxima"
          labelClassName="mb-1.5"
          type="number"
          min="1"
          error={errors.capacity?.message}
          required
          {...register('capacity')}
        />
      </div>

      <div className="flex items-center gap-3 pt-4 border-t border-white/10">
        <Button
          type="submit"
          isLoading={isLoading}
          leftIcon={<Save size={16} />}
          className="flex-1"
        >
          {initialData ? 'Guardar cambios' : 'Crear evento'}
        </Button>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel} leftIcon={<X size={16} />}>
            Cancelar
          </Button>
        )}
      </div>
    </form>
  );
}
