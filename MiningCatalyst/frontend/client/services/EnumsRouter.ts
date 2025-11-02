import { makeRequest } from '../core/requests'

import { AllEnumsRead } from '../models/AllEnumsRead'
import { EnumRead } from '../models/EnumRead'
import { EnumWrite } from '../models/EnumWrite'

export function useEnumsRouter() {
  const updatePriority = (
    body: EnumWrite,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<EnumRead>({
      method: 'PUT',
      url: '/enums/priority',
      body,
      aborter_key,
    })
  }

  const addPriority = (
    body: EnumWrite,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<EnumRead>({
      method: 'POST',
      url: '/enums/priority',
      body,
      aborter_key,
    })
  }

  const deletePriority = (
    {
      id,
    }: {
      id: number
    },
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<any>({
      method: 'DELETE',
      url: '/enums/priority',
      query: {
        id,
      },
      aborter_key,
    })
  }

  const updateStatus = (
    body: EnumWrite,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<EnumRead>({
      method: 'PUT',
      url: '/enums/status',
      body,
      aborter_key,
    })
  }

  const addStatus = (
    body: EnumWrite,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<EnumRead>({
      method: 'POST',
      url: '/enums/status',
      body,
      aborter_key,
    })
  }

  const deleteStatus = (
    {
      id,
    }: {
      id: number
    },
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<any>({
      method: 'DELETE',
      url: '/enums/status',
      query: {
        id,
      },
      aborter_key,
    })
  }

  const updateTrigger = (
    body: EnumWrite,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<EnumRead>({
      method: 'PUT',
      url: '/enums/trigger',
      body,
      aborter_key,
    })
  }

  const addTrigger = (
    body: EnumWrite,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<EnumRead>({
      method: 'POST',
      url: '/enums/trigger',
      body,
      aborter_key,
    })
  }

  const deleteTrigger = (
    {
      id,
    }: {
      id: number
    },
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<any>({
      method: 'DELETE',
      url: '/enums/trigger',
      query: {
        id,
      },
      aborter_key,
    })
  }

  const updatePrimaryDriver = (
    body: EnumWrite,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<EnumRead>({
      method: 'PUT',
      url: '/enums/primary_driver',
      body,
      aborter_key,
    })
  }

  const addPrimaryDriver = (
    body: EnumWrite,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<EnumRead>({
      method: 'POST',
      url: '/enums/primary_driver',
      body,
      aborter_key,
    })
  }

  const deletePrimaryDriver = (
    {
      id,
    }: {
      id: number
    },
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<any>({
      method: 'DELETE',
      url: '/enums/primary_driver',
      query: {
        id,
      },
      aborter_key,
    })
  }

  const updateSecondaryDriver = (
    body: EnumWrite,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<EnumRead>({
      method: 'PUT',
      url: '/enums/secondary_driver',
      body,
      aborter_key,
    })
  }

  const addSecondaryDriver = (
    body: EnumWrite,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<EnumRead>({
      method: 'POST',
      url: '/enums/secondary_driver',
      body,
      aborter_key,
    })
  }

  const deleteSecondaryDriver = (
    {
      id,
    }: {
      id: number
    },
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<any>({
      method: 'DELETE',
      url: '/enums/secondary_driver',
      query: {
        id,
      },
      aborter_key,
    })
  }

  const updateCostBenefitCategory = (
    body: EnumWrite,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<EnumRead>({
      method: 'PUT',
      url: '/enums/cost_benefit_category',
      body,
      aborter_key,
    })
  }

  const addCostBenefitCategory = (
    body: EnumWrite,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<EnumRead>({
      method: 'POST',
      url: '/enums/cost_benefit_category',
      body,
      aborter_key,
    })
  }

  const deleteCostBenefitCategory = (
    {
      id,
    }: {
      id: number
    },
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<any>({
      method: 'DELETE',
      url: '/enums/cost_benefit_category',
      query: {
        id,
      },
      aborter_key,
    })
  }

  const updateBenefitFrequency = (
    body: EnumWrite,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<EnumRead>({
      method: 'PUT',
      url: '/enums/benefit_frequency',
      body,
      aborter_key,
    })
  }

  const addBenefitFrequency = (
    body: EnumWrite,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<EnumRead>({
      method: 'POST',
      url: '/enums/benefit_frequency',
      body,
      aborter_key,
    })
  }

  const deleteBenefitFrequency = (
    {
      id,
    }: {
      id: number
    },
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<any>({
      method: 'DELETE',
      url: '/enums/benefit_frequency',
      query: {
        id,
      },
      aborter_key,
    })
  }

  const getAllEnums = (
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<AllEnumsRead>({
      method: 'GET',
      url: '/enums/all',
      aborter_key,
    })
  }

  const getPriorities = (
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<Array<EnumRead>>({
      method: 'GET',
      url: '/enums/priority/all',
      aborter_key,
    })
  }

  const updatePriorities = (
    body: Array<EnumWrite>,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<Array<EnumRead>>({
      method: 'PUT',
      url: '/enums/priority/all',
      body,
      aborter_key,
    })
  }

  const getStatuses = (
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<Array<EnumRead>>({
      method: 'GET',
      url: '/enums/status/all',
      aborter_key,
    })
  }

  const updateStatuses = (
    body: Array<EnumWrite>,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<Array<EnumRead>>({
      method: 'PUT',
      url: '/enums/status/all',
      body,
      aborter_key,
    })
  }

  const getTriggers = (
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<Array<EnumRead>>({
      method: 'GET',
      url: '/enums/trigger/all',
      aborter_key,
    })
  }

  const updateTriggers = (
    body: Array<EnumWrite>,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<Array<EnumRead>>({
      method: 'PUT',
      url: '/enums/trigger/all',
      body,
      aborter_key,
    })
  }

  const getPrimaryDrivers = (
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<Array<EnumRead>>({
      method: 'GET',
      url: '/enums/primary_driver/all',
      aborter_key,
    })
  }

  const updatePrimaryDrivers = (
    body: Array<EnumWrite>,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<Array<EnumRead>>({
      method: 'PUT',
      url: '/enums/primary_driver/all',
      body,
      aborter_key,
    })
  }

  const getSecondaryDrivers = (
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<Array<EnumRead>>({
      method: 'GET',
      url: '/enums/secondary_driver/all',
      aborter_key,
    })
  }

  const updateSecondaryDrivers = (
    body: Array<EnumWrite>,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<Array<EnumRead>>({
      method: 'PUT',
      url: '/enums/secondary_driver/all',
      body,
      aborter_key,
    })
  }

  const getCostBenefitCategories = (
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<Array<EnumRead>>({
      method: 'GET',
      url: '/enums/cost_benefit_category/all',
      aborter_key,
    })
  }

  const updateCostBenefitCategories = (
    body: Array<EnumWrite>,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<Array<EnumRead>>({
      method: 'PUT',
      url: '/enums/cost_benefit_category/all',
      body,
      aborter_key,
    })
  }

  const getBenefitFrequencies = (
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<Array<EnumRead>>({
      method: 'GET',
      url: '/enums/benefit_frequency/all',
      aborter_key,
    })
  }

  const updateBenefitFrequencies = (
    body: Array<EnumWrite>,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<Array<EnumRead>>({
      method: 'PUT',
      url: '/enums/benefit_frequency/all',
      body,
      aborter_key,
    })
  }

  return {
    updatePriority,
    addPriority,
    deletePriority,
    updateStatus,
    addStatus,
    deleteStatus,
    updateTrigger,
    addTrigger,
    deleteTrigger,
    updatePrimaryDriver,
    addPrimaryDriver,
    deletePrimaryDriver,
    updateSecondaryDriver,
    addSecondaryDriver,
    deleteSecondaryDriver,
    updateCostBenefitCategory,
    addCostBenefitCategory,
    deleteCostBenefitCategory,
    updateBenefitFrequency,
    addBenefitFrequency,
    deleteBenefitFrequency,
    getAllEnums,
    getPriorities,
    updatePriorities,
    getStatuses,
    updateStatuses,
    getTriggers,
    updateTriggers,
    getPrimaryDrivers,
    updatePrimaryDrivers,
    getSecondaryDrivers,
    updateSecondaryDrivers,
    getCostBenefitCategories,
    updateCostBenefitCategories,
    getBenefitFrequencies,
    updateBenefitFrequencies,
  }
}
