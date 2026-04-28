import { useDebouncedValue } from '@/features/shared/hooks/useDebouncedValue';
import { Spinner } from '@/features/shared/ui/Spinner';
import { Search } from 'lucide-react';
import { memo, useEffect, useState, useTransition } from 'react';

interface UsersFiltersProps {
  isFiltering: boolean;
  onSearchChange: (value: string) => void;
}

function _UsersFilters({ isFiltering, onSearchChange }: UsersFiltersProps) {
  const [input, setInput] = useState('');
  const debounced = useDebouncedValue(input, 350);
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    startTransition(() => onSearchChange(debounced));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debounced]);

  const showSpinner = isFiltering || isPending || input !== debounced;

  return (
    <div className="relative max-w-md flex-1">
      <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30" />
      <input
        type="text"
        placeholder="Buscar usuarios..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        className="w-full glass border border-white/10 rounded-xl pl-10 pr-10 py-2.5 text-white placeholder:text-white/30 text-sm focus:outline-none focus:border-brand-400/50"
      />
      {showSpinner && (
        <div className="absolute right-3 top-1/2 -translate-y-1/2">
          <Spinner size="sm" />
        </div>
      )}
    </div>
  );
}

export const UsersFilters = memo(_UsersFilters);
