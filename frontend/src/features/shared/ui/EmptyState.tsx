import type { ReactNode } from 'react';

interface EmptyStateProps {
  icon: string;
  title: string;
  description: string;
  action?: ReactNode;
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="text-6xl mb-4">{icon}</div>
      <h3 className="font-display text-xl font-semibold text-white/80 mb-2">{title}</h3>
      <p className="text-white/40 font-body text-sm max-w-xs mb-6">{description}</p>
      {action}
    </div>
  );
}
