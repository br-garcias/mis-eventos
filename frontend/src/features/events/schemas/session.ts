import { z } from 'zod';

export const sessionSchema = z
  .object({
    title: z.string().min(5, 'Mínimo 5 caracteres').max(200, 'Máximo 200 caracteres'),
    description: z.string().min(10, 'Mínimo 10 caracteres').max(2000, 'Máximo 2000 caracteres'),
    speaker_name: z.string().min(3, 'Mínimo 3 caracteres').max(100, 'Máximo 100 caracteres'),
    speaker_bio: z.string().max(500, 'Máximo 500 caracteres').optional(),
    start_at: z.string().min(1, 'Fecha y hora de inicio requerida'),
    end_at: z.string().min(1, 'Fecha y hora de fin requerida'),
  })
  .refine((data) => new Date(data.end_at) > new Date(data.start_at), {
    message: 'La hora de fin debe ser posterior a la hora de inicio',
    path: ['end_at'],
  })
  .refine(
    (data) => {
      const start = new Date(data.start_at).getTime();
      const end = new Date(data.end_at).getTime();
      return end > start;
    },
    {
      message: 'La sesión debe durar al menos 1 minuto',
      path: ['end_at'],
    },
  );

export const createSessionSchema = (eventStartAt?: string, eventEndAt?: string) => {
  let schema = sessionSchema;

  const startValid = eventStartAt && !isNaN(Date.parse(eventStartAt));
  const endValid = eventEndAt && !isNaN(Date.parse(eventEndAt));

  if (startValid) {
    schema = schema.refine((data) => new Date(data.start_at) >= new Date(eventStartAt!), {
      message: `La sesión debe iniciar después del inicio del evento`,
      path: ['start_at'],
    });
  }

  if (endValid) {
    schema = schema.refine((data) => new Date(data.end_at) <= new Date(eventEndAt!), {
      message: `La sesión debe terminar antes del fin del evento`,
      path: ['end_at'],
    });
  }

  return schema;
};

export type SessionFormData = z.infer<typeof sessionSchema>;
