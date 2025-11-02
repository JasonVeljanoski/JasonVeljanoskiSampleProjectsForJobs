import logging

from fastapi import APIRouter, BackgroundTasks, Depends

from app import crud, models, schemas, utils

router = APIRouter()


logger = logging.getLogger(__name__)


def update_supervisors():
    db = next(utils.get_db())
    db_sf = next(utils.get_sf())

    sql = """
        SELECT
            "SupervisorEmail", "EmployeeEmail", "SuperTier"
        FROM
            AA_ASSETS_FIXEDPLANT.SELFSERVICE."ap_SupervisorTeams"
        WHERE
            "SupervisorEmail" is not NULL and "EmployeeEmail" is not NULL and "SupervisorEmail" != "EmployeeEmail"
    """

    items = db_sf.execute(sql).fetchall()

    logger.info(f"Found {len(items)} items")

    try:
        for item in items:
            supervisor = crud.user.get_kw_single(db, email=item.SupervisorEmail.lower())
            employee = crud.user.get_kw_single(db, email=item.EmployeeEmail.lower())

            # update supervisor
            if supervisor and employee:
                # filter items by employee email
                filtered_items = [i for i in items if i.EmployeeEmail == item.EmployeeEmail.lower()]
                # get row with highest tier
                filtered_items = sorted(filtered_items, key=lambda x: x.SuperTier, reverse=True)

                # get immediate supervisor email
                supervisor_email = filtered_items[0].SupervisorEmail
                immediate_supervisor = crud.user.get_kw_single(db, email=supervisor_email.lower())

                # update immediate supervisor
                if immediate_supervisor:
                    employee.supervisor_id = immediate_supervisor.id
                    db.commit()

    except Exception as e:
        logger.exception(e)

    db.close()
    db_sf.close()


# todo: make cron - once a week or fortnight or month
@router.put("/update_supervisors")
async def update_supervisors_task(
    background_tasks: BackgroundTasks,
    db=Depends(utils.get_db),
    db_sf=Depends(utils.get_sf),
    valid=Depends(utils.token_auth),
):
    background_tasks.add_task(update_supervisors)
    return {"message": "Updating supervisors in the background"}
