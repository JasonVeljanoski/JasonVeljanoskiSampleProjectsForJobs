import { makeRequest } from '../core/requests'

import { User } from '../models/User'
import { UserBasic } from '../models/UserBasic'

export function useUserRouter() {
  const getAuthToken = (
    {
      code,
    }: {
      code: string
    },
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<any>({
      method: 'GET',
      url: '/user/login',
      query: {
        code,
      },
      aborter_key,
    })
  }

  const localBackdoor = (
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<any>({
      method: 'GET',
      url: '/user/backdoor',
      aborter_key,
    })
  }

  const getUser = (
    aborter_key = null as string | boolean | null 
  ) => {
    const date_fields = ['.created', '.updated', '.last_logged_in']
    return makeRequest<User>({
      method: 'GET',
      url: '/user',
      aborter_key,
      date_fields,
    })
  }

  const updateUser = (
    body: User,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<any>({
      method: 'PUT',
      url: '/user',
      body,
      aborter_key,
    })
  }

  const getUser2 = (
    {
      id,
    }: {
      id: number
    },
    aborter_key = null as string | boolean | null 
  ) => {
    const date_fields = ['.created', '.updated', '.last_logged_in']
    return makeRequest<User>({
      method: 'GET',
      url: '/user/HALP',
      query: {
        id,
      },
      aborter_key,
      date_fields,
    })
  }

  const getUsersSupervisor = (
    {
      user_id,
    }: {
      user_id?: number
    },
    aborter_key = null as string | boolean | null 
  ) => {
    const date_fields = ['.created', '.updated']
    return makeRequest<UserBasic>({
      method: 'GET',
      url: '/user/supervisor',
      query: {
        user_id,
      },
      aborter_key,
      date_fields,
    })
  }

  const getAllUsers = (
    aborter_key = null as string | boolean | null 
  ) => {
    const date_fields = ['.created', '.updated']
    return makeRequest<Array<UserBasic>>({
      method: 'GET',
      url: '/user/all',
      aborter_key,
      date_fields,
    })
  }

  const getAllBasic = (
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<any>({
      method: 'GET',
      url: '/user/all/basic',
      aborter_key,
    })
  }

  const searchUsers = (
    {
      search,
    }: {
      search?: string
    },
    aborter_key = null as string | boolean | null 
  ) => {
    const date_fields = ['.created', '.updated', '.last_logged_in']
    return makeRequest<Array<User>>({
      method: 'GET',
      url: '/user/search/user',
      query: {
        search,
      },
      aborter_key,
      date_fields,
    })
  }

  const getUsersFromIds = (
    body: Array<number>,
    aborter_key = null as string | boolean | null 
  ) => {
    const date_fields = ['.created', '.updated', '.last_logged_in']
    return makeRequest<Array<User>>({
      method: 'POST',
      url: '/user/users',
      body,
      aborter_key,
      date_fields,
    })
  }

  const updateAccess = (
    {
      access,
    }: {
      access: number
    },
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<any>({
      method: 'PUT',
      url: '/user/access',
      query: {
        access,
      },
      aborter_key,
    })
  }

  return {
    getAuthToken,
    localBackdoor,
    getUser,
    updateUser,
    getUser2,
    getUsersSupervisor,
    getAllUsers,
    getAllBasic,
    searchUsers,
    getUsersFromIds,
    updateAccess,
  }
}
