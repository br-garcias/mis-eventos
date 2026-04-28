import { ApiError } from '@/lib/http/apiClient';

interface FastAPIErrorDetail {
  msg: string;
  type: string;
  loc?: string[];
}

interface FastAPIErrorResponse {
  detail?: string | FastAPIErrorDetail | FastAPIErrorDetail[];
  code?: string;
  message?: string;
}

/**
 * Formats an ApiError into a user-friendly message.
 * Handles FastAPI error responses with detail field.
 */
export function formatApiError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.data) {
      const data = error.data as FastAPIErrorResponse;

      if (data.code) {
        const customMessages: Record<string, string> = {
          SessionOverlapError: 'Ya existe una sesión en ese horario. Elige otro rango de tiempo.',
          EventFullError: 'El evento está lleno. No hay cupos disponibles.',
          RegistrationExistsError: 'Ya estás registrado en este evento.',
          NotRegisteredError: 'No estás registrado en este evento.',
          PastEventError: 'No puedes modificar eventos pasados.',
        };
        if (customMessages[data.code]) {
          return customMessages[data.code];
        }
      }

      if (data.message) {
        return data.message;
      }

      if (typeof data.detail === 'string') {
        return data.detail;
      }

      if (Array.isArray(data.detail)) {
        return data.detail.map((d) => d.msg || JSON.stringify(d)).join(', ');
      }

      if (data.detail?.msg) {
        return data.detail.msg;
      }
    }

    switch (error.status) {
      case 401:
        return 'Sesión expirada. Por favor inicia sesión nuevamente.';
      case 403:
        return 'No tienes permiso para realizar esta acción.';
      case 404:
        return 'Recurso no encontrado.';
      case 422:
        return 'Datos inválidos. Verifica los campos del formulario.';
      case 500:
        return 'Error del servidor. Intenta más tarde.';
      default:
        return error.message || 'Ocurrió un error.';
    }
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'Ocurrió un error inesperado.';
}
