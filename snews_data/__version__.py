# -*- coding: utf-8 -*-

# Standard library modules
from pathlib import Path

# Third-party imports
from single_version import get_version

__version__ = get_version("snews_data_services", Path(__file__).parent.parent)
schema_version = "0.1a"
