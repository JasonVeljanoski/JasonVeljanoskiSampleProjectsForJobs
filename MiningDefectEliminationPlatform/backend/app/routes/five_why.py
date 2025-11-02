from app import crud, models, schemas, utils
from app.crud import five_why
from app.schemas import ImgPath
from fastapi import APIRouter, Body, Depends

router = APIRouter()


# ------------------
# READ
# ------------------
@router.get("", response_model=models.Five_Why_Full)
def get_investigation_five_why(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    investigation_id: int,
):
    return crud.five_why.get_kw_single(db, investigation_id=investigation_id)


# ------------------
# UPDATE
# ------------------
@router.put("", response_model=models.Five_Why_Full)
def update_five_why_full(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    edits: models.Investigation_Full,
):
    def create_responses(db, response):
        new_response = schemas.Five_Why_Response(
            cause=response.cause,
            reason=response.reason,
            attachments=utils.create_upload_files(
                response.files, ImgPath.FIVE_WHY.value, base_name="five_why", suffix="jpeg"
            ),
            children_responses=[create_responses(db, x) for x in response.children_responses],
        )
        db.add(new_response)
        return new_response

    fivewhy_edits = edits.five_why
    five_why = crud.five_why.update(db, fivewhy_edits, commit=False)
    five_why.root_response = create_responses(db, fivewhy_edits.root_response)
    # five_why.actions = utils.create_actions(fivewhy_edits.actions)

    # --------------------------------------

    db.commit()
    db.refresh(five_why)

    # --------------------------------------

    for action in fivewhy_edits.actions:
        db.query(schemas.Action).filter(schemas.Action.id == action.id).update(
            {"five_why_id": five_why.id, "updated": utils.get_time_now()}
        )

        # BRAND NEW ACTION
        if (
            not action.flash_report_id
            and not action.five_why_id
            and not action.root_cause_detail_id
        ):
            utils.broadcast_action_alert(db, action.id, [], True)

    # --------------------------------------

    # BROADCAST ALERTS
    utils.create_notification(db, user.id, "Five Why", "Section was updated successfully")

    # --------------------------------------

    # update logs to document who/when changed things
    crud.log.create(
        db,
        schemas.Log(
            five_why_id=five_why.id,
            user_id=user.id,
            log_type=schemas.enums.LogEnum.FIVE_WHY,
        ),
    )

    # --------------------------------------

    return five_why


@router.patch("/flash_report_action_ids")
def update_five_why_flash_report_action_ids(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    five_why_id: int,
    flash_report_action_ids: list[int] = Body(...),
):
    db.query(schemas.Five_Why).filter(schemas.Five_Why.id == five_why_id).update(
        {"flash_report_action_ids": flash_report_action_ids}
    )
    db.commit()

    return {"success": True}


# ------------------
# DELETE
# ------------------
@router.delete("")
def delete_five_why(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    id: int,
):
    # remove actions
    crud.action.delete_kw(db, five_why_id=id)

    # remove five why doc
    crud.five_why.delete(db, id=id)
