import { BaseInitiative } from './BaseInitiative'
import { EnumRead } from './EnumRead'
import { InitiativeTypeEnum } from './InitiativeTypeEnum'

export type FullInitiative = {
  id?: number
  created?: Date
  updated?: Date
  impact_ou_id?: number
  floc_id?: number
  equipment_id?: number
  primary_driver_id?: number
  primary_driver?: EnumRead
  secondary_driver_id?: number
  secondary_driver?: EnumRead
  cost?: number
  tonnes?: number
  safety?: number
  availability?: number
  events?: number
  benefit_frequency?: EnumRead
  benefit_estimate_notes?: string
  notification?: string
  workorder?: string
  purchase_request?: string
  purchase_order?: string
  owner_ou_id?: number
  trigger_ids?: Array<number>
  triggers?: Array<EnumRead>
  maintenance_plan?: string
  cost_benefit_category_id?: number
  cost_benefit_category?: EnumRead
  benefit_frequency_id?: number
  parent_initiative_id?: number
  parent_initiative?: BaseInitiative
  type?: InitiativeTypeEnum
  date_opened?: Date
  target_completion_date?: Date
  title?: string
  description?: string
  project_owner_id?: number
  supervisor_id?: number
  priority_id?: number
  priority?: EnumRead
  status_id?: number
  status?: EnumRead
  change_request?: string
}
