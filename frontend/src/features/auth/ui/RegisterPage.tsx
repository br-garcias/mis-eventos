import { useAuthRedirect } from '@/features/auth/hooks/useAuthRedirect';
import { registerSchema, type RegisterFormData } from '@/features/auth/schemas';
import { useAuthStore } from '@/features/auth/store';
import { Button } from '@/features/shared/ui/Button';
import { Input } from '@/features/shared/ui/Input';
import { showToast } from '@/features/shared/utils/toast';
import { zodResolver } from '@hookform/resolvers/zod';
import { ArrowRight, Eye, EyeOff, Lock, Mail, User } from 'lucide-react';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { AuthLayout } from './AuthLayout';

export function RegisterPage() {
  const navigate = useNavigate();
  const { resolveReturnUrl } = useAuthRedirect();
  const { register: authRegister, isLoading, error, clearError } = useAuthStore();
  const [showPass, setShowPass] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    clearError();
    const ok = await authRegister({ name: data.name, email: data.email, password: data.password });
    if (ok) {
      showToast('¡Cuenta creada! Bienvenido 🎉', 'success');
      navigate(resolveReturnUrl(), { replace: true });
    }
  };

  return (
    <AuthLayout title="Crear cuenta" subtitle="Únete a la comunidad de MisEventos">
      <div className="glass rounded-2xl p-6 space-y-5">
        {error && (
          <div className="p-3 bg-red-500/10 rounded-xl border border-red-500/20">
            <span className="text-red-400 text-sm">⚠ {error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Nombre completo"
            placeholder="Andrés Castellanos"
            leftIcon={<User size={16} />}
            error={errors.name?.message}
            autoComplete="off"
            required
            wrapperClassName="space-y-1.5"
            {...register('name')}
          />
          <Input
            label="Correo electrónico"
            type="email"
            placeholder="tu@correo.com"
            leftIcon={<Mail size={16} />}
            error={errors.email?.message}
            autoComplete="off"
            required
            wrapperClassName="space-y-1.5"
            {...register('email')}
          />
          <Input
            label="Contraseña"
            type={showPass ? 'text' : 'password'}
            placeholder="Mínimo 6 caracteres"
            leftIcon={<Lock size={16} />}
            error={errors.password?.message}
            autoComplete="off"
            required
            wrapperClassName="space-y-1.5"
            {...register('password')}
          />
          <Input
            label="Confirmar contraseña"
            type={showPass ? 'text' : 'password'}
            placeholder="Repite la contraseña"
            leftIcon={<Lock size={16} />}
            error={errors.confirmPassword?.message}
            autoComplete="off"
            rightIcon={
              <button type="button" onClick={() => setShowPass(!showPass)}>
                {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            }
            required
            wrapperClassName="space-y-1.5"
            {...register('confirmPassword')}
          />

          <Button
            type="submit"
            className="w-full bg-brand-400 hover:bg-brand-300 text-white border-0"
            isLoading={isLoading}
            rightIcon={<ArrowRight size={16} />}
          >
            Crear cuenta
          </Button>
        </form>

        <p className="text-center text-sm text-white/40 font-body">
          ¿Ya tienes cuenta?{' '}
          <Link
            to="/login"
            className="text-brand-400 hover:text-brand-300 font-medium transition-colors"
          >
            Inicia sesión
          </Link>
        </p>
      </div>
    </AuthLayout>
  );
}
