import { useAuthStore } from '@/features/auth/store';
import { useUIStore } from '@/features/shared/stores/ui-store';
import { Button } from '@/features/shared/ui/Button';
import { showToast } from '@/features/shared/utils/toast';
import { UsersService } from '@/features/users/services';
import type { Role, User } from '@/features/users/types';
import { formatApiError } from '@/lib/apiError';
import { ArrowLeft, Plus, Shield } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { CreateUserForm } from './CreateUserForm';
import { UsersFilters } from './UsersFilters';
import { UsersTable } from './UsersTable';

export function AdminUsersPage() {
  const openDialog = useUIStore((s) => s.openDialog);
  const closeDialog = useUIStore((s) => s.closeDialog);
  const currentUser = useAuthStore((s) => s.user);

  const [users, setUsers] = useState<User[] | null>(null);
  const [roles, setRoles] = useState<Role[]>([]);
  const [search, setSearch] = useState('');
  const [isFetching, setIsFetching] = useState(false);

  const loadUsers = useCallback(async (q: string) => {
    setIsFetching(true);
    try {
      const res = await UsersService.getUsers({ size: 100, search: q || undefined });
      setUsers(res.items);
    } catch {
      showToast('Error al cargar usuarios', 'error');
    } finally {
      setIsFetching(false);
    }
  }, []);

  // Load roles once.
  useEffect(() => {
    UsersService.getRoles()
      .then(setRoles)
      .catch(() => showToast('Error al cargar roles', 'error'));
  }, []);

  // Refetch users on search change.
  useEffect(() => {
    loadUsers(search);
  }, [search, loadUsers]);

  const handleToggleUser = useCallback(
    async (userId: string) => {
      if (currentUser && userId === currentUser.id) {
        showToast('No puedes desactivarte a ti mismo', 'error');
        return;
      }
      try {
        await UsersService.toggleUser(userId);
        setUsers((prev) =>
          prev ? prev.map((u) => (u.id === userId ? { ...u, is_active: !u.is_active } : u)) : prev,
        );
        showToast('Usuario actualizado', 'success');
      } catch (err) {
        showToast(formatApiError(err), 'error');
      }
    },
    [currentUser],
  );

  const handleCreate = useCallback(() => {
    openDialog(
      'Crear usuario',
      'Completa el formulario para crear un nuevo usuario',
      <CreateUserForm
        roles={roles}
        onSuccess={() => {
          closeDialog();
          loadUsers(search);
        }}
        onCancel={closeDialog}
      />,
      'sm:max-w-lg',
    );
  }, [openDialog, closeDialog, roles, loadUsers, search]);

  const isInitialLoading = users === null;
  const list = users ?? [];

  return (
    <div className="min-h-screen pt-28 pb-20">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link to="/" className="p-2 rounded-lg hover:bg-white/5 transition-colors">
            <ArrowLeft size={20} className="text-white/60" />
          </Link>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-brand-400/10 border border-brand-400/20 flex items-center justify-center">
              <Shield size={20} className="text-brand-400" />
            </div>
            <div>
              <h1 className="font-display font-black text-2xl text-white">Administración</h1>
              <p className="text-white/40 text-sm">Gestión de usuarios</p>
            </div>
          </div>
        </div>

        {/* Filters & Actions */}
        <div className="flex justify-between items-center gap-4 mb-6">
          <UsersFilters isFiltering={!isInitialLoading && isFetching} onSearchChange={setSearch} />
          <Button
            onClick={handleCreate}
            leftIcon={<Plus size={16} />}
            disabled={roles.length === 0}
          >
            Crear usuario
          </Button>
        </div>

        {/* Users Table */}
        <div
          className={`glass rounded-2xl overflow-hidden transition-opacity ${
            !isInitialLoading && isFetching ? 'opacity-60' : ''
          }`}
        >
          <UsersTable users={list} isLoading={isInitialLoading} onToggle={handleToggleUser} />
        </div>
      </div>
    </div>
  );
}
