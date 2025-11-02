import { makeRequest } from '../core/requests'

import { Equipment } from '../models/Equipment'
import { Floc } from '../models/Floc'

export function useEquipmentRouter() {
  const fromEquipmentGetFlocs = (
    body: Array<number>,
    aborter_key = null as string | boolean | null 
  ) => {
    const date_fields = ['.created', '.updated']
    return makeRequest<Array<Floc>>({
      method: 'POST',
      url: '/equipment/floc',
      body,
      aborter_key,
      date_fields,
    })
  }

  const getEquipment = (
    {
      search,
    }: {
      search?: string
    },
    aborter_key = null as string | boolean | null 
  ) => {
    const date_fields = ['.created', '.updated']
    return makeRequest<Array<Equipment>>({
      method: 'GET',
      url: '/equipment',
      query: {
        search,
      },
      aborter_key,
      date_fields,
    })
  }

  return {
    fromEquipmentGetFlocs,
    getEquipment,
  }
}
