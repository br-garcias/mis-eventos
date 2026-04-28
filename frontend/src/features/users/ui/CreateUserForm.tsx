import { ROLE_LABELS } from '@/features/shared/constants';
import { Button } from '@/features/shared/ui/Button';
import { FieldError } from '@/features/shared/ui/FieldError';
import { Input } from '@/features/shared/ui/Input';
import { Label } from '@/features/shared/ui/Label';
import { showToast } from '@/features/shared/utils/toast';
import { createUserSchema, type CreateUserFormData } from '@/features/users/schemas';
import { UsersService } from '@/features/users/services';
import type { Role } from '@/features/users/types';
import { formatApiError } from '@/lib/apiError';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';

interface CreateUserFormProps {
  roles: Role[];
  onSuccess: () => void;
  onCancel?: () => void;
}

export function CreateUserForm({ roles, onSuccess, onCancel }: CreateUserFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateUserFormData>({
    resolver: zodResolver(createUserSchema),
    defaultValues: { name: '', email: '', password: '', role_name: '' },
  });

  const onSubmit = async (data: CreateUserFormData) => {
    try {
      await UsersService.createUser(data);
      showToast('Usuario creado', 'success');
      onSuccess();
    } catch (err) {
      showToast(formatApiError(err), 'error');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
      <Input
        label="Nombre"
        labelClassName="mb-1.5"
        placeholder="Juan Pérez"
        autoComplete="name"
        error={errors.name?.message}
        {...register('name')}
      />
      <Input
        label="Email"
        labelClassName="mb-1.5"
        type="email"
        placeholder="juan@ejemplo.com"
        autoComplete="email"
        error={errors.email?.message}
        {...register('email')}
      />
      <Input
        label="Contraseña"
        labelClassName="mb-1.5"
        type="password"
        placeholder="••••••••"
        autoComplete="new-password"
        error={errors.password?.message}
        {...register('password')}
      />
      <div>
        <Label required className="mb-1.5">
          Rol
        </Label>
        <select
          {...register('role_name')}
          className="w-full glass border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-brand-400/50"
        >
          <option value="">Seleccionar rol</option>
          {roles.map((role) => (
            <option key={role.id} value={role.name}>
              {ROLE_LABELS[role.name as keyof typeof ROLE_LABELS] || role.name}
            </option>
          ))}
        </select>
        {errors.role_name && <FieldError message={errors.role_name.message} />}
      </div>
      <div className="flex gap-3 pt-2">
        <Button type="submit" className="flex-1" isLoading={isSubmitting}>
          Crear
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={onCancel ?? onSuccess}
          className="flex-1"
          disabled={isSubmitting}
        >
          Cancelar
        </Button>
      </div>
    </form>
  );
}
