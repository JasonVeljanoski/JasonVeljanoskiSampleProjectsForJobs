import { makeRequest } from '../core/requests'

import { Equipment } from '../models/Equipment'
import { OrganisationalUnit } from '../models/OrganisationalUnit'

export function useListsRouter() {
  const allEquipments = (
    aborter_key = null as string | boolean | null 
  ) => {
    const date_fields = ['.created', '.updated']
    return makeRequest<Array<Equipment>>({
      method: 'GET',
      url: '/lists/equipments',
      aborter_key,
      date_fields,
    })
  }

  const organisationalUnits = (
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<Array<OrganisationalUnit>>({
      method: 'GET',
      url: '/lists/organisational_units',
      aborter_key,
    })
  }

  const getOrganisationAreas = (
    {
      search,
    }: {
      search?: string
    },
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<Array<OrganisationalUnit>>({
      method: 'GET',
      url: '/lists/organisational_units/search/area',
      query: {
        search,
      },
      aborter_key,
    })
  }

  const getOrganisationUnits = (
    {
      search,
    }: {
      search?: string
    },
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<Array<OrganisationalUnit>>({
      method: 'GET',
      url: '/lists/organisational_units/search/department',
      query: {
        search,
      },
      aborter_key,
    })
  }

  return {
    allEquipments,
    organisationalUnits,
    getOrganisationAreas,
    getOrganisationUnits,
  }
}
