import { EnumRead } from './EnumRead'

export type AllEnumsRead = {
  priority: Array<EnumRead>
  status: Array<EnumRead>
  trigger: Array<EnumRead>
  primary_driver: Array<EnumRead>
  secondary_driver: Array<EnumRead>
  cost_benefit_category: Array<EnumRead>
  benefit_frequency: Array<EnumRead>
}
