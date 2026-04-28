import { useAuthRedirect } from '@/features/auth/hooks/useAuthRedirect';
import { loginSchema, type LoginFormData } from '@/features/auth/schemas';
import { useAuthStore } from '@/features/auth/store';
import { Button } from '@/features/shared/ui/Button';
import { Input } from '@/features/shared/ui/Input';
import { showToast } from '@/features/shared/utils/toast';
import { zodResolver } from '@hookform/resolvers/zod';
import { ArrowRight, Eye, EyeOff, Lock, Mail } from 'lucide-react';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { AuthLayout } from './AuthLayout';

const DEMO_USERS = [
  {
    label: 'Admin',
    email: 'admin@demo.com',
    password: 'Admin#12345',
    badge: 'Admin',
    color: 'text-brand-400',
  },
  {
    label: 'Organizador',
    email: 'organizer@demo.com',
    password: 'Organizer#12345',
    badge: 'Org',
    color: 'text-accent-teal',
  },
  {
    label: 'Asistente',
    email: 'attendee@demo.com',
    password: 'Attendee#12345',
    badge: 'User',
    color: 'text-violet-400',
  },
] as const;

export function LoginPage() {
  const navigate = useNavigate();
  const { resolveReturnUrl } = useAuthRedirect();
  const { login, isLoading, error, clearError } = useAuthStore();
  const [showPass, setShowPass] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    clearError();
    const ok = await login(data.email, data.password);
    if (ok) {
      showToast('¡Bienvenido de vuelta! 👋', 'success');
      navigate(resolveReturnUrl(), { replace: true });
    }
  };

  const fillDemo = (user: (typeof DEMO_USERS)[number]) => {
    setValue('email', user.email);
    setValue('password', user.password);
    clearError();
  };

  return (
    <AuthLayout title="Iniciar sesión" subtitle="Accede a tu cuenta de MisEventos">
      {/* Demo accounts */}
      <div className="mb-5">
        <p className="text-xs text-white/30 text-center mb-3 font-body">— Cuentas demo —</p>
        <div className="grid grid-cols-3 gap-2">
          {DEMO_USERS.map((u) => (
            <button
              key={u.email}
              type="button"
              onClick={() => fillDemo(u)}
              className="glass rounded-xl p-3 text-center hover:border-white/20 transition-all group"
            >
              <span className={`text-xs font-bold font-display ${u.color}`}>{u.badge}</span>
              <p className="text-xs text-white/40 font-body mt-0.5 truncate">{u.label}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Form */}
      <div className="glass rounded-2xl p-6 space-y-5">
        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-500/10 rounded-xl border border-red-500/20">
            <span className="text-red-400 text-sm">⚠ {error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
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
            placeholder="••••••••"
            leftIcon={<Lock size={16} />}
            rightIcon={
              <button type="button" onClick={() => setShowPass(!showPass)}>
                {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            }
            error={errors.password?.message}
            autoComplete="off"
            required
            wrapperClassName="space-y-1.5"
            {...register('password')}
          />

          <Button
            type="submit"
            className="w-full bg-brand-400 hover:bg-brand-300 text-white border-0"
            isLoading={isLoading}
            rightIcon={<ArrowRight size={16} />}
          >
            Iniciar sesión
          </Button>
        </form>

        <p className="text-center text-sm text-white/40 font-body">
          ¿No tienes cuenta?{' '}
          <Link
            to="/registro"
            className="text-brand-400 hover:text-brand-300 font-medium transition-colors"
          >
            Regístrate
          </Link>
        </p>
      </div>
    </AuthLayout>
  );
}
