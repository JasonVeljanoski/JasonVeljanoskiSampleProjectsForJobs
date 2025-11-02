import json
import logging
import os
import re
import shutil
import time

from fastapi import FastAPI

from .models import save_models
from .openapi_types import Parameter, Path, Schema, Schema2, Specification
from .routers import group_by_tag, save_routers
from .services import save_services

logger = logging.getLogger(__name__)


OUTPUT_DIR = "/client"
CORE_DIR = f"{OUTPUT_DIR}/core"
MODELS_DIR = f"{OUTPUT_DIR}/models"
SERVICES_DIR = f"{OUTPUT_DIR}/services"

TAB = "  "


def X(tab=1):
    return TAB * tab


def generate_openapi(app: FastAPI):
    try:
        openapi_spec = app.openapi()

        spec = Specification(**openapi_spec)

        clear_output_dir()

        save_models(spec)
        # save_services(spec)
        save_routers(spec)

        save_index(spec)
    except Exception as e:
        # logger.info("------------------WTF-----------------")
        logger.error(type(e))
        logger.error(e)
        raise e


# ------------------------------------------------------------------------------------


def save_index(spec):
    filename = f"{OUTPUT_DIR}/index.ts"

    with open(filename, "w") as file:
        save_index_models(file, spec)


def save_index_models(file, spec: Specification):
    write_imports(file, spec)

    tags = group_by_tag(spec)

    for tag in tags:
        file.write(f"import {{ use{tag}Router }} from './services/{tag}Router'\n")

    file.write("\n\n")

    file.write("export function useApiRouter() {\n")

    for tag in tags:
        file.write(f"{X(1)}const {tag}Router = use{tag}Router()\n")

    file.write("\n")
    file.write(f"{X(1)}return {{\n")

    for tag in tags:
        file.write(f"{X(2)}{tag}Router,\n")

    file.write(f"{X(1)}}}\n")
    file.write("}")


def write_imports(file, spec: Specification):
    for key, schema in spec.components.schemas.items():
        if schema.enum:
            file.write(f"export {{ {schema.title} }} from './models/{schema.title}'\n")
        else:
            file.write(f"export type {{ {schema.title} }} from './models/{schema.title}'\n")

    file.write("\n")


# ------------------------------------------------------------------------------------
def clear_output_dir():
    # Delete folder

    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    if os.path.exists(MODELS_DIR):
        shutil.rmtree(MODELS_DIR)

    if os.path.exists(SERVICES_DIR):
        shutil.rmtree(SERVICES_DIR)

    if not os.path.exists(MODELS_DIR):
        os.mkdir(MODELS_DIR)

    if not os.path.exists(SERVICES_DIR):
        os.mkdir(SERVICES_DIR)
