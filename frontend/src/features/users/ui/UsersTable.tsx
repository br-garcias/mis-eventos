import { ROLE_LABELS } from '@/features/shared/constants';
import { Avatar, AvatarFallback } from '@/features/shared/ui/Avatar';
import { Badge } from '@/features/shared/ui/Badge';
import { EmptyState } from '@/features/shared/ui/EmptyState';
import { Skeleton } from '@/features/shared/ui/Skeleton';
import type { User } from '@/features/users/types';
import { getInitials } from '@/lib/initials';
import { ToggleLeft, ToggleRight } from 'lucide-react';
import { memo } from 'react';

interface UsersTableProps {
  users: User[];
  isLoading: boolean;
  onToggle: (userId: string) => void;
}

function _UsersTable({ users, isLoading, onToggle }: UsersTableProps) {
  if (isLoading) {
    return (
      <div className="p-4 space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex items-center gap-4 p-4">
            <Skeleton className="h-10 w-10 rounded-full" />
            <div className="flex-1">
              <Skeleton className="h-5 w-48 mb-2" />
              <Skeleton className="h-4 w-64" />
            </div>
            <Skeleton className="h-6 w-20" />
            <Skeleton className="h-8 w-24" />
          </div>
        ))}
      </div>
    );
  }

  if (users.length === 0) {
    return (
      <EmptyState
        icon="👥"
        title="No hay usuarios"
        description="No se encontraron usuarios con ese criterio"
      />
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-white/10">
            <th className="text-left text-xs font-medium text-white/40 uppercase tracking-wider px-6 py-4">
              Usuario
            </th>
            <th className="text-left text-xs font-medium text-white/40 uppercase tracking-wider px-6 py-4">
              Rol
            </th>
            <th className="text-left text-xs font-medium text-white/40 uppercase tracking-wider px-6 py-4">
              Estado
            </th>
            <th className="text-left text-xs font-medium text-white/40 uppercase tracking-wider px-6 py-4">
              Fecha
            </th>
            <th className="text-right text-xs font-medium text-white/40 uppercase tracking-wider px-6 py-4">
              Acciones
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {users.map((user) => (
            <tr key={user.id} className="hover:bg-white/5 transition-colors">
              <td className="px-6 py-4">
                <div className="flex items-center gap-3">
                  <Avatar>
                    <AvatarFallback className="text-xs">{getInitials(user.name)}</AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="text-sm font-medium text-white">{user.name}</p>
                    <p className="text-xs text-white/40">{user.email}</p>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4">
                <Badge variant={user.role.name === 'admin' ? 'secondary' : 'default'}>
                  {ROLE_LABELS[user.role.name as keyof typeof ROLE_LABELS] || user.role.name}
                </Badge>
              </td>
              <td className="px-6 py-4">
                <span
                  className={`text-xs font-medium ${user.is_active ? 'text-green-400' : 'text-red-400'}`}
                >
                  {user.is_active ? 'Activo' : 'Inactivo'}
                </span>
              </td>
              <td className="px-6 py-4 text-xs text-white/40">
                {new Date(user.created_at).toLocaleDateString('es-CO')}
              </td>
              <td className="px-6 py-4 text-right">
                <button
                  onClick={() => onToggle(user.id)}
                  className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                  title={user.is_active ? 'Desactivar' : 'Activar'}
                >
                  {user.is_active ? (
                    <ToggleRight size={20} className="text-green-400" />
                  ) : (
                    <ToggleLeft size={20} className="text-white/30" />
                  )}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export const UsersTable = memo(_UsersTable);
