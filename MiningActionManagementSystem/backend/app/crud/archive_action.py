from app import crud, schemas, utils
from app.schemas.enums import StatusEnum

from .base import CRUD_Base


class Archive_Action(CRUD_Base[schemas.Archive_Action]):

    """
    schema - schema type for the type of action to run this on - e.g. schemas.ACE_Action
    actionIds_to_exclude - the actions we don't want to archive. The actions of schema type that are not in this IDs list
                            will be archived
                                ** The way we call this method in Action_Ingestion routes, is once we have ingested a collection of records,
                                   we save the IDs of the records we have seen in a list, and then we want to delete/archive the Actions that
                                   don't exist in this list. Therefore, actionIds_to_exclude is the list of Action IDs we want to KEEP, and this
                                   method uses '.id.not_in(actionIds_to_exclude)', to then perform the operations on the actions to delete/archive.
                                **
    sourceId - default set to False. If set to True, instead of making the initial query by schema.id, will use schema.source_id,
                and thus, actionIds_to_exclude should be sourceIds to exclude
    """

    # TODO - rework this function & archive_actions to be one function
    # This one is only different in that it is supplied the action ids to delete, as opposed to archive_actions which is supplied the IDs to keep (which is a bit odd tbqh - TODO refactor)
    def archive_actions_teams(self, db, actionIds_to_delete, syncUUID):
        numArchived = 0

        result = (
            db.query(schemas.Teams_Action)
            .filter(schemas.Teams_Action.id.in_(actionIds_to_delete))
            .filter(schemas.Teams_Action.is_deleted.isnot(True))
            .all()
        )

        for record in result:
            record.status = StatusEnum.CLOSED
            record.is_deleted = True
            db.commit()
            crud.archive_action.create_archive_action_record(db, record, syncUUID)
            numArchived = numArchived + 1

        return numArchived

    def archive_actions(self, db, schema, actionIds_to_exclude, syncUUID, sourceId=False):

        numArchived = 0

        if sourceId == False:
            result = (
                db.query(schema)
                .filter(schema.id.not_in(actionIds_to_exclude))
                .filter(schema.is_deleted.isnot(True))
                .all()
            )  # list of schemas.XXXX_Action with records we want to archive
        else:
            result = (
                db.query(schema)
                .filter(schema.source_id.not_in(actionIds_to_exclude))
                .filter(schema.is_deleted.isnot(True))
                .all()
            )

        # Set the actual Action record to CLOSED, then create a Archive_Action record for that action.
        for record in result:
            record.status = StatusEnum.CLOSED
            record.is_deleted = True
            db.commit()
            crud.archive_action.create_archive_action_record(db, record, syncUUID)
            numArchived = numArchived + 1

        return numArchived

    # Create a Archive_Action record from a Action record (schemas.Action object)
    def create_archive_action_record(self, db, action, syncUUID):

        # Convert action object into schemas.Archive_Action obj
        archive_action = schemas.Archive_Action()
        archive_action.title = action.title
        archive_action.description = action.description
        archive_action.priority = action.priority.name

        # owner_id, supervisor_id - get emails
        if action.owner_id != None:
            owner_user = crud.user.get(db, action.owner_id)
            archive_action.owner_email = owner_user.email

        if action.supervisor_id != None:
            supervisor_user = crud.user.get(db, action.supervisor_id)
            archive_action.supervisor_email = supervisor_user.email

        archive_action.source_created = action.source_created
        archive_action.source_updated = action.source_updated

        archive_action.action_created = action.created
        archive_action.action_id = action.id

        archive_action.start_date = action.start_date
        archive_action.date_due = action.date_due

        archive_action.privacy = action.privacy.name
        archive_action.status = action.status.name

        archive_action.date_closed = action.date_closed
        archive_action.source_id = action.source_id

        archive_action.completed = action.completed
        archive_action.functional_location = action.functional_location
        archive_action.work_center = action.work_center
        archive_action.link = action.link

        archive_action.completed = action.completed
        archive_action.functional_location = action.functional_location
        archive_action.work_center = action.work_center
        archive_action.link = action.link
        archive_action.action_metadata = str(action.action_metadata)

        if action.dep_extra_owner_id != None:
            extra_owner_user = crud.user.get(db, action.dep_extra_owner_id)
            archive_action.dep_extra_owner_email = extra_owner_user.email

        archive_action.type = action.type

        member_emails = []
        for member in action.members:
            member_emails.append(member.email)
        archive_action.member_emails = ",".join(member_emails)

        workgroup_titles = []
        for workgroup in action.workgroups:
            workgroup_titles.append(workgroup.title)
        archive_action.workgroup_titles = ",".join(workgroup_titles)

        archive_action.archive_datetime = utils.get_time_now()
        archive_action.is_archived = 1
        archive_action.syncUUID = syncUUID

        crud.archive_action.create(db, archive_action)


archive_action = Archive_Action()
