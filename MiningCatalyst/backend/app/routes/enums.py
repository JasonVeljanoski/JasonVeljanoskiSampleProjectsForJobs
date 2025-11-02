import datetime as dt

import pytz
from fastapi import APIRouter, Body, Depends
from sqlalchemy import MetaData
from sqlalchemy.event import listens_for

from app import crud, errors, models, schemas, utils

utc = pytz.UTC
router = APIRouter()


# ------------------
# CREATE
# ------------------
@router.post("/priority", response_model=models.EnumRead)
def add_priority(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    priority: models.EnumWrite,
):
    return crud.priority.create(db, priority)


@router.post("/status", response_model=models.EnumRead)
def add_status(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    status: models.EnumWrite,
):
    return crud.status.create(db, status)


@router.post("/trigger", response_model=models.EnumRead)
def add_trigger(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    status: models.EnumWrite,
):
    return crud.trigger.create(db, status)


@router.post("/primary_driver", response_model=models.EnumRead)
def add_primary_driver(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    status: models.EnumWrite,
):
    return crud.primary_driver.create(db, status)


@router.post("/secondary_driver", response_model=models.EnumRead)
def add_secondary_driver(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    status: models.EnumWrite,
):
    return crud.secondary_driver.create(db, status)


@router.post("/cost_benefit_category", response_model=models.EnumRead)
def add_cost_benefit_category(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    cost_benefit_category: models.EnumWrite,
):
    return crud.cost_benefit_category.create(db, cost_benefit_category)


@router.post("/benefit_frequency", response_model=models.EnumRead)
def add_benefit_frequency(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    benefit_frequency: models.EnumWrite,
):
    return crud.benefit_frequency.create(db, benefit_frequency)


