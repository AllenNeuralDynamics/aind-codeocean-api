"""Basic CodeOcean Credentials Handling."""
import json
import os


class CodeOceanCredentials:
    """Class to hold CodeOcean Credentials"""

    @staticmethod
    def _load_json(path: str) -> json:
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
        """Initializes credentials."""
        self.credentials_path = os.environ.get(
            "CODEOCEAN_CREDENTIALS_PATH", "credentials.json"
        )
        self.credentials = self._load_json(self.credentials_path)

    def create_credentials():
        file_location = input("Location: ")
        domain = input("Domain: ")
        access_token = input("API Access Token: ")

        if not file_location:
            file_location = "{$HOME}/.codeocean/"
        
        with open(os.path.join(file_location, "credentials.json"), "w") as as output:
            json.dump({ "domain": domain, "token": access_token}, output)
