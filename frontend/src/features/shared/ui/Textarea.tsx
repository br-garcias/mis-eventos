import { cn } from '@/lib/cn';
import { ComponentProps, Fragment } from 'react';
import { FieldError } from './FieldError';
import { Label } from './Label';

interface Props extends ComponentProps<'textarea'> {
  wrapperClassName?: string;
  label?: string;
  labelClassName?: string;
  error?: string;
  required?: boolean;
}

function Textarea({
  wrapperClassName,
  label,
  labelClassName,
  error,
  required,
  className,
  ...props
}: Props) {
  const isWrapperDiv = Boolean(wrapperClassName || label || error);

  const Wrapper = isWrapperDiv ? 'div' : Fragment;

  const hasError = Boolean(error);
  const wrapperProps = isWrapperDiv ? { className: cn(wrapperClassName) } : {};

  return (
    <Wrapper {...wrapperProps}>
      {label && (
        <Label htmlFor={props.id} className={labelClassName} required={required}>
          {label}
        </Label>
      )}
      <textarea
        data-slot="textarea"
        aria-invalid={hasError}
        aria-describedby={hasError && props.id ? `${props.id}-error` : undefined}
        className={cn(
          'flex min-h-[80px] w-full rounded-lg border border-surface-200 bg-surface-100 px-3 py-2 text-base text-white placeholder:text-white/30 transition-all outline-none resize-none focus:border-brand-400 focus:ring-2 focus:ring-brand-400/20 disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50',
          hasError && 'border-destructive focus:border-destructive focus:ring-destructive/20',
        )}
        {...props}
      />
      {hasError && <FieldError message={error} />}
    </Wrapper>
  );
}

export { Textarea };
