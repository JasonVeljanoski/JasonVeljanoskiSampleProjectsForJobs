from dataclasses import dataclass

from .openapi_types import Parameter, Path, Schema, Schema2, Specification
from .utils import MODELS_DIR, OUTPUT_DIR, SERVICES_DIR, TAB, X


@dataclass
class PathWrap:
    path: Path
    method: str
    url: str


def save_services(spec: Specification):
    tag_groups = group_by_tag(spec)

    for tag, paths in tag_groups.items():
        save_tag(tag, paths, spec)


def group_by_tag(spec: Specification) -> dict[str, list[PathWrap]]:
    groups = {}

    for url, path in spec.paths.items():
        for method, route in path.items():
            for tag in route.better_tags:
                tag = tag.replace(" ", "")
                tag = tag.replace("-", "")

                if tag not in groups:
                    groups[tag] = []

                groups[tag].append(PathWrap(path=route, method=method, url=url))

    return groups


def save_tag(tag: str, items: list[PathWrap], spec):
    with open(f"{SERVICES_DIR}/{tag}Service.ts", "w") as f:
        write_imports(f, items)

        f.write(f"export class {tag}Service {{\n")

        write_routes(f, items, spec)

        f.write("}\n")


def write_imports(f, items: list[PathWrap]):
    f.write("import { makeRequest, formatDates } from '../core/requests'\n\n")

    dependencies = set()

    for item in items:
        path_depends = item.path.dependencies

        dependencies.update(path_depends)

    for temp in dependencies:
        f.write(f"import {{ {temp} }} from '../models/{temp}'\n")

    if dependencies:
        f.write("\n")


def write_routes(f, items: list[PathWrap], spec):
    for item in items:
        write_route(f, item, spec)
        f.write("\n")


def write_route(f, item: PathWrap, spec):
    method = item.method
    path = item.path
    url = item.url

    f.write(f"{X(1)}public static {path.operation_id}(\n")

    write_args(f, path)

    f.write(f"{X(1)}) {{\n")
    # f.write(f"{X(1)}): Promise<{path.response_type}>{{\n")

    write_function_body(f, method, url, path, spec)

    f.write(f"{X(1)}}}\n")


def write_args(f, path: Path):
    url_params = path.query_parameters + path.path_parameters

    if url_params:
        f.write(f"{X(2)}{{\n")

        for param in url_params:
            f.write(f"{X(3)}{param.name},\n")

        f.write(f"{X(2)}}}: {{\n")

        for param in url_params:
            t = "" if param.required else "?"

            f.write(f"{X(3)}{param.name}{t}: {param.schema_.type_str}\n")

        f.write(f"{X(2)}}},\n")

    body = path.content_body

    if body:
        f.write(f"{X(2)}body: {body.type_str},\n")


def write_function_body(f, method, url, path: Path, spec):
    path_params = path.path_parameters
    query_params = path.query_parameters
    body = path.content_body

    f.write(f"{X(2)}return makeRequest<{path.response_type}>({{\n")

    f.write(f"{X(3)}method: '{method.upper()}',\n")

    f.write(f"{X(3)}url: '/api{url}',\n")

    if path_params:
        f.write(f"{X(3)}path: {{\n")

        for param in path_params:
            f.write(f"{X(4)}{param.name},\n")

        f.write(f"{X(3)}}},\n")

    if query_params:
        f.write(f"{X(3)}query: {{\n")

        for param in query_params:
            f.write(f"{X(4)}{param.name},\n")

        f.write(f"{X(3)}}},\n")

    if body:
        f.write(f"{X(3)}body,\n")

    # f.write(f"{X(3)}aborter_key,\n")

    f.write(f"{X(2)}}})\n")


# def write_function_body(f, method, url, path: Path, spec):
#     path_params = path.path_parameters
#     query_params = path.query_parameters
#     body = path.content_body

#     f.write(f"{X(2)}return makeRequest<{path.response_type}>({{\n")

#     f.write(f"{X(3)}method: '{method.upper()}',\n")

#     f.write(f"{X(3)}url: '{url}',\n")

#     if path_params:
#         f.write(f"{X(3)}path: {{\n")

#         for param in path_params:
#             f.write(f"{X(4)}{param.name},\n")

#         f.write(f"{X(3)}}},\n")

#     if query_params:
#         f.write(f"{X(3)}query: {{\n")

#         for param in query_params:
#             f.write(f"{X(4)}{param.name},\n")

#         f.write(f"{X(3)}}},\n")

#     if body:
#         f.write(f"{X(3)}body,\n")

#     f.write(f"{X(3)}aborter_key,\n")

#     f.write(f"{X(2)}}})")

#     # Find all fields recursively that are of type Date

#     auto_dates(f, path, spec)

#     f.write("\n")


# def auto_dates(f, path: Path, spec: Specification):
#     response = path.responses["200"]
#     if not response.content:
#         return

#     content = response.content["application/json"]

#     if not content.schema_:
#         return

#     schema = content.schema_

#     possible = set()

#     for x in schema.multi_ref:
#         if x.ref:
#             possible.add(x.ref)

#     if schema.ref:
#         possible.add(schema.ref)

#     if schema.items and schema.items.ref:
#         possible.add(schema.items.ref)

#     if not possible:
#         return

#     date_string_paths = []

#     def recursive_stuff(schema_name, path=""):
#         schema = spec.get_schema(schema_name)

#         for name, prop in schema.properties.items():
#             if prop.type_str == "Date":
#                 date_string_paths.append(f"{path}.{name}")

#             if prop.ref:
#                 recursive_stuff(prop.ref, f"{path}.{name}")

#             if prop.items:
#                 if prop.items.ref:
#                     recursive_stuff(prop.items.ref, f"{path}.{name}[]")

#     for x in possible:
#         recursive_stuff(x, "")

#     if not date_string_paths:
#         return

#     print(date_string_paths)

#     f.write(".then((res) => formatDates(res, [\n")
#     for x in date_string_paths:
#         f.write(f"{X(4)}'{x}',\n")

#     f.write(f"{X(3)}]))")
