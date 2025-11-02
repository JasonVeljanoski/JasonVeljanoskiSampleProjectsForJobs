import re

from .openapi_types import Parameter, Path, Schema, Schema2, Specification
from .utils import MODELS_DIR, OUTPUT_DIR, TAB, X


def save_models(spec: Specification):
    for schema in spec.components.schemas.values():
        if schema.enum:
            save_enum(schema)
        else:
            save_model(schema)


# ------------------------------------------------------------------------


def save_model(schema: Schema2):
    with open(f"{MODELS_DIR}/{schema.title}.ts", "w") as f:
        write_imports(f, schema)

        f.write(f"export type {schema.title} = {{\n")

        write_fields(f, schema)

        f.write("}\n")


def write_imports(f, schema: Schema2):
    imports = schema.dependencies
    for temp in imports:
        f.write(f"import {{ {temp} }} from './{temp}'\n")

    if imports:
        f.write("\n")


def write_fields(f, schema: Schema2):
    for name, prop in schema.properties.items():
        type_str = prop.type_str

        nullable = schema.is_field_nullable(name)

        f.write(f"{X(1)}{name}{'?'*nullable}: {type_str}\n")


# ------------------------------------------------------------------------


def save_enum(schema: Schema2):
    name = schema.title

    with open(f"{MODELS_DIR}/{name}.ts", "w") as f:
        f.write(f"export enum {name} {{\n")

        for enum in schema.enum:
            left = convert_enum_to_key(enum)
            right = enum

            f.write(f"{X(1)}{left} = '{right}',\n")

        f.write("}\n")


def convert_enum_to_key(enum: str):
    return re.sub(
        r"\W+",
        "_",
        re.sub(r"^(\d+)", r"_\1", re.sub(r"([a-z])([A-Z]+)", r"\1_\2", str(enum))),
    ).upper()
