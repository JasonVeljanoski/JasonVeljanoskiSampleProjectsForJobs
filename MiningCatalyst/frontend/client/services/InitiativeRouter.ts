import { makeRequest } from '../core/requests'

import { FullInitiative } from '../models/FullInitiative'
import { GeneralImprovementInitiative } from '../models/GeneralImprovementInitiative'

export function useInitiativeRouter() {
  const getInitiative = (
    {
      id,
    }: {
      id: number
    },
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<FullInitiative>({
      method: 'GET',
      url: '/initiative',
      query: {
        id,
      },
      aborter_key,
    })
  }

  const updateInitiative = (
    body: FullInitiative,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<FullInitiative>({
      method: 'PUT',
      url: '/initiative',
      body,
      aborter_key,
    })
  }

  const getGeneralImprovement = (
    {
      id,
    }: {
      id: number
    },
    aborter_key = null as string | boolean | null 
  ) => {
    const date_fields = ['.created', '.updated']
    return makeRequest<GeneralImprovementInitiative>({
      method: 'GET',
      url: '/initiative/general_improvement',
      query: {
        id,
      },
      aborter_key,
      date_fields,
    })
  }

  const getAllInitiatives = (
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<Array<FullInitiative>>({
      method: 'GET',
      url: '/initiative/all',
      aborter_key,
    })
  }

  return {
    getInitiative,
    updateInitiative,
    getGeneralImprovement,
    getAllInitiatives,
  }
}
