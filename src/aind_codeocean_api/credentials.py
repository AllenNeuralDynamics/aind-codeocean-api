"""Basic CodeOcean Credentials Handling."""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import boto3
from pydantic import BaseSettings, Field, SecretStr, validator
from pydantic.env_settings import (
    EnvSettingsSource,
    InitSettingsSource,
    SecretsSettingsSource,
)


# Small helper function to get an aws secret
def get_secret(secret_name: str) -> dict:
    """
    Retrieves a secret from AWS Secrets Manager.

    param secret_name: The name of the secret to retrieve.
    """
    # Create a Secrets Manager client
    client = boto3.client("secretsmanager")
    try:
        response = client.get_secret_value(SecretId=secret_name)
    finally:
        client.close()
    return json.loads(response["SecretString"])


class CodeOceanCredentials(BaseSettings):
    """Class to define credentials needed for CodeOcean. Has an api to set
    credentials through a class constructor, environment variables, a config
    file, or to pull them from aws secrets manager."""

    aws_secrets_name: Optional[str] = Field(
        default=None,
        repr=False,
        description="Optionally pull credentials from aws secrets manager.",
    )
    config_file: Optional[Path] = Field(
        default=None,
        repr=False,
        description="Optionally pull credentials from local config file.",
    )
    domain: str = Field(
        ...,
        title="Code Ocean Domain",
        description=(
            "Domain for Code Ocean platform "
            "(e.g., https://acmecorp.codeocean.com)"
        ),
        env_prefix="codeocean_",
    )
    token: SecretStr = Field(
        ...,
        title="Code Ocean API Token",
        description="API token for Code Ocean platform",
        env_prefix="codeocean_",
    )

    @classmethod
    def default_config_file_path(cls):
        """Return the default config file path."""
        return cls.Config.secrets_dir

    @validator("domain", pre=True)
    def _strip_trailing_slash(cls, input_domain):
        """Strips trailing slash from domain."""
        return input_domain.strip("/")

    class Config:
        """This class will add custom sourcing from aws."""

        # Prefix to append to env vars
        env_prefix = "CODEOCEAN_"

        # Default location of the config file
        secrets_dir = (
            Path(os.path.expanduser("~")) / ".codeocean" / "credentials.json"
        )

        @staticmethod
        def settings_from_config_file(config_file: Optional[Path]):
            """
            Curried function that returns a function to retrieve creds from
            a file.
            Parameters
            ----------
            config_file : Optional[Path]
              Location of json file to retrieve the creds from.

            Returns
            -------
            A function that retrieves the credentials.

            """

            def set_settings(_: BaseSettings) -> Dict[str, Any]:
                """
                A simple settings source that loads from a file
                """
                if config_file is None or not os.path.isfile(config_file):
                    return {}
                else:
                    with open(config_file, "r") as f:
                        contents = json.load(f)
                    return contents

            return set_settings

        @staticmethod
        def settings_from_aws(secrets_name: Optional[str]):
            """
            Curried function that returns a function to retrieve creds from aws
            Parameters
            ----------
            secrets_name : Optional[str]
              Name of the credentials we wish to retrieve
            Returns
            -------
            A function that retrieves the credentials.
            """

            def set_settings(_: BaseSettings) -> Dict[str, Any]:
                """
                A simple settings source that loads from aws secrets manager
                """
                credentials_from_aws = get_secret(secrets_name)
                return credentials_from_aws

            return set_settings

        @classmethod
        def customise_sources(
            cls,
            init_settings: InitSettingsSource,
            env_settings: EnvSettingsSource,
            file_secret_settings: SecretsSettingsSource,
        ):
            """Class method to return custom sources."""

            # Check if aws_secrets_name is defined during instantiation
            aws_secrets_name = init_settings.init_kwargs.get(
                "aws_secrets_name"
            )
            # Check if config_file is defined during instantiation
            config_file = init_settings.init_kwargs.get("config_file")
            domain = init_settings.init_kwargs.get("domain")
            token = init_settings.init_kwargs.get("token")
            env_domain = os.getenv((cls.env_prefix + "domain").upper())
            env_token = os.getenv((cls.env_prefix + "token").upper())

            # If user inputs aws_secrets_name, ignore all other settings
            if aws_secrets_name:
                return (
                    init_settings,
                    cls.settings_from_aws(secrets_name=aws_secrets_name),
                )
            # If a user defines a config_file, ignore non-init settings
            elif config_file is not None:
                return (
                    init_settings,
                    cls.settings_from_config_file(config_file),
                )
            # If a user attempts to construct object using init args and env
            # vars, ignore looking for a default config file
            elif (domain or env_domain) and (token or env_token):
                return (
                    init_settings,
                    env_settings,
                )
            # Otherwise, attempt to pull creds from default creds file location
            else:
                return (
                    cls.settings_from_config_file(
                        file_secret_settings.secrets_dir
                    ),
                )

    def save_credentials_to_file(self, output_path: Optional[Path] = None):
        """Saves domain and token to the file defined in config_file field or
        the default_config_file_path if config_file is None."""

        # Use default path if config_file is None
        if output_path is not None:
            out_path = output_path
        elif self.config_file is not None:
            out_path = self.config_file
        else:
            out_path = self.default_config_file_path()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w+") as output:
            json.dump(
                {
                    "domain": self.domain,
                    "token": self.token.get_secret_value(),
                },
                output,
                indent=4,
            )


def create_config_file():
    """Main method to create a config file from user inputs"""
    # Prompt user
    user_input_file_path = (
        input(
            f"Save to (Leave blank to save to default location"
            f" {CodeOceanCredentials.default_config_file_path()}): "
        )
        or None
    )
    domain = input("Domain (e.g. https://acmecorp.codeocean.com): ")
    token = input("API Token: ")
    CodeOceanCredentials(
        domain=domain, token=token, config_file=user_input_file_path
    ).save_credentials_to_file()


if __name__ == "__main__":
    create_config_file()
