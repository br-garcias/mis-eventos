import { Spinner } from '@/features/shared/ui/Spinner';

export function PageLoader() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center space-y-4">
        <Spinner size="lg" className="mx-auto" />
        <p className="text-white/30 font-body text-sm">Cargando...</p>
      </div>
    </div>
  );
}
