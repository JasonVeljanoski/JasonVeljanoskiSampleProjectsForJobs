import { makeRequest } from '../core/requests'

export function useStaticRouter() {
  const ingestOrganisationalUnit = (
    {
      token,
    }: {
      token?: string
    },
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<any>({
      method: 'POST',
      url: '/static/ingest_organisational_unit',
      query: {
        token,
      },
      aborter_key,
    })
  }

  const ingestEquipment = (
    {
      token,
    }: {
      token?: string
    },
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<any>({
      method: 'POST',
      url: '/static/ingest_equipment',
      query: {
        token,
      },
      aborter_key,
    })
  }

  const updateUsers = (
    {
      token,
    }: {
      token?: string
    },
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<any>({
      method: 'POST',
      url: '/static/update_users',
      query: {
        token,
      },
      aborter_key,
    })
  }

  const ingestAllStaticData = (
    {
      token,
    }: {
      token?: string
    },
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<any>({
      method: 'POST',
      url: '/static/ingest_all_static_data',
      query: {
        token,
      },
      aborter_key,
    })
  }

  return {
    ingestOrganisationalUnit,
    ingestEquipment,
    updateUsers,
    ingestAllStaticData,
  }
}
