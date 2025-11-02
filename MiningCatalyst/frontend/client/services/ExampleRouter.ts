import { makeRequest } from '../core/requests'

export function useExampleRouter() {
  const test = (
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<any>({
      method: 'GET',
      url: '/example/test',
      aborter_key,
    })
  }

  return {
    test,
  }
}
