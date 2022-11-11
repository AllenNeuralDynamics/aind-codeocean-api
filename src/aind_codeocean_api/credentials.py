"""Basic CodeOcean Credentials Handling."""
import json
import os


class CodeOceanCredentials:
    """Class to hold CodeOcean Credentials"""

    @staticmethod
    def _load_json(path):
        """
        Loads credentials from a pth
        Parameters
        ----------
        path : str

        Returns
        -------
        json
        """
        assert os.path.exists(path), f"credentials file {path} does not exist"
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)

    def __init__(self):
        self.credentials_path = os.environ.get(
            "CODEOCEAN_CREDENTIALS_PATH", "credentials.json"
        )
        self.credentials = self._load_json(self.credentials_path)
