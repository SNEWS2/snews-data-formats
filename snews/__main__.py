# -*- coding: utf-8 -*-

# Standard modules
import json
import logging
from pathlib import Path

from pydantic import BaseModel

# Local modules
from snews import models
from snews.schema import SNEWSJsonSchema


# .................................................................................................
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    return


# .................................................................................................
def generate_model_schemas(outdir: str = None, models_module: list = models, dry_run: bool = False):
    """Generate JSON schemas for all models in the package and write them to file"""

    outdir = Path(__file__).parent / "schema" if outdir is None else Path(outdir).resolve()

    for model_class_name in models.__all__:
        model_class = getattr(models, model_class_name)
        for model_name in model_class.__all__:
            model = getattr(model_class, model_name)

            if not issubclass(model, BaseModel):
                continue

            schema = model.model_json_schema(schema_generator=SNEWSJsonSchema)
            filename = f"{model.__name__}.schema.json"
            schema_path = outdir / filename if not dry_run else Path("/tmp") / filename

            with open(schema_path, "w") as f:
                f.write(json.dumps(schema, indent=2))
                logging.info(f"Wrote schema for {model.__name__} to file {schema_path}")

    return


# .................................................................................................
def main() -> None:
    setup_logging()
    generate_model_schemas()

    return


# .................................................................................................
if __name__ == '__main__':
    main()
