from app import crud, schemas
from app.schemas.enums import LogTypeEnum

from .base import CRUD_Base


class Log(CRUD_Base[schemas.Log]):
    def create_action_log(self, db, logType, userId, actionId):
        if logType != LogTypeEnum.ACTION_CREATION and logType != LogTypeEnum.ACTION_UPDATE:
            raise Exception()

        log_record = schemas.Log()
        log_record.type = logType.value
        log_record.user_id = userId
        log_record.action_id = actionId

        crud.log.create(db, log_record)

    def create_workgroup_log(self, db, logType, userId, workgroupId):
        if logType != LogTypeEnum.WORKGROUP_CREATION and logType != LogTypeEnum.WORKGROUP_UPDATE:
            raise Exception()

        log_record = schemas.Log()
        log_record.type = logType.value
        log_record.user_id = userId
        log_record.workgroup_id = workgroupId

        crud.log.create(db, log_record)

    def create_login_log(self, db, userId):
        log_record = schemas.Log()
        log_record.type = LogTypeEnum.LOGIN.value
        log_record.user_id = userId

        crud.log.create(db, log_record)

    def create_ingestion_log(self, db, syncUuid, numCreated, numArchived, numUpdated):
        log_record = schemas.Log()
        log_record.type = LogTypeEnum.ACTION_INGESTION_SYNC.value
        log_record.sync_uuid = syncUuid
        log_record.total_actions_created = numCreated
        log_record.total_actions_archived = numArchived
        log_record.total_actions_updated = numUpdated

        crud.log.create(db, log_record)

    def create_teams_ingestion_log(self, db, syncUuid, numActionsCreated, numActionsArchived, numWorkgroupsCreated, workgroupIdsInvolved, userIdsInvolved):
        log_record = schemas.Log()
        log_record.type = LogTypeEnum.TEAMS_INGESTION_SYNC.value
        log_record.sync_uuid = syncUuid
        log_record.total_actions_created = numActionsCreated
        log_record.total_actions_archived = numActionsArchived
        log_record.total_workgroups_created = numWorkgroupsCreated
        log_record.workgroup_ids_involved = workgroupIdsInvolved
        log_record.user_ids_involved = userIdsInvolved

        crud.log.create(db, log_record)


class Update_History(CRUD_Base[schemas.Update_History]):
    pass


log = Log()
update_history = Update_History()

"""
class Log(CRUD_Base[schemas.Log]):
    pass


class Action_Log(CRUD_Base[schemas.Action_Log]):
    pass


class Workgroup_Log(CRUD_Base[schemas.Workgroup_Log]):
    pass



log = Log()
action_log = Action_Log()
workgroup_log = Workgroup_Log()
"""
