/**
 * Calculates the percentage of capacity used, capped at 100.
 */
export function getCapacityPercent(registered: number, capacity: number): number {
  return Math.min(100, Math.round((registered / capacity) * 100));
}

/**
 * Returns a Tailwind text-color class based on capacity percentage.
 */
export function getCapacityColor(percent: number): string {
  if (percent >= 90) return 'text-red-400';
  if (percent >= 70) return 'text-amber-400';
  return 'text-green-400';
}

/**
 * Returns a Tailwind background-color class based on capacity percentage.
 */
export function getCapacityBarColor(percent: number): string {
  if (percent >= 90) return 'bg-red-400';
  if (percent >= 70) return 'bg-amber-400';
  return 'bg-green-400';
}

/**
 * Returns a human-readable string describing available spots.
 */
export function getAvailableSpots(registered: number, capacity: number): string {
  const available = capacity - registered;
  if (available <= 0) return 'Agotado';
  if (available <= 10) return `¡Solo ${available} cupos!`;
  return `${available} cupos disponibles`;
}

/**
 * Returns a human-readable string for how many days until the event date.
 */
export function getDaysUntil(dateStr: string): string {
  const event = new Date(dateStr.length === 10 ? dateStr + 'T00:00:00' : dateStr);
  const now = new Date();
  const diff = Math.ceil((event.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  if (diff < 0) return 'Finalizado';
  if (diff === 0) return '¡Hoy!';
  if (diff === 1) return 'Mañana';
  return `En ${diff} días`;
}
