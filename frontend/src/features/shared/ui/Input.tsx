import { cn } from '@/lib/cn';
import { ComponentProps, Fragment, ReactNode } from 'react';
import { FieldError } from './FieldError';
import { Label } from './Label';

interface Props extends ComponentProps<'input'> {
  wrapperClassName?: string;
  label?: string;
  labelClassName?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  error?: string;
}

function Input({
  wrapperClassName,
  label,
  labelClassName,
  error,
  type,
  className,
  leftIcon,
  rightIcon,
  ...props
}: Props) {
  const isWrapperDiv = Boolean(wrapperClassName || label || error);

  const Wrapper = isWrapperDiv ? 'div' : Fragment;

  const hasError = Boolean(error);
  const wrapperProps = isWrapperDiv ? { className: cn(wrapperClassName) } : {};

  const isDateTime = type === 'datetime-local';

  return (
    <Wrapper {...wrapperProps}>
      {label && (
        <Label htmlFor={props.id} className={labelClassName} required={props.required}>
          {label}
        </Label>
      )}
      <div className="relative">
        {leftIcon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40">{leftIcon}</div>
        )}
        <input
          type={type}
          data-slot="input"
          aria-invalid={hasError}
          aria-describedby={hasError ? `${props.id}-error` : undefined}
          className={cn(
            'h-10 w-full min-w-0 rounded-lg border border-surface-200 bg-surface-100 px-3 py-2 text-base text-white placeholder:text-white/30 transition-all outline-none focus:border-brand-400 focus:ring-2 focus:ring-brand-400/20 disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50',
            leftIcon && 'pl-10',
            hasError && 'border-destructive focus:border-destructive focus:ring-destructive/20',
            isDateTime && [
              '[&::-webkit-calendar-picker-indicator]:filter [&::-webkit-calendar-picker-indicator]:invert',
              '[&::-webkit-calendar-picker-indicator]:cursor-pointer',
              '[&::-webkit-calendar-picker-indicator]:opacity-60',
              '[&::-webkit-calendar-picker-indicator]:hover:opacity-100',
              '[&::-webkit-datetime-edit]:text-white',
              '[&::-webkit-datetime-edit-year-field]:text-white',
              '[&::-webkit-datetime-edit-month-field]:text-white',
              '[&::-webkit-datetime-edit-day-field]:text-white',
              '[&::-webkit-datetime-edit-hour-field]:text-white',
              '[&::-webkit-datetime-edit-minute-field]:text-white',
              '[&::-webkit-datetime-edit-ampm-field]:text-white',
            ],
            className,
          )}
          {...props}
        />
        {rightIcon && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-white/40">{rightIcon}</div>
        )}
      </div>
      {hasError && <FieldError message={error} />}
    </Wrapper>
  );
}

export { Input };
