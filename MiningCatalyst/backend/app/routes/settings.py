from fastapi import APIRouter, Body, Depends

from app import config, crud, errors, schemas, utils

router = APIRouter()


@router.get("", response_model=utils.Settings)
def get_settings(*, db=Depends(utils.get_db), user: schemas.User = utils.IS_SUPER_USER):
    return utils.get_settings()


@router.post("")
def edit_settings(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_SUPER_USER,
    settings: utils.Settings = Body(...),
):
    return utils.edit_settings(settings)


@router.get("/frontend", response_model=utils.SettingsFrontend)
def get_frontend_settings(*, db=Depends(utils.get_db), user: schemas.User = utils.IS_LOGGED_IN):
    return utils.get_frontend_settings()


# ----------------------------------------------------------------------------------------

# todo: implement the below (looks useful)
# @router.post("/clone_prod")
# def clone_prod(*, user: schemas.User = utils.IS_SUPER_USER):
#     if config.ENV == "prod":
#         raise errors.CustomException("You cannot clone prod")

#     try:
#         # Save the current db
#         dump_database(config.POSTGRES_SERVER, "current_db.sql")

#         if sql_utils.database_exists(config.SQLALCHEMY_DATABASE_URI):
#             sql_utils.drop_database(config.SQLALCHEMY_DATABASE_URI)

#         sql_utils.create_database(config.SQLALCHEMY_DATABASE_URI)

#         dump_database(config.POSTGRES_SERVER_PROD, "prod_db.sql")
#         restore_database(config.POSTGRES_SERVER, "prod_db.sql")

#         run_alembic()

#         subprocess.run(["rm", "prod_db.sql"])

#         return {"message": "Cloned prod"}
#     except Exception as e:
#         restore_database(config.POSTGRES_SERVER, "current_db.sql")

#         return {"message": "Error cloning prod", "error": str(e)}
#     finally:
#         subprocess.run(["rm", "current_db.sql"])


# def dump_database(host, filename):
#     dump_command = f"pg_dump -Fc -h {host} -U {config.POSTGRES_USER} -d {config.POSTGRES_DB} -f {filename}"
#     subprocess.run(dump_command.split(" "), check=True, env={"PGPASSWORD": config.POSTGRES_PASSWORD})


# def restore_database(host, filename):
#     restore_command = f"pg_restore -h {host} -U {config.POSTGRES_USER} -d {config.POSTGRES_DB} -v {filename}"
#     subprocess.run(restore_command.split(" "), check=True, env={"PGPASSWORD": config.POSTGRES_PASSWORD})


# def run_alembic():
#     from alembic import command
#     from alembic.config import Config

#     alembic_cfg = Config("alembic.ini")
#     alembic_cfg.set_main_option("sqlalchemy.url", config.SQLALCHEMY_DATABASE_URI)
#     command.upgrade(alembic_cfg, "head")
