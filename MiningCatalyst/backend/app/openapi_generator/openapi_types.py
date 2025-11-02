import re
from typing import Any

from pydantic import BaseModel, Field, validator


class Base(BaseModel):
    pass
    # class Config:
    #     extra = "forbid"


def ensure_camel(value: str) -> str:
    if value is None:
        return None
    return re.sub(r"(?<!^)_([a-zA-Z])", lambda m: m.group(1).upper(), value)


class Info(Base):
    title: str = None
    description: str = None
    version: str = None


class Server(Base):
    url: str = None
    description: str = None


class Schema(Base):
    title: str = None
    type: str = None
    required: bool = None
    ref: str | None = Field(alias="$ref")

    items: "Schema" = None
    properties: dict[str, "Schema"] = Field(default_factory=dict)

    enum: list[str] = None
    description: str = None

    allOf: list["Schema"] = Field(default_factory=list)
    oneOf: list["Schema"] = Field(default_factory=list)
    anyOf: list["Schema"] = Field(default_factory=list)

    example: Any = None
    default: Any = None
    format: str = None

    additional_properties: "Schema" = Field(default_factory=dict, alias="additionalProperties")

    maximum: float = None
    minimum: float = None

    # Strip ref on assignment
    @validator("ref", pre=True)
    def strip_ref(cls, v):
        if v is not None:
            return v.replace("#/components/schemas/", "")

        return v

    @property
    def multi_ref(self):
        return self.allOf + self.oneOf + self.anyOf

    @property
    def type_str(self):
        if self.ref is not None:
            return self.ref
        elif self.title == "File":
            return "Blob"
        elif self.multi_ref:
            return " | ".join([s.type_str for s in self.multi_ref])
        elif self.type == "array":
            return f"Array<{self.items.type_str}>"
        elif self.type == "object":
            return "Record<string, any>"
        elif self.type == "integer":
            return "number"
        elif self.type == "number":
            return "number"
        elif self.type == "string":
            if self.format == "date-time":
                return "Date"
            elif self.format == "binary":
                return "Blob"
            else:
                return "string"
        elif self.type == "boolean":
            return "boolean"

        return "any"


class Schema2(Base):
    title: str = None
    type: str = None
    required: list[str] = Field(default_factory=list)

    properties: dict[str, "Schema"] = Field(default_factory=dict)

    enum: list[str] = None
    description: str = None

    @validator("title", pre=True)
    def camel_title(cls, v):
        return ensure_camel(v)

    @property
    def dependencies(self):
        depends = set()

        for prop in self.properties.values():
            if prop.ref is not None:
                depends.add(prop.ref)

            if prop.items is not None:
                if prop.items.ref is not None:
                    depends.add(prop.items.ref)

        # Exclude self
        depends.discard(self.title)

        return sorted(depends)

    def is_field_nullable(self, field_name):
        return field_name not in self.required


class Content(Base):
    schema_: Schema = Field(alias="schema")


class Parameter(Base):
    required: bool = None
    schema_: Schema = Field(alias="schema")
    name: str = None
    in_: str | None = Field(alias="in")

    @validator("name", pre=True)
    def array_name(cls, v):
        if v is not None:
            return v.replace("[]", "")

        return v


class Response(Base):
    description: str = None
    content: dict[str, Content] = None
    required: bool = None


class Path(Base):
    tags: list[str] = None
    summary: str = None
    operation_id: str = Field(alias="operationId")
    parameters: list[Parameter] = Field(default_factory=list)
    responses: dict[str, Response] = None
    security: list[dict[str, list[Any]]] = None
    requestBody: Response = None
    description: str = None

    @validator("operation_id", pre=True)
    def camel_operation_id(cls, v):
        return ensure_camel(v)

    @property
    def query_parameters(self):
        return [p for p in self.parameters if p.in_ == "query"]

    @property
    def path_parameters(self):
        return [p for p in self.parameters if p.in_ == "path"]

    @property
    def response_type(self):
        response = self.responses["200"]

        types = set()

        if response.content:
            for content in response.content.values():
                types.add(content.schema_.type_str)

        return " | ".join(types)

    @property
    def dependencies(self):
        needed_types = set()

        def add_import(item: Schema):
            if item.ref:
                needed_types.add(item.ref)

            if item.items:
                add_import(item.items)

            if item.properties:
                for prop in item.properties.values():
                    add_import(prop)

            for prop in item.multi_ref:
                add_import(prop)

        for param in self.parameters:
            add_import(param.schema_)

        for response in self.responses.values():
            if response.content:
                for content in response.content.values():
                    add_import(content.schema_)

        if self.requestBody:
            for content in self.requestBody.content.values():
                add_import(content.schema_)

        # Exclude self
        needed_types.discard(self.operation_id)
        needed_types.discard("HTTPValidationError")

        return sorted(needed_types)

    @property
    def content_body(self):
        if self.requestBody:
            return self.requestBody.content["application/json"].schema_

        return None

    @property
    def better_tags(self):
        first = self.tags[0]
        others = self.tags[1:]

        first = first.split(" - ")[0]

        return [first] + others


class Components(Base):
    schemas: dict[str, Schema2] = None
    securitySchemes: dict[str, dict] = None


class Specification(Base):
    openapi: str = None
    info: Info = None
    paths: dict[str, dict[str, Path]] = Field(default_factory=dict)
    servers: list[Server] = Field(default_factory=list)
    components: Components = None

    def get_schema(self, name):
        return self.components.schemas[name]
