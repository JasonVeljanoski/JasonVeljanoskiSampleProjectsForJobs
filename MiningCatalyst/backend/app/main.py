import glob
import logging
import os
import sys
from functools import partial
from importlib import import_module
from os import path

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.cors import CORSMiddleware

from app import config, schemas, utils
from app.utils import errors

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
    root_path="/api",
    generate_unique_id_function=lambda x: x.name,
)


# -------------------------------------------


app.add_middleware(GZipMiddleware, minimum_size=5000)

files = glob.glob("app/routes/**/*.py", recursive=True)

files.sort()
for f in files:
    route = f[11:-3]

    module_name = f"app.routes.{route.replace('/', '.')}"
    module = import_module(module_name)

    if not hasattr(module, "router"):
        continue

    router = module.router

    if route.endswith("__main__"):
        route = route[:-9]
    tag = route.replace("/", " - ").replace("_", " ").title()

    if isinstance(router, APIRouter):
        app.include_router(
            router,
            prefix="/" + route,
            tags=[tag],
        )
    elif isinstance(router, FastAPI):
        app.mount("/" + route, router)

# -------------------------------------------


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


if config.DEV_MODE:
    from app.openapi_generator.main import generate_openapi

    generate_openapi(app)