# ------------------
# READ
# ------------------
@router.get("/all", response_model=models.AllEnumsRead)
def get_all_enums(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    class_names = [
        "priority",
        "status",
        "trigger",
        "primary_driver",
        "secondary_driver",
        "cost_benefit_category",
        "benefit_frequency",
    ]

    res = {
        class_name: getattr(utils.crud, class_name.lower()).all(db=db) for class_name in class_names
    }

    # remove when is_deleted is True
    for class_name in class_names:
        res[class_name] = [x for x in res[class_name] if not x.is_deleted]

    return res


@router.get("/priority/all", response_model=list[models.EnumRead])
def get_priorities(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.priority.all(db)


@router.get("/status/all", response_model=list[models.EnumRead])
def get_statuses(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.status.all(db)


@router.get("/trigger/all", response_model=list[models.EnumRead])
def get_triggers(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.trigger.all(db)


@router.get("/primary_driver/all", response_model=list[models.EnumRead])
def get_primary_drivers(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.primary_driver.all(db)


@router.get("/secondary_driver/all", response_model=list[models.EnumRead])
def get_secondary_drivers(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.secondary_driver.all(db)


@router.get("/cost_benefit_category/all", response_model=list[models.EnumRead])
def get_cost_benefit_categories(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.cost_benefit_category.all(db)


@router.get("/benefit_frequency/all", response_model=list[models.EnumRead])
def get_benefit_frequencies(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.benefit_frequency.all(db)


# ------------------
# UPDATE
# ------------------
@router.put("/priority", response_model=models.EnumRead)
def update_priority(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    priority: models.EnumWrite,
):
    return crud.priority.update(db, priority)


@router.put("/priority/all", response_model=list[models.EnumRead])
def update_priorities(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    priorities: list[models.EnumWrite],
):
    return crud.priority.update_all(db, priorities)


@router.put("/status", response_model=models.EnumRead)
def update_status(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    status: models.EnumWrite,
):
    return crud.status.update(db, status)


@router.put("/status/all", response_model=list[models.EnumRead])
def update_statuses(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    statuses: list[models.EnumWrite],
):
    return crud.status.update_all(db, statuses)


@router.put("/trigger", response_model=models.EnumRead)
def update_trigger(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    trigger: models.EnumWrite,
):
    return crud.trigger.update(db, trigger)


@router.put("/trigger/all", response_model=list[models.EnumRead])
def update_triggers(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    triggers: list[models.EnumWrite],
):
    return crud.trigger.update_all(db, triggers)


@router.put("/primary_driver", response_model=models.EnumRead)
def update_primary_driver(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    primary_driver: models.EnumWrite,
):
    return crud.primary_driver.update(db, primary_driver)


@router.put("/primary_driver/all", response_model=list[models.EnumRead])
def update_primary_drivers(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    primary_drivers: list[models.EnumWrite],
):
    return crud.primary_driver.update_all(db, primary_drivers)


@router.put("/secondary_driver", response_model=models.EnumRead)
def update_secondary_driver(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    secondary_driver: models.EnumWrite,
):
    return crud.secondary_driver.update(db, secondary_driver)


@router.put("/secondary_driver/all", response_model=list[models.EnumRead])
def update_secondary_drivers(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    secondary_drivers: list[models.EnumWrite],
):
    return crud.secondary_driver.update_all(db, secondary_drivers)


@router.put("/cost_benefit_category", response_model=models.EnumRead)
def update_cost_benefit_category(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    cost_benefit_category: models.EnumWrite,
):
    return crud.cost_benefit_category.update(db, cost_benefit_category)


@router.put("/cost_benefit_category/all", response_model=list[models.EnumRead])
def update_cost_benefit_categories(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    cost_benefit_category: list[models.EnumWrite],
):
    return crud.cost_benefit_category.update_all(db, cost_benefit_category)


@router.put("/benefit_frequency", response_model=models.EnumRead)
def update_benefit_frequency(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    benefit_frequency: models.EnumWrite,
):
    return crud.benefit_frequency.update(db, benefit_frequency)


@router.put("/benefit_frequency/all", response_model=list[models.EnumRead])
def update_benefit_frequencies(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    benefit_frequencies: list[models.EnumWrite],
):
    return crud.benefit_frequency.update_all(db, benefit_frequencies)


# ------------------
# DELETE
# ------------------
@router.delete("/priority")
def delete_priority(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    id: int,
):
    priority = db.query(schemas.Priority).get(id)

    # Note: don't use crud.delete because it will NOT trigger the before_delete listener
    db.delete(priority)
    db.commit()


@router.delete("/status")
def delete_status(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    id: int,
):
    status = db.query(schemas.Status).get(id)

    # Note: don't use crud.delete because it will NOT trigger the before_delete listener
    db.delete(status)
    db.commit()


@router.delete("/trigger")
def delete_trigger(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    id: int,
):
    trigger = db.query(schemas.Trigger).get(id)

    # Note: don't use crud.delete because it will NOT trigger the before_delete listener
    db.delete(trigger)
    db.commit()


@router.delete("/primary_driver")
def delete_primary_driver(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    id: int,
):
    primary_driver = db.query(schemas.PrimaryDriver).get(id)

    # Note: don't use crud.delete because it will NOT trigger the before_delete listener
    db.delete(primary_driver)
    db.commit()


@router.delete("/secondary_driver")
def delete_secondary_driver(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    id: int,
):
    secondary_driver = db.query(schemas.SecondaryDriver).get(id)

    # Note: don't use crud.delete because it will NOT trigger the before_delete listener
    db.delete(secondary_driver)
    db.commit()


@router.delete("/cost_benefit_category")
def delete_cost_benefit_category(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    id: int,
):
    cost_benefit_category = db.query(schemas.CostBenefitCategory).get(id)

    # Note: don't use crud.delete because it will NOT trigger the before_delete listener
    db.delete(cost_benefit_category)
    db.commit()


@router.delete("/benefit_frequency")
def delete_benefit_frequency(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    id: int,
):
    benefit_frequency = db.query(schemas.BenefitFrequency).get(id)

    # Note: don't use crud.delete because it will NOT trigger the before_delete listener
    db.delete(benefit_frequency)
    db.commit()


# ------------------
# LISTENERS
# ------------------
@listens_for(schemas.Priority, "before_delete")
def before_delete_priority(
    mapper,
    connection,
    target,
):
    db = utils.get_db()
    db = next(db)

    metadata = MetaData(bind=db.bind)
    metadata.reflect()

    # Define a list of schemas that reference Priority
    referencing_models = [
        (schemas.Initiative, "priority_id"),
        # todo: Add other schemas here...
    ]

    related_objects = {}
    for model, foreign_key_attr in referencing_models:
        # Check if the priority being deleted is referenced in the current model
        num_related_objects = (
            db.query(model).filter(getattr(model, foreign_key_attr) == target.id).count()
        )

        if num_related_objects > 0:
            related_objects[model.__tablename__] = num_related_objects

    if related_objects:
        message = "Cannot delete priority because it is referenced in the following tables:\n"
        for table_name, count in related_objects.items():
            message += f"       {table_name}: {count} \n"

        raise errors.CustomException(
            message=message,
            status=409,
        )


# ------------------------------------------------------------


@listens_for(schemas.Status, "before_delete")
def before_delete_status(
    mapper,
    connection,
    target,
):
    db = utils.get_db()
    db = next(db)

    metadata = MetaData(bind=db.bind)
    metadata.reflect()

    # Define a list of schemas that reference Status
    referencing_models = [
        (schemas.Initiative, "status_id"),
        # todo: Add other schemas here...
    ]

    related_objects = {}
    for model, foreign_key_attr in referencing_models:
        # Check if the status being deleted is referenced in the current model
        num_related_objects = (
            db.query(model).filter(getattr(model, foreign_key_attr) == target.id).count()
        )

        if num_related_objects > 0:
            related_objects[model.__tablename__] = num_related_objects

    if related_objects:
        message = "Cannot delete status because it is referenced in the following tables:\n"
        for table_name, count in related_objects.items():
            message += f"       {table_name}: {count} \n"

        raise errors.CustomException(
            message=message,
            status=409,
        )


# ------------------------------------------------------------


@listens_for(schemas.Trigger, "before_delete")
def before_delete_trigger(
    mapper,
    connection,
    target,
):
    db = utils.get_db()
    db = next(db)

    metadata = MetaData(bind=db.bind)
    metadata.reflect()

    # Define a list of schemas that reference Status
    referencing_models = [
        (schemas.initiative, "trigger_id"),
        # todo: Add other schemas here...
    ]

    related_objects = {}
    for model, foreign_key_attr in referencing_models:
        # Check if the status being deleted is referenced in the current model
        num_related_objects = (
            db.query(model).filter(getattr(model, foreign_key_attr) == target.id).count()
        )

        if num_related_objects > 0:
            related_objects[model.__tablename__] = num_related_objects

    if related_objects:
        message = "Cannot delete status because it is referenced in the following tables:\n"
        for table_name, count in related_objects.items():
            message += f"       {table_name}: {count} \n"

        raise errors.CustomException(
            message=message,
            status=409,
        )


# ------------------------------------------------------------


@listens_for(schemas.PrimaryDriver, "before_delete")
def before_delete_primary_driver(
    mapper,
    connection,
    target,
):
    db = utils.get_db()
    db = next(db)

    metadata = MetaData(bind=db.bind)
    metadata.reflect()

    # Define a list of schemas that reference Status
    referencing_models = [
        (schemas.Initiative, "primary_driver_id"),
        # todo: Add other schemas here...
    ]

    related_objects = {}
    for model, foreign_key_attr in referencing_models:
        # Check if the status being deleted is referenced in the current model
        num_related_objects = (
            db.query(model).filter(getattr(model, foreign_key_attr) == target.id).count()
        )

        if num_related_objects > 0:
            related_objects[model.__tablename__] = num_related_objects

    if related_objects:
        message = "Cannot delete status because it is referenced in the following tables:\n"
        for table_name, count in related_objects.items():
            message += f"       {table_name}: {count} \n"

        raise errors.CustomException(
            message=message,
            status=409,
        )


# ------------------------------------------------------------


@listens_for(schemas.SecondaryDriver, "before_delete")
def before_delete_secondary_driver(
    mapper,
    connection,
    target,
):
    db = utils.get_db()
    db = next(db)

    metadata = MetaData(bind=db.bind)
    metadata.reflect()

    # Define a list of schemas that reference Status
    referencing_models = [
        (schemas.Initiative, "secondary_driver_id"),
        # todo: Add other schemas here...
    ]

    related_objects = {}
    for model, foreign_key_attr in referencing_models:
        # Check if the status being deleted is referenced in the current model
        num_related_objects = (
            db.query(model).filter(getattr(model, foreign_key_attr) == target.id).count()
        )

        if num_related_objects > 0:
            related_objects[model.__tablename__] = num_related_objects

    if related_objects:
        message = "Cannot delete status because it is referenced in the following tables:\n"
        for table_name, count in related_objects.items():
            message += f"       {table_name}: {count} \n"

        raise errors.CustomException(
            message=message,
            status=409,
        )


# ------------------------------------------------------------


@listens_for(schemas.CostBenefitCategory, "before_delete")
def before_delete_cost_benefit_frequency(
    mapper,
    connection,
    target,
):
    db = utils.get_db()
    db = next(db)

    metadata = MetaData(bind=db.bind)
    metadata.reflect()

    # Define a list of schemas that reference Status
    referencing_models = [
        (schemas.Initiative, "cost_benefit_category_id"),
        # todo: Add other schemas here...
    ]

    related_objects = {}
    for model, foreign_key_attr in referencing_models:
        # Check if the status being deleted is referenced in the current model
        num_related_objects = (
            db.query(model).filter(getattr(model, foreign_key_attr) == target.id).count()
        )

        if num_related_objects > 0:
            related_objects[model.__tablename__] = num_related_objects

    if related_objects:
        message = "Cannot delete status because it is referenced in the following tables:\n"
        for table_name, count in related_objects.items():
            message += f"       {table_name}: {count} \n"

        raise errors.CustomException(
            message=message,
            status=409,
        )


# ------------------------------------------------------------


@listens_for(schemas.BenefitFrequency, "before_delete")
def before_delete_benefit_frequency(
    mapper,
    connection,
    target,
):
    db = utils.get_db()
    db = next(db)

    metadata = MetaData(bind=db.bind)
    metadata.reflect()

    # Define a list of schemas that reference Status
    referencing_models = [
        (schemas.Initiative, "benefit_frequency_id"),
        # todo: Add other schemas here...
    ]

    related_objects = {}
    for model, foreign_key_attr in referencing_models:
        # Check if the status being deleted is referenced in the current model
        num_related_objects = (
            db.query(model).filter(getattr(model, foreign_key_attr) == target.id).count()
        )

        if num_related_objects > 0:
            related_objects[model.__tablename__] = num_related_objects

    if related_objects:
        message = "Cannot delete status because it is referenced in the following tables:\n"
        for table_name, count in related_objects.items():
            message += f"       {table_name}: {count} \n"

        raise errors.CustomException(
            message=message,
            status=409,
        )
