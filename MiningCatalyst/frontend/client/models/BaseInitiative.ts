import { EnumRead } from './EnumRead'
import { InitiativeTypeEnum } from './InitiativeTypeEnum'

export type BaseInitiative = {
  id?: number
  created?: Date
  updated?: Date
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
