import { useState, useCallback, useEffect } from 'react';
import { PlusIcon } from 'lucide-react';
import { toast } from 'sonner';

import { Button } from '@/features/shared/ui/Button';
import { Pagination } from '@/features/shared/ui/Pagination';
import { useDialog } from '@/features/shared/stores/ui-store';
import type { SortField, SortDirection } from '@/features/shared/types/pagination';

import { __name__sService, type __Name__sQueryParams } from '../services';
import type { __Name__ } from '../types';

// TODO: Crear e importar los siguientes componentes
// import { __Name__Form } from './__Name__Form';
// import { __Name__sFilters } from './__Name__sFilters';
// import { __Name__sTable } from './__Name__sTable';
// import { __Name__sPageSkeleton } from './__Name__sPageSkeleton';

const ITEMS_PER_PAGE = 10;

export function __Name__sPage() {
  const { openDialog, closeDialog, confirmDialog } = useDialog();
  
  const [__name__s, set__Name__s] = useState<__Name__[]>([]);
  const [meta, setMeta] = useState({ count: 0, total: 0 });
  const [isLoading, setIsLoading] = useState(true);
  const [isPending, setIsPending] = useState(false);

  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const [sortField, setSortField] = useState<SortField>('id');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [currentPage, setCurrentPage] = useState(1);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearchTerm(searchTerm), 500);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  const fetch__Name__s = useCallback(async () => {
    setIsPending(true);
    try {
      const params: __Name__sQueryParams = {
        offset: (currentPage - 1) * ITEMS_PER_PAGE,
        limit: ITEMS_PER_PAGE,
        orderBy: sortField,
        orderType: sortDirection.toUpperCase() as 'ASC' | 'DESC',
      };

      if (debouncedSearchTerm) {
        // params.name = debouncedSearchTerm; // Ajustar según los campos de búsqueda reales
      }

      const res = await __name__sService.get__Name__s(params);
      set__Name__s(res.data);
      setMeta(res.meta || { count: res.data.length, total: res.data.length });
    } catch (err) {
      console.error('Error loading __name__s:', err);
      set__Name__s([]);
      setMeta({ count: 0, total: 0 });
      toast.error('Error al cargar los datos');
    } finally {
      setIsPending(false);
      setIsLoading(false);
    }
  }, [currentPage, sortField, sortDirection, debouncedSearchTerm]);

  useEffect(() => {
    fetch__Name__s();
  }, [fetch__Name__s]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
    setCurrentPage(1);
  };

  const handleFormSuccess = useCallback(async () => {
    await fetch__Name__s();
    closeDialog();
  }, [fetch__Name__s, closeDialog]);

  const handleCreate = () => {
    openDialog(
      'Crear __name__',
      'Completa el formulario para crear un nuevo registro',
      <div>TODO: Implementar Formulario</div>, // <__Name__Form onSuccess={handleFormSuccess} />
      'sm:max-w-[700px]'
    );
  };

  const handleEdit = (item: __Name__) => {
    openDialog(
      'Editar __name__',
      `ID: ${item.id}`,
      <div>TODO: Implementar Formulario</div> // <__Name__Form item={item} onSuccess={handleFormSuccess} />
    );
  };

  const handleDelete = (item: __Name__) => {
    confirmDialog(
      'Eliminar registro',
      `¿Estás seguro que deseas eliminar este registro? Esta acción no se puede deshacer.`,
      async () => {
        try {
          await __name__sService.delete__Name__(item.id);
          toast.success('Registro eliminado exitosamente');
          await fetch__Name__s();
        } catch (error) {
          toast.error(error instanceof Error ? error.message : 'Error al eliminar el registro');
        }
      }
    );
  };

  const handleSearchChange = (value: string) => {
    setSearchTerm(value);
    setCurrentPage(1);
  };

  const resetFilters = () => {
    setSearchTerm('');
    setCurrentPage(1);
  };

  const hasActiveFilters = !!searchTerm;

  if (isLoading) {
    return <div>Cargando...</div>; // return <__Name__sPageSkeleton />;
  }

  return (
    <div className="space-y-6 px-4 lg:px-6">
      <div className="flex justify-between items-center">
        <div></div>
        <Button onClick={handleCreate}>
          <PlusIcon className="h-4 w-4 mr-2" />
          Nuevo registro
        </Button>
      </div>

      <div className={`rounded-xl bg-card shadow-sm transition-opacity ${isPending ? 'opacity-60' : 'opacity-100'}`}>
        <div className="p-4 sm:p-6 pb-3 sm:pb-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 sm:gap-0 mb-3 sm:mb-4">
            <div className="flex items-center gap-2">
              <h3 className="text-base sm:text-lg font-semibold text-foreground">__Name__s</h3>
              {isPending && (
                <div className="h-4 w-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              )}
            </div>
            <div className="text-xs sm:text-sm text-muted-foreground">
              {meta.total} registro{meta.total !== 1 ? 's' : ''}
            </div>
          </div>

          {/* TODO: Implementar Filtros */}
          {/* <__Name__sFilters 
            searchTerm={searchTerm} 
            onSearchChange={handleSearchChange} 
            onResetFilters={resetFilters} 
            hasActiveFilters={hasActiveFilters} 
          /> */}
        </div>

        {/* TODO: Implementar Tabla */}
        <div className="p-4">
          Tabla de __name__s aquí. 
          {/* <__Name__sTable 
            items={__name__s}
            sortField={sortField}
            sortDirection={sortDirection}
            onSort={handleSort}
            onEdit={handleEdit}
            onDelete={handleDelete}
          /> */}
        </div>

        {__name__s.length > 0 && (
          <Pagination
            currentPage={currentPage}
            totalItems={meta.total}
            itemsPerPage={ITEMS_PER_PAGE}
            onPageChange={setCurrentPage}
            isLoading={isPending}
          />
        )}
      </div>
    </div>
  );
}
