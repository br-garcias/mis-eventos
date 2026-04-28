interface EventsPaginationProps {
  page: number;
  totalPages: number;
  onChange: (page: number) => void;
}

export function EventsPagination({ page, totalPages, onChange }: EventsPaginationProps) {
  if (totalPages <= 1) return null;
  return (
    <div className="flex items-center justify-center gap-2 mt-10">
      <button
        onClick={() => onChange(page - 1)}
        disabled={page === 1}
        className="px-4 py-2 rounded-xl border border-white/10 text-white/60 hover:text-white hover:border-white/30 disabled:opacity-30 disabled:cursor-not-allowed text-sm font-medium transition-all"
      >
        ← Anterior
      </button>
      {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
        <button
          key={p}
          onClick={() => onChange(p)}
          className={`w-10 h-10 rounded-xl text-sm font-medium transition-all ${
            p === page
              ? 'bg-brand-400 text-white shadow-lg shadow-brand-400/25'
              : 'border border-white/10 text-white/50 hover:text-white hover:border-white/30'
          }`}
        >
          {p}
        </button>
      ))}
      <button
        onClick={() => onChange(page + 1)}
        disabled={page === totalPages}
        className="px-4 py-2 rounded-xl border border-white/10 text-white/60 hover:text-white hover:border-white/30 disabled:opacity-30 disabled:cursor-not-allowed text-sm font-medium transition-all"
      >
        Siguiente →
      </button>
    </div>
  );
}
