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


app = FastAPI(
    title=config.PROJECT_NAME,
    description="??",
    version="v1",
    # docs_url="/api/docs",
    # redoc_url=None,
    # openapi_url="/api/openapi.json",
    root_path="/api",
)


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


@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi(user: schemas.User = utils.IS_SUPER_USER):
    openapi_schema = app.openapi()
    return openapi_schema


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(
    request: Request,
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_SUPER_USER,
):
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
