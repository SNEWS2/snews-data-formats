# -*- coding: utf-8 -*-

# Third-party modules
from pydantic.json_schema import GenerateJsonSchema

# Local modules
from ..__version__ import schema_version


# .................................................................................................
class SNEWSJsonSchema(GenerateJsonSchema):
    def generate(self, schema, mode='serialization'):
        json_schema = {
            "$schema": self.schema_dialect,
            "schema_author": "Supernova Early Warning System (SNEWS)",
            "schema_version": schema_version
        }
        json_schema.update(super().generate(schema, mode=mode))

        return json_schema
