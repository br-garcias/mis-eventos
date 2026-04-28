import { z } from 'zod';

export const createUserSchema = z.object({
  name: z.string().min(3, 'Mínimo 3 caracteres'),
  email: z.string().email('Email inválido'),
  password: z.string().min(6, 'Mínimo 6 caracteres'),
  role_name: z.string().min(1, 'Selecciona un rol'),
});

export type CreateUserFormData = z.infer<typeof createUserSchema>;
