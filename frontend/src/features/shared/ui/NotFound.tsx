export function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center px-4">
      <div className="text-8xl mb-6">🌌</div>
      <h1 className="font-display font-black text-6xl text-white mb-3">404</h1>
      <p className="text-white/40 font-body mb-8 max-w-xs">
        Esta página no existe en nuestra galaxia de eventos.
      </p>
      <a
        href="/"
        className="bg-brand-400 text-white px-6 py-3 rounded-xl font-medium hover:bg-brand-300 transition-colors inline-flex items-center gap-2"
      >
        ← Volver al inicio
      </a>
    </div>
  );
}
