/**
 * Formats a date string to a long Spanish locale date.
 * Supports both YYYY-MM-DD and ISO datetime.
 * Example: "15 de marzo de 2025"
 */
export function formatDate(dateStr: string): string {
  const d = new Date(dateStr.length === 10 ? dateStr + 'T00:00:00' : dateStr);
  return d.toLocaleDateString('es-CO', { day: 'numeric', month: 'long', year: 'numeric' });
}

/**
 * Formats a date string to a short Spanish locale date.
 * Supports both YYYY-MM-DD and ISO datetime.
 * Example: "15 mar"
 */
export function formatDateShort(dateStr: string): string {
  const d = new Date(dateStr.length === 10 ? dateStr + 'T00:00:00' : dateStr);
  return d.toLocaleDateString('es-CO', { day: 'numeric', month: 'short' });
}

/**
 * Formats an ISO datetime string to a time-only display.
 * Example: "09:00"
 */
export function formatDateTime(isoStr: string): string {
  const d = new Date(isoStr);
  return d.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
}
