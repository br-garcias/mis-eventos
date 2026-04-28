import Cookies from 'js-cookie';
import { APP_CONFIG } from '@/lib/config';

export interface SessionMeta {
  accessExpiry: number;
  refreshExpiry: number;
  sessionId: string;
}

export function readSessionMeta(): SessionMeta | null {
  const raw = Cookies.get(APP_CONFIG.cookies.meta);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as SessionMeta;
  } catch {
    return null;
  }
}

export function nowSec(): number {
  return Math.floor(Date.now() / 1000);
}

export function isAccessExpiringSoon(meta: SessionMeta, skewSec: number): boolean {
  return meta.accessExpiry - nowSec() <= skewSec;
}

export function isRefreshExpired(meta: SessionMeta): boolean {
  return meta.refreshExpiry <= nowSec();
}

export function clearSessionMeta(): void {
  Cookies.remove(APP_CONFIG.cookies.meta, { path: '/' });
}
