"""Basic CodeOcean Credentials Handling."""
import json
import os
from pathlib import Path

CREDENTIALS_FILENAME = "credentials.json"
CREDENTIALS_DIR = ".codeocean"
DEFAULT_ENV_VAR = "CODEOCEAN_CREDENTIALS_PATH"
DEFAULT_HOME_PATH = Path.home() / CREDENTIALS_DIR / CREDENTIALS_FILENAME


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

        if os.environ.get(DEFAULT_ENV_VAR):
            filepath = os.environ.get(DEFAULT_ENV_VAR)
        else:
            filepath = str(DEFAULT_HOME_PATH)

        self.credentials = self._load_json(filepath)

    @staticmethod
    def create_credentials(
        api_domain: str,
        access_token: str,
        file_location: str,
    ) -> None:
        """
        Takes in credential information from
        user input and create a credentials.json file.

        Parameters
        ---------------
        api_domain : string
            API domain
        access_token : string
            API Access Token
        file_location : str
            File path where credentials.json file is written to

        Returns
        ---------------
        None
            Writes to file
        """

        with open(file_location, "w+") as output:
            json.dump(
                {"domain": api_domain, "token": access_token}, output, indent=4
            )


if __name__ == "__main__":

    # Prompt user
    user_input_file_path = input(
        f"Save to (Leave blank to default to {DEFAULT_HOME_PATH}): "
    )
    domain = input("Domain (e.g. https://acmecorp.codeocean.com): ")
    token = input("Access Token: ")

    # Use default file path if none entered
    if user_input_file_path:
        file_path = user_input_file_path
    elif os.environ.get(DEFAULT_ENV_VAR):
        file_path = os.environ.get(DEFAULT_ENV_VAR)
    else:
        file_path = str(DEFAULT_HOME_PATH)

    Path(file_path).parent.mkdir(exist_ok=True, parents=True)

    CodeOceanCredentials.create_credentials(
        api_domain=domain, access_token=token, file_location=file_path
    )
