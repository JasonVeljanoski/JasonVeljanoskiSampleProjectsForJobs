from .files import create_upload_files


def create_actions(actions):
    from app import schemas
    from app.schemas.enums import ImgPath

    # CREATE ACTIONS
    res = []
    for action in actions:
        new = schemas.Action(
            investigation_id=action.investigation_id,
            title=action.title,
            description=action.description,
            status=action.status,
            priority=action.priority,
            date_due=action.date_due,
            date_closed=action.date_closed,
            supervisor_id=action.supervisor_id,
            owners=[
                schemas.Action_Owner_Association(action_id=None, user_id=_owner_id)
                for _owner_id in action.owner_ids
            ],
            attachments=create_upload_files(
                action.files, ImgPath.ACTION.value, base_name="action", suffix="jpeg"
            ),
        )

        res.append(new)

    return res
