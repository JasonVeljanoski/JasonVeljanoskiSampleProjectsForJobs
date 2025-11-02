def refresh_action(db, id):
    from app import crud, models

    item = crud.action.get(db, id)

    if not item:
        return None

    return models.Action.from_orm(item)


def refresh_investigation(db, id):
    from app import crud, models

    item = crud.investigation.get(db, id)

    if not item:
        return None

    return models.Investigation.from_orm(item)


def refresh_investigation_full(db, id):
    from app import crud, models

    item = crud.investigation.get(db, id)

    if not item:
        return None

    return models.Investigation_Full.from_orm(item)
