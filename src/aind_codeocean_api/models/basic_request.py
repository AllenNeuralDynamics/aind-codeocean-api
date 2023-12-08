"""Module for common methods used by all subclasses"""

import json
from dataclasses import asdict, dataclass


@dataclass
class BasicRequest:
    """Class for basic request methods"""

    def __clean_nones(self, value):
        """
        Recursively remove all None values from dictionaries and lists, and
        returns the result as a new dictionary or list. Modified from
        https://stackoverflow.com/a/60124334
        """
        if isinstance(value, list):
            return [self.__clean_nones(x) for x in value if x is not None]
        elif isinstance(value, dict):
            return {
                key: self.__clean_nones(val)
                for key, val in value.items()
                if val is not None
            }
        else:
            return value

    @property
    def json_string(self) -> str:
        """Render dataclass as json object with null values removed."""
        return json.dumps(self.__clean_nones(asdict(self)))
