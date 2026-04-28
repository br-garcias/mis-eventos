import { Button } from '@/features/shared/ui/Button';
import { Link } from 'react-router-dom';

export function ForbiddenPage() {
  return (
    <div className="min-h-screen flex items-center justify-center pt-20 px-4">
      <div className="text-center">
        <div className="text-6xl mb-6">🚫</div>
        <h1 className="font-display font-black text-4xl text-white mb-4">Acceso denegado</h1>
        <p className="text-white/50 font-body text-lg mb-8 max-w-md mx-auto">
          No tienes los permisos necesarios para acceder a esta sección.
        </p>
        <Link to="/">
          <Button>Volver al inicio</Button>
        </Link>
      </div>
    </div>
  );
}
