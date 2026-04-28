export function getMinDateTime(): string {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  return now.toISOString().slice(0, 16);
}

export function getDefaultEndTime(startTime: string): string {
  if (!startTime) return '';
  const start = new Date(startTime);
  start.setHours(start.getHours() + 1);
  start.setMinutes(start.getMinutes() - start.getTimezoneOffset());
  return start.toISOString().slice(0, 16);
}
