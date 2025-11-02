import { makeRequest } from '../core/requests'

export function useTasksRouter() {
  const updateSupervisorsTask = (
    {
      token,
    }: {
      token?: string
    },
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<any>({
      method: 'PUT',
      url: '/tasks/update_supervisors',
      query: {
        token,
      },
      aborter_key,
    })
  }

  return {
    updateSupervisorsTask,
  }
}
