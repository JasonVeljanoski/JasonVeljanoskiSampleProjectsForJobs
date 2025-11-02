import { makeRequest } from '../core/requests'

import { Equipment } from '../models/Equipment'
import { Floc } from '../models/Floc'

export function useFlocRouter() {
  const fromFlocsGetEquipment = (
    body: Array<number>,
    aborter_key = null as string | boolean | null 
  ) => {
    const date_fields = ['.created', '.updated']
    return makeRequest<Array<Equipment>>({
      method: 'POST',
      url: '/floc/equipment',
      body,
      aborter_key,
      date_fields,
    })
  }

  const getFlocs = (
    {
      search,
    }: {
      search?: string
    },
    aborter_key = null as string | boolean | null 
  ) => {
    const date_fields = ['.created', '.updated']
    return makeRequest<Array<Floc>>({
      method: 'GET',
      url: '/floc',
      query: {
        search,
      },
      aborter_key,
      date_fields,
    })
  }

  return {
    fromFlocsGetEquipment,
    getFlocs,
  }
}
