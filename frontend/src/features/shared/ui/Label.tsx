import { cn } from '@/lib/cn';

import { Label as LabelPrimitive } from 'radix-ui';

import { ComponentProps } from 'react';

interface Props extends ComponentProps<typeof LabelPrimitive.Root> {
  required?: boolean;
}

function Label({ className, required, children, ...props }: Props) {
  return (
    <LabelPrimitive.Root
      data-slot="label"
      className={cn(
        'flex items-center gap-2 text-sm leading-none font-medium text-white/80 select-none group-data-[disabled=true]:pointer-events-none group-data-[disabled=true]:opacity-50 peer-disabled:cursor-not-allowed peer-disabled:opacity-50',
        className,
      )}
      {...props}
    >
      {children}
      {required && <span className="text-destructive ml-1">*</span>}
    </LabelPrimitive.Root>
  );
}

export { Label };
