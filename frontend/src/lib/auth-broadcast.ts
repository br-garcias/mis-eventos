import { APP_CONFIG } from '@/lib/config';

type AuthMessage = { type: 'logout' | 'token-updated' };

class AuthBroadcast {
  private channel: BroadcastChannel | null = null;
  private listeners = new Set<(msg: AuthMessage) => void>();

  private init() {
    if (!this.channel) {
      this.channel = new BroadcastChannel(APP_CONFIG.auth.broadcastChannelName);
      this.channel.onmessage = (e) => {
        this.listeners.forEach((cb) => cb(e.data));
      };
    }
  }

  send(msg: AuthMessage) {
    this.init();
    this.channel?.postMessage(msg);
  }

  onMessage(cb: (msg: AuthMessage) => void): () => void {
    this.init();
    this.listeners.add(cb);
    return () => this.listeners.delete(cb);
  }

  close() {
    this.channel?.close();
    this.channel = null;
  }
}

export const authBroadcast = new AuthBroadcast();
