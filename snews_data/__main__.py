# -*- coding: utf-8 -*-

# Standard modules
import json
import logging
from pathlib import Path

# Local modules
from . import models
from .schema import SNEWSJsonSchema


# .................................................................................................
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    return


# .................................................................................................
def generate_model_schemas(out_dir: str = None, models: list = models.all()):
    """Generate JSON schemas for all models in the package and write them to file"""

    if out_dir is not None:
        out_dir = Path(out_dir).resolve()
    else:
        out_dir = f"{Path(__file__).parent}/schema"

    for model in models:
        schema = model.model_json_schema(schema_generator=SNEWSJsonSchema)
        schema_path = f"{out_dir}/{model.__name__}.schema.json"

        try:
            with open(schema_path, "w") as f:
                f.write(json.dumps(schema, indent=2))
                logging.info(f"Wrote schema for {model.__name__} to file {schema_path}")
        except Exception as e:
            logging.error(f"Failed to write schema for {model.__name__} to file: {e}")

    return


# .................................................................................................
def main():
    setup_logging()
    generate_model_schemas()

    return


# .................................................................................................
if __name__ == '__main__':
    main()
