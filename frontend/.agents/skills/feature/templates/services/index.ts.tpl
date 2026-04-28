import { Criteria, CriteriaBuilder } from '@/lib/criteria';
import { http } from '@/lib/http';
import { Create__Name__Dto, Update__Name__Dto, __Name__sResponse } from '../types';

export interface __Name__sQueryParams extends Criteria.Params {
  // TODO: Añadir propiedades de filtrado
}

export const __name__sService = {
  get__Name__s(params?: __Name__sQueryParams): Promise<__Name__sResponse> {
    const builder = new CriteriaBuilder();

    // TODO: Añadir filtros a aplicar sobre la query
    // if (params?.name) {
    //   builder.addFilter('name', 'CONTAINS', params.name);
    // }

    if (params?.offset !== undefined && params?.limit !== undefined) {
      builder.setPagination(params.offset, params.limit);
    }

    if (params?.orderBy && params?.orderType) {
      builder.setOrder(params.orderBy, params.orderType);
    }

    const queryString = builder.build();
    const url = `/api/nexus/__name__s${queryString ? `?${queryString}` : ''}`;
    
    return http.get<__Name__sResponse>(url);
  },

  create__Name__: (data: Create__Name__Dto) => 
    http.post<void>('/api/nexus/__name__s', data),
    
  update__Name__: (id: string, data: Update__Name__Dto) => 
    http.put<void>(`/api/nexus/__name__s/${id}`, data),
    
  delete__Name__: (id: string) => 
    http.delete<void>(`/api/nexus/__name__s/${id}`),
};
