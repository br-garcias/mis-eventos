import { z } from 'zod';

export const __name__Schema = z.object({
  // TODO: Definir campos del esquema
  name: z.string().min(1, 'El nombre es requerido'),
});

// Type exports
export type __Name__FormValues = z.infer<typeof __name__Schema>;
