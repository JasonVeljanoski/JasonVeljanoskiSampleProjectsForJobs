from fastapi import APIRouter, Depends

from app import models, schemas, utils

router = APIRouter()


# -----------------------------------
# GETS
# -----------------------------------
@router.get("/equipments", response_model=list[models.Equipment])
def all_equipments(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return db.query(schemas.Equipment).all()


@router.get("/organisational_units", response_model=list[models.OrganisationalUnit])
def organisational_units(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return db.query(schemas.OrganisationalUnit).all()


# -----------------------------------
# SEARCHES
# -----------------------------------


@router.get("/organisational_units/search/area", response_model=list[models.OrganisationalUnit])
def get_organisation_areas(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    search: str = None,
):
    return (
        db.query(schemas.OrganisationalUnit)
        .filter(schemas.OrganisationalUnit.area.ilike(f"%{search}%"))
        .all()
    )


@router.get(
    "/organisational_units/search/department", response_model=list[models.OrganisationalUnit]
)
def get_organisation_units(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    search: str = None,
):
    return (
        db.query(schemas.OrganisationalUnit)
        .filter(schemas.OrganisationalUnit.department.ilike(f"%{search}%"))
        .all()
    )
