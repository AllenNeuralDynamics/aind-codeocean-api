"""Basic CodeOcean Credentials Handling."""
import functools
import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Type, Union

import boto3
from pydantic import Field, SecretStr, field_validator
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    InitSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class JsonConfigSettingsSource(PydanticBaseSettingsSource, ABC):
    """Abstract base class for settings that parse json"""

    def __init__(self, settings_cls, config_file_location):
        """
        Class constructor for generic settings source that parses json
        Parameters
        ----------
        settings_cls
          Required for parent init
        config_file_location
          Location of json contents to parse
        """
        self.config_file_location = config_file_location
        super().__init__(settings_cls)

    @abstractmethod
    def _retrieve_contents(self) -> Dict[str, Any]:
        """Retrieve contents from config_file_location"""

    @functools.cached_property
    def _json_contents(self):
        """Cache contents to a property to avoid re-downloading."""
        contents = self._retrieve_contents()
        return contents

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> Tuple[Any, str, bool]:
        """
        Gets the value, the key for model creation, and a flag to determine
        whether value is complex.
        Parameters
        ----------
        field : FieldInfo
          The field
        field_name : str
          The field name

        Returns
        -------
        Tuple[Any, str, bool]
          A tuple contains the key, value and a flag to determine whether
          value is complex.

        """
        file_content_json = self._json_contents
        field_value = file_content_json.get(field_name)
        return field_value, field_name, False

    def prepare_field_value(
        self,
        field_name: str,
        field: FieldInfo,
        value: Any,
        value_is_complex: bool,
    ) -> Any:
        """
        Prepares the value of a field.
        Parameters
        ----------
        field_name : str
          The field name
        field : FieldInfo
          The field
        value : Any
          The value of the field that has to be prepared
        value_is_complex : bool
          A flag to determine whether value is complex

        Returns
        -------
        Any
          The prepared value

        """
        return value

    def __call__(self) -> Dict[str, Any]:
        """
        Run this when this class is called. Required to be implemented.

        Returns
        -------
        Dict[str, Any]
          The fields for the settings defined as a dict object.

        """
        d: Dict[str, Any] = {}

        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(
                field, field_name
            )
            field_value = self.prepare_field_value(
                field_name, field, field_value, value_is_complex
            )
            if field_value is not None:
                d[field_key] = field_value

        return d


class ConfigFileSettingsSource(JsonConfigSettingsSource):
    """Class that parses from a local json file."""

    def _retrieve_contents(self) -> Dict[str, Any]:
        """Retrieve contents from config_file_location"""
        with open(self.config_file_location, "r") as f:
            contents = json.load(f)
        return contents


class AWSConfigSettingsSource(JsonConfigSettingsSource):
    """Class that parses from aws secrets manager."""

    @staticmethod
    def _get_secret(secret_name: str) -> Dict[str, Any]:
        """
        Retrieves a secret from AWS Secrets Manager.

        Parameters
        ----------
        secret_name : str
          Secret name as stored in Secrets Manager

        Returns
        -------
        Dict[str, Any]
          Contents of the secret

        """
        # Create a Secrets Manager client
        client = boto3.client("secretsmanager")
        try:
            response = client.get_secret_value(SecretId=secret_name)
        finally:
            client.close()
        return json.loads(response["SecretString"])

    def _retrieve_contents(self) -> Dict[str, Any]:
        """Retrieve contents from config_file_location"""
        credentials_from_aws = self._get_secret(self.config_file_location)
        return credentials_from_aws


class CodeOceanCredentials(BaseSettings):
    """Class to define credentials needed for CodeOcean. Has an api to set
    credentials through a class constructor, environment variables, a config
    file, or to pull them from aws secrets manager."""

    model_config = SettingsConfigDict(env_prefix="CODEOCEAN_")

    aws_secrets_name: Optional[str] = Field(
        default=None,
        repr=False,
        description="Optionally pull credentials from aws secrets manager.",
    )
    config_file: Optional[Path] = Field(
        default_factory=lambda: Path(os.path.expanduser("~"))
        / ".codeocean"
        / "credentials.json",
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

    @field_validator("domain")
    def _strip_trailing_slash(cls, v):
        """Strips the trailing slash from the domain. For example, if the user
        inputs: https://acmecorp.codeocean.com/, then it will be changed to:
        https://acmecorp.codeocean.com"""
        return v.strip("/")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: InitSettingsSource,
        env_settings: EnvSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """
        Method to pull configs from a variety sources, such as a file or aws.
        Arguments are required and set by pydantic.
        Parameters
        ----------
        settings_cls : Type[BaseSettings]
          Top level class. Model fields can be pulled from this.
        init_settings : InitSettingsSource
          The settings in the init arguments.
        env_settings : EnvSettingsSource
          The settings pulled from environment variables.
        dotenv_settings : PydanticBaseSettingsSource
          Settings from .env files. Currently not supported.
        file_secret_settings : PydanticBaseSettingsSource
          Settings from secret files such as used in Docker. Currently not
          supported.

        Returns
        -------
        Tuple[PydanticBaseSettingsSource, ...]

        """
        init_file_path = init_settings.init_kwargs.get("config_file")
        default_file_path = settings_cls.model_fields[
            "config_file"
        ].default_factory()
        aws_secrets_path = init_settings.init_kwargs.get("aws_secrets_name")
        default_file_exists = os.path.isfile(default_file_path)

        # If user defines aws secrets, create creds from there
        if aws_secrets_path is not None:
            return (
                init_settings,
                AWSConfigSettingsSource(settings_cls, aws_secrets_path),
            )
        # else, if user defines config file path, create creds from there
        elif init_file_path is not None:
            # raise an exception if config file does not exist
            if os.path.isfile(init_file_path) is False:
                raise FileNotFoundError(
                    f"{init_file_path} is defined, but file not found."
                )
            return (
                init_settings,
                ConfigFileSettingsSource(settings_cls, init_file_path),
            )
        # If default file exists, create creds from init, env, and then there
        elif default_file_exists:
            return (
                init_settings,
                env_settings,
                ConfigFileSettingsSource(settings_cls, default_file_path),
            )
        # Otherwise, create creds from init and env
        else:
            return (
                init_settings,
                env_settings,
            )

    def save_credentials_to_file(self, output_path: Union[Path, str]) -> None:
        """
        Saves domain and token to a file.
        Parameters
        ----------
        output_path : Union[Path, str]
          Location to write to

        Returns
        -------
        None
          Save contents to a file

        """

        if isinstance(output_path, str):
            out_path = Path(output_path)
        else:
            out_path = output_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w+") as output_file:
            json.dump(
                {
                    "domain": self.domain,
                    "token": self.token.get_secret_value(),
                },
                output_file,
                indent=4,
            )


def create_config_file():
    """Main method to create a config file from user inputs"""
    default_file_path = CodeOceanCredentials.model_fields[
        "config_file"
    ].default_factory()
    # Prompt user
    user_input_file_path = (
        input(
            f"Save to (Leave blank to save to default location"
            f" {default_file_path}): "
        )
        or default_file_path
    )
    domain = input("Domain (e.g. https://acmecorp.codeocean.com): ")
    token = input("API Token: ")
    CodeOceanCredentials(domain=domain, token=token).save_credentials_to_file(
        user_input_file_path
    )


if __name__ == "__main__":
    create_config_file()
