import { EnumRead } from './EnumRead'

export type GeneralImprovementInitiative = {
  id?: number
  created?: Date
  updated?: Date
  owner_ou_id?: number
  impact_ou_id?: number
  trigger_ids?: Array<number>
  triggers?: Array<EnumRead>
  primary_driver_id?: number
  primary_driver?: EnumRead
  secondary_driver_id?: number
  secondary_driver?: EnumRead
  cost_benefit_category_id?: number
  cost_benefit_category?: EnumRead
  benefit_frequency_id?: number
  benefit_frequency?: EnumRead
  tonnes?: number
  safety?: number
  availability?: number
  events?: number
  benefit_estimate_notes?: string
  notification?: string
  workorder?: string
}
