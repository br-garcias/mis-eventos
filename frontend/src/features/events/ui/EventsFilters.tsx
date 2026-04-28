import { useDebouncedValue } from '@/features/shared/hooks/useDebouncedValue';
import type { EventStatus } from '@/features/shared/types';
import { Spinner } from '@/features/shared/ui/Spinner';
import { Search } from 'lucide-react';
import { useEffect, useState, useTransition } from 'react';

const STATUS_OPTIONS: { value: EventStatus | undefined; label: string }[] = [
  { value: undefined, label: 'Todos' },
  { value: 'published', label: 'Próximos' },
  { value: 'finished', label: 'Pasados' },
];

interface EventsFiltersProps {
  status: EventStatus | undefined;
  initialSearch: string;
  isFiltering: boolean;
  onStatusChange: (status: EventStatus | undefined) => void;
  onSearchChange: (value: string) => void;
}

export function EventsFilters({
  status,
  initialSearch,
  isFiltering,
  onStatusChange,
  onSearchChange,
}: EventsFiltersProps) {
  const [input, setInput] = useState(initialSearch);
  const debounced = useDebouncedValue(input, 350);
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    if (debounced === initialSearch) return;
    startTransition(() => onSearchChange(debounced));
    // We deliberately depend only on `debounced` so the commit happens once per stop.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debounced]);

  const showSpinner = isFiltering || isPending || input !== debounced;

  return (
    <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
      <div className="relative w-full sm:w-64">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30" />
        <input
          type="text"
          placeholder="Buscar eventos..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="w-full pl-10 pr-10 py-2 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/30 text-sm focus:outline-none focus:border-brand-400/50 transition-all"
        />
        {showSpinner && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <Spinner size="sm" />
          </div>
        )}
      </div>
      <div className="flex gap-2">
        {STATUS_OPTIONS.map((opt) => (
          <button
            key={opt.label}
            type="button"
            onClick={() => onStatusChange(opt.value)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all border ${
              status === opt.value
                ? 'bg-brand-400 text-white border-brand-400'
                : 'border-white/10 text-white/50 hover:text-white hover:border-white/30'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  );
}
