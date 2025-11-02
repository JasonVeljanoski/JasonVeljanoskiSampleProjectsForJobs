import { makeRequest } from '../core/requests'

import { Settings } from '../models/Settings'
import { SettingsFrontend } from '../models/SettingsFrontend'

export function useSettingsRouter() {
  const getSettings = (
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<Settings>({
      method: 'GET',
      url: '/settings',
      aborter_key,
    })
  }

  const editSettings = (
    body: Settings,
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<any>({
      method: 'POST',
      url: '/settings',
      body,
      aborter_key,
    })
  }

  const getFrontendSettings = (
    aborter_key = null as string | boolean | null 
  ) => {
    return makeRequest<SettingsFrontend>({
      method: 'GET',
      url: '/settings/frontend',
      aborter_key,
    })
  }

  return {
    getSettings,
    editSettings,
    getFrontendSettings,
  }
}
