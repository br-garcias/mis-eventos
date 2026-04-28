import { cn } from '@/lib/cn';

interface Props {
  message?: string;
  className?: string;
}

export function FieldError({ message, className }: Props) {
  if (!message) return null;

  return (
    <p className={cn('text-xs text-red-400 flex items-center gap-1.5 mt-1', className)}>
      {message}
    </p>
  );
}
