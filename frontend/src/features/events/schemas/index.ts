import { z } from 'zod';

export const eventSchema = z
  .object({
    name: z.string().min(5, 'Mínimo 5 caracteres').max(100, 'Máximo 100 caracteres'),
    description: z.string().min(50, 'Mínimo 50 caracteres'),
    capacity: z.union([z.number(), z.string()]).transform((val) => Number(val)),
    start_at: z.string().min(1, 'Fecha y hora de inicio requerida'),
    end_at: z.string().optional(),
    location: z.string().min(5, 'Mínimo 5 caracteres'),
  })
  .refine((data) => new Date(data.start_at) > new Date(), {
    message: 'La fecha de inicio no puede ser en el pasado',
    path: ['start_at'],
  })
  .refine((data) => !data.end_at || new Date(data.end_at) > new Date(data.start_at), {
    message: 'La fecha de fin debe ser posterior a la de inicio',
    path: ['end_at'],
  })
  .refine((data) => data.capacity >= 1 && data.capacity <= 100000, {
    message: 'La capacidad debe ser entre 1 y 100,000',
    path: ['capacity'],
  });

export type EventFormData = z.infer<typeof eventSchema>;
