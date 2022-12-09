"""Basic CodeOcean Credentials Handling."""
import json
import os
from pathlib import Path
from typing import Optional

CREDENTIALS_FILENAME = "credentials.json"

if os.environ.get("CODEOCEAN_CREDENTIALS_PATH"):
    CREDENTIALS_FILEPATH = os.environ.get("CODEOCEAN_CREDENTIALS_PATH")
else:
    CREDENTIALS_FILEPATH = Path.home() / CREDENTIALS_FILENAME


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
        This will take in credentials information from
        user input and create a credentials.json file.

        Parameters
        ---------------
        api_domain : string
            API domain
        access_token : string
            API Access Token
        file_locaiton: string
            File path where credentials.json file is written to

        Returns
        ---------------
        credentials.json
        """

        if not file_location:
            file_location = CREDENTIALS_FILEPATH

        # TO-DO: function to check url, indentation to json to format it
        if not os.path.isdir(file_location):
            os.mkdir(file_location)

        with open(
            os.path.join(file_location, "credentials.json"), "w"
        ) as output:
            json.dump({"domain": api_domain, "token": access_token}, output)


def main():
    """Prompts user and calls create credentials method"""
    file_path = input(
        "Enter a file path to which your credentials will be saved: "
    )
    domain = input("Enter your domain: ")
    token = input("Enter your API Access Token: ")

    CodeOceanCredentials.create_credentials(
        api_domain=domain, access_token=token, file_location=file_path
    )


if __name__ == "__main__":
    main()
