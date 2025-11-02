export type { AllEnumsRead } from './models/AllEnumsRead'
export type { BaseInitiative } from './models/BaseInitiative'
export type { EnumRead } from './models/EnumRead'
export type { EnumWrite } from './models/EnumWrite'
export type { Equipment } from './models/Equipment'
export type { Floc } from './models/Floc'
export type { FullInitiative } from './models/FullInitiative'
export type { GeneralImprovementInitiative } from './models/GeneralImprovementInitiative'
export type { HTTPValidationError } from './models/HTTPValidationError'
export { InitiativeTypeEnum } from './models/InitiativeTypeEnum'
export type { OrganisationalUnit } from './models/OrganisationalUnit'
export type { Settings } from './models/Settings'
export type { SettingsFrontend } from './models/SettingsFrontend'
export type { User } from './models/User'
export type { UserBasic } from './models/UserBasic'
export type { ValidationError } from './models/ValidationError'

import { useEnumsRouter } from './services/EnumsRouter'
import { useEquipmentRouter } from './services/EquipmentRouter'
import { useExampleRouter } from './services/ExampleRouter'
import { useFlocRouter } from './services/FlocRouter'
import { useInitiativeRouter } from './services/InitiativeRouter'
import { useListsRouter } from './services/ListsRouter'
import { useSettingsRouter } from './services/SettingsRouter'
import { useStaticRouter } from './services/StaticRouter'
import { useTasksRouter } from './services/TasksRouter'
import { useUserRouter } from './services/UserRouter'


export function useApiRouter() {
  const EnumsRouter = useEnumsRouter()
  const EquipmentRouter = useEquipmentRouter()
  const ExampleRouter = useExampleRouter()
  const FlocRouter = useFlocRouter()
  const InitiativeRouter = useInitiativeRouter()
  const ListsRouter = useListsRouter()
  const SettingsRouter = useSettingsRouter()
  const StaticRouter = useStaticRouter()
  const TasksRouter = useTasksRouter()
  const UserRouter = useUserRouter()

  return {
    EnumsRouter,
    EquipmentRouter,
    ExampleRouter,
    FlocRouter,
    InitiativeRouter,
    ListsRouter,
    SettingsRouter,
    StaticRouter,
    TasksRouter,
    UserRouter,
  }
}