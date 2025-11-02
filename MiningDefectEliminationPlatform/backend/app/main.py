import glob
import logging
import os
import sys
from functools import partial
from importlib import import_module
from os import path

from app import config, schemas, utils
from app.utils import errors
from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.cors import CORSMiddleware

# -------------------------------------------

console_handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s][%(process)d][%(filename)s:%(lineno)d] %(message)s"
)
console_handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)
root_logger.setLevel(logging.INFO)

# todo: add and test that cron jobs still work
app = FastAPI(
    title="DEP",
    description="??",
    version="v1",
    # docs_url=None,
    # redoc_url=None,
    # openapi_url=None,
    root_path="/api",
)

# app = FastAPI(
#     title="DEP",
#     description="Defect Elimination Platform",
#     contact={
#         "name": "Enco Group Pty Ltd",
#         "email": "dev@enco.net.au",
#         "url": "https://enco.net.au",
#     },
#     docs_url=None,
#     redoc_url=None,
#     openapi_url=None,
#     root_path="/api",
# )


# -------------------------------------------


app.add_middleware(GZipMiddleware, minimum_size=5000)

files = glob.glob("app/routes/*.py")

files.sort()
for f in files:
    route = path.basename(f[:-3])
    if not route.startswith("__"):
        app.include_router(
            import_module("app.routes." + route).router,
            prefix="/" + route,
            tags=[route],
        )

# -------------------------------------------

# TODO: limit docs to only admins - make sure you dont stuff up cron jobs
@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi(user: schemas.User = Depends(utils.get_current_user)):
    if not user or not user.is_admin:
        return RedirectResponse(f"https://{config.SERVER_NAME}/auth?redirect=docs")
    openapi_schema = app.openapi()
    return openapi_schema


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(request: Request, *, db=Depends(utils.get_db)):

    try:
        user = utils.get_current_user(db=db, token=None, request=request)
    except Exception:
        return RedirectResponse(f"https://{config.SERVER_NAME}/auth?redirect=docs")

    if not user or not user.is_admin:
        raise errors.CredentialsInvalidException

    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title=f"{app.title} - Swagger UI",
    )


# -------------------------------------------


@app.exception_handler(errors.CustomException)
async def credentails_invalid_wrapper(request, exc):
    return JSONResponse(status_code=exc.status, content={"message": exc.message})


# --------------------------------------------------

root_directory = "/attachments"
attachment_folders = ("general",)

concat_root_path = partial(os.path.join, root_directory)
make_directory = partial(os.makedirs, exist_ok=True)

for path_items in map(concat_root_path, attachment_folders):
    make_directory(path_items)
