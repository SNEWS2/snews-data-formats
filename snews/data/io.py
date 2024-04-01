# Standard library imports
import json
from pathlib import PosixPath


# .................................................................................................
def read_json_file(filepath: PosixPath) -> dict:
    """
    Read and parse a JSON file on disk

    Parameters
    ----------
    filepath : str
        Path to JSON file

    Returns
    -------
    data : dict
        Data from JSON file

    Examples
    --------
    >>> read_json_file("data.json")
    {"a": 1, "b": 2}
    """

    return json.loads(filepath.read_text(encoding="utf-8"))
