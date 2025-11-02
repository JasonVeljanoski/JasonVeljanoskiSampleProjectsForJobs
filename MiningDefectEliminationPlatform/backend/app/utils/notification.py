def create_notification(db, user_id, title, body, tags=[], status="success"):
    """
    1) Create a notification entry in db
    2) Pushes a notification via the socket connection
    """
    from app import crud, schemas, sockets
    from app.schemas.enums import NotificationTypeEnum

    # setup type
    type = NotificationTypeEnum.INFO
    if status == "success":
        type = NotificationTypeEnum.SUCCESS
    elif status == "info":
        type = NotificationTypeEnum.INFO
    elif status == "warning":
        type = NotificationTypeEnum.WARNING

    # create notification
    notification = schemas.Notification(
        title=title, message=body, tags=tags, user_id=user_id, type=type
    )
    notification = crud.notification.create(db, notification)

    # send notification
    body = {
        column: str(getattr(notification, column)) for column in notification.__table__.c.keys()
    }
    body["type"] = status

    sockets.send(user_id, sockets.Socket_Group.NOTIFICATION, body)


def broadcast_action_alert(db, id, old_owners, is_new=False):
    """ """
    from app import crud, email, schemas, sockets, utils

    # -----------------------------------------------

    new_obj = utils.refresh_action(db, id)
    if not new_obj.id:
        return

    # -----------------------------------------------

    # New owners/supervisor
    new_owners = []
    new_owners = new_owners + new_obj.owner_ids
    new_owners.append(new_obj.supervisor_id)
    new_owners = list(set(new_owners))

    removed_owners = list(set(old_owners) - set(new_owners))

    # -----------------------------------------------

    # EMAIL
    for user_id in new_owners:
        title_text = "New DEP Action Created" if is_new else "Updated DEP Action"
        subject = f"{title_text} Action"
        header = title_text
        user = crud.user.get(db, user_id)
        email.action_email(db, user.email, subject, header, new_obj)

    # ! 2023-01-16: Feature to only send email to users when an action is created
    # for user_id in removed_owners:
    #     subject = "Action owners changed"
    #     header = f"Action #{new_obj.id} is no longer your responsibility"
    #     user = crud.user.get(db, user_id)
    #     email.action_email(db, user.email, subject, header, new_obj)

    # -----------------------------------------------

    # SEND NOTIFICATION TO NEW USERS
    response = dict(id=new_obj.id, data=new_obj)
    for user_id in new_owners:

        # Update Socket
        if new_obj.status == schemas.StatusEnum.OPEN:
            sockets.send(user_id, sockets.Socket_Group.ACTION, response)
        else:
            sockets.send(user_id, sockets.Socket_Group.ACTION, dict(id=new_obj.id, data=None))

        # Send Notification
        title = new_obj.title
        create_notification(
            db,
            user_id,
            title,
            f"{new_obj.title}",
            tags=[],
            status="success",
        )

    # -----------------------------------------------

    # SEND NOTIFICATION TO REMOVED USERS
    response = dict(id=new_obj.id, data=None)
    for user_id in removed_owners:
        sockets.send(user_id, sockets.Socket_Group.ACTION, response)

        create_notification(
            db,
            user_id,
            "Action is no longer your responsibility (Action owners changed)",
            new_obj.title,
            tags=[],
            status="info",
        )


# ----------------------------------------------------------------------


def broadcast_investigation_alert(db, id, title, old_owners, is_new=False):
    """ """
    from app import crud, email, schemas, sockets, utils

    # -----------------------------------------------

    new_obj = utils.refresh_investigation(db, id)

    # -----------------------------------------------

    # New owners/supervisor
    new_owners = []
    new_owners = new_owners + new_obj.owner_ids
    new_owners.append(new_obj.supervisor_id)
    new_owners = list(set(new_owners))

    removed_owners = list(set(old_owners) - set(new_owners))

    # -----------------------------------------------

    # TODO check the investigation is created by the user_id or not to decide to use create or update in the email.

    # EMAIL
    for user_id in new_owners:
        title_text = "New DEP Investigation Created" if is_new else "Updated DEP Investigation"
        subject = f"{title_text} Investigation {title}"
        # header = f"{title_text} Investigation is waiting for you"
        header = f"{title_text}"
        user = crud.user.get(db, user_id)
        email.investigation_email(db, user.email, subject, header, new_obj)

    # ! 2023-01-16: Feature to only send email to users when an investigation is created
    # for user_id in removed_owners:
    #     subject = "Investigation owners changed"
    #     header = f"Investigation #{new_obj.id} is no longer your responsibility"
    #     user = crud.user.get(db, user_id)
    #     email.investigation_email(db, user.email, subject, header, new_obj)

    # -----------------------------------------------

    # SEND NOTIFICATION TO NEW USERS
    response = dict(id=new_obj.id, data=new_obj)
    for user_id in new_owners:

        # Update Socket
        if new_obj.status == schemas.StatusEnum.OPEN:
            sockets.send(user_id, sockets.Socket_Group.INVESTIGATION, response)
        else:
            sockets.send(
                user_id, sockets.Socket_Group.INVESTIGATION, dict(id=new_obj.id, data=None)
            )

        title = f"Investigation #{new_obj.id}"
        create_notification(
            db,
            user_id,
            title,
            f"{new_obj.title}",
            tags=[],
            status="success",
        )

    # -----------------------------------------------

    # SEND NOTIFICATION TO REMOVED USERS
    response = dict(id=new_obj.id, data=None)
    for user_id in removed_owners:
        sockets.send(user_id, sockets.Socket_Group.INVESTIGATION, response)

        create_notification(
            db,
            user_id,
            f"Investigation #{new_obj.id} is no longer your responsibility",
            f"{new_obj.title}",
            tags=[],
            status="info",
        )


# ----------------------------------------------------------------------


def broadcast_action_update_socket(db, action_id):
    from app import sockets, utils

    new_obj = utils.refresh_action(db, action_id)
    if not new_obj.id:
        return

    all_owners = []
    all_owners = all_owners + new_obj.owner_ids
    all_owners.append(new_obj.supervisor_id)
    all_owners = list(set(all_owners))

    # SEND NOTIFICATION TO NEW USERS
    response = dict(id=new_obj.id, data=new_obj)
    for user_id in all_owners:
        sockets.send(user_id, sockets.Socket_Group.ACTION, response)


# ----------------------------------------------------------------------


def broadcast_investigation_update_socket(db, investigation_id):
    from app import sockets, utils

    new_obj = utils.refresh_investigation(db, investigation_id)
    if not new_obj.id:
        return

    all_owners = []
    all_owners = all_owners + new_obj.owner_ids
    all_owners.append(new_obj.supervisor_id)
    all_owners = list(set(all_owners))

    # SEND NOTIFICATION TO NEW USERS
    response = dict(id=new_obj.id, data=new_obj)
    for user_id in all_owners:
        sockets.send(user_id, sockets.Socket_Group.INVESTIGATION, response)


# ----------------------------------------------------------------------
