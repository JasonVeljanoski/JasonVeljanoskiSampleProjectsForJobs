from .files import create_upload_files
from app import schemas
from app.schemas.enums import ImgPath


def create_actions(actions):
    res = []
    for action in actions:
        new = schemas.Action(
            title=action.title,
            description=action.description,
            priority=action.priority,
            date_due=action.date_due,
            owners=[
                schemas.Action_Owner_Association(
                    action_id=action.id, user_email=_action_member_emails
                )
                for _action_member_email in action.action_member_emails
            ],
            attachments=create_upload_files(
                action.files, ImgPath.ACTION.value, base_name="action", suffix="jpeg"
            ),
        )

        res.append(new)

    return res


def duplicate_comments(db, cls_comments, action_id, comments):
    for comment in comments:
        new = cls_comments(
            action_id=action_id,
            user_id=comment.user_id,
            datetime=comment.datetime,
            comment=comment.comment,
            fullname=comment.fullname,
        )
        db.add(new)
    db.commit()
