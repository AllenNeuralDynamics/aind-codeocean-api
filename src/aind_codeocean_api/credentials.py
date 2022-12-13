"""Basic CodeOcean Credentials Handling."""
import json
import os
from pathlib import Path
from typing import Optional

CREDENTIALS_FILENAME = "credentials.json"
CREDENTIALS_DIR = ".codeocean"

if os.environ.get("CODEOCEAN_CREDENTIALS_PATH"):
    CREDENTIALS_FILEPATH = os.environ.get("CODEOCEAN_CREDENTIALS_PATH")
else:
    CREDENTIALS_FILEPATH = Path.home() / CREDENTIALS_DIR


class CodeOceanCredentials:
    """Class to hold CodeOcean Credentials"""

    @staticmethod
    def _load_json(path: str) -> json:
        """
        Loads credentials from a path
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

        self.credentials = self._load_json(CREDENTIALS_FILEPATH)

    @staticmethod
    def create_credentials(
        api_domain: str,
        access_token: str,
        file_location: Optional[str] = None,
    ):
        """
        Takes in credential information from
        user input and create a credentials.json file.

        Parameters
        ---------------
        api_domain : string
            API domain
        access_token : string
            API Access Token
        file_location : Optional[str]
            File path where credentials.json file is written to

        Returns
        ---------------
        credentials.json
        """
        if not os.path.exists(file_location):
            file_location = os.path.join(Path.home(), file_location)
            os.makedirs(file_location, exist_ok=True)

        if not file_location:
            file_location = CREDENTIALS_FILEPATH

        with open(
            os.path.join(file_location, CREDENTIALS_FILENAME), "w"
        ) as output:
            json.dump(
                {"domain": api_domain, "token": access_token}, output, indent=4
            )


def main():
    """Prompts user and calls create credentials method"""

    file_path = input(
        """Enter a file path to which your credentials
        will be saved. This defaults to `$HOME/.codeocean`:"""
    )
    domain = input("Enter your domain: ")
    token = input("Enter your API Access Token: ")

    CodeOceanCredentials.create_credentials(
        api_domain=domain, access_token=token, file_location=file_path
    )


if __name__ == "__main__":
    main()
