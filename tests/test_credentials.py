"""Tests credentials loader."""
import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, mock_open, patch

from botocore.exceptions import ClientError

from aind_codeocean_api.credentials import (
    AWSConfigSettingsSource,
    CodeOceanCredentials,
    create_config_file,
)

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
FAKE_CREDENTIALS_PATH = TEST_DIR / "resources" / "fake_credentials.json"
FAKE_PATH_USER_INPUT = TEST_DIR / "resources"


class TestCredentials(unittest.TestCase):
    """Tests credentials class methods."""

    EXAMPLE_ENV_VARS = {
        "CODEOCEAN_DOMAIN": "http://acmecorp-env.com",
        "CODEOCEAN_TOKEN": "123-abc-e",
    }
    EXAMPLE_AWS_SECRETS = {
        "domain": "http://acmecorp-aws.com",
        "token": "123-abc-a",
    }
    EXAMPLE_CONFIG_FILE = json.dumps(
        {
            "domain": "http://acmecorp-cfg.com",
            "token": "123-abc-c",
        }
    )

    def test_basic_init(self):
        """Tests that the credentials can be instantiated with class
        constructor."""
        creds = CodeOceanCredentials(
            domain="http://acmecorp.com/", token="123-abc"
        )

        # Trailing slashes should be stripped
        self.assertEqual("http://acmecorp.com", creds.domain)
        self.assertEqual("123-abc", creds.token.get_secret_value())

    @patch.dict(os.environ, EXAMPLE_ENV_VARS, clear=True)
    def test_env_vars(self):
        """Tests setting credentials from environment variables."""
        creds_from_env = CodeOceanCredentials()
        creds_combo_1 = CodeOceanCredentials(domain="http://acmecorp.com/")
        creds_combo_2 = CodeOceanCredentials(token="123-abc")
        creds_combo_3 = CodeOceanCredentials(
            domain="http://acmecorp.com/", token="123-abc"
        )

        self.assertEqual("http://acmecorp-env.com", creds_from_env.domain)
        self.assertEqual("123-abc-e", creds_from_env.token.get_secret_value())
        self.assertEqual("http://acmecorp.com", creds_combo_1.domain)
        self.assertEqual("123-abc-e", creds_combo_1.token.get_secret_value())
        self.assertEqual("http://acmecorp-env.com", creds_combo_2.domain)
        self.assertEqual("123-abc", creds_combo_2.token.get_secret_value())
        self.assertEqual("http://acmecorp.com", creds_combo_3.domain)
        self.assertEqual("123-abc", creds_combo_3.token.get_secret_value())

    @patch.dict(os.environ, EXAMPLE_ENV_VARS, clear=True)
    @patch(
        "aind_codeocean_api.credentials.AWSConfigSettingsSource._get_secret"
    )
    def test_from_aws(self, mock_get_secret: MagicMock):
        """Tests pulling credentials from aws secrets manager."""

        mock_get_secret.return_value = self.EXAMPLE_AWS_SECRETS
        creds_from_aws = CodeOceanCredentials(aws_secrets_name="mocked_secret")
        creds_from_aws2 = CodeOceanCredentials(
            aws_secrets_name="mocked_secret", domain="a_url", token="tkn"
        )
        self.assertEqual("http://acmecorp-aws.com", creds_from_aws.domain)
        self.assertEqual("123-abc-a", creds_from_aws.token.get_secret_value())
        self.assertEqual("a_url", creds_from_aws2.domain)
        self.assertEqual("tkn", creds_from_aws2.token.get_secret_value())

    @patch.dict(os.environ, EXAMPLE_ENV_VARS, clear=True)
    @patch(
        "aind_codeocean_api.credentials.AWSConfigSettingsSource._get_secret"
    )
    def test_from_aws_error(self, mock_get_secret: MagicMock):
        """Tests situation where an error is raised when attempting to set
        credentials through aws_secrets_name."""

        def mock_error(_):
            """Mock an error."""
            raise Exception("An error occurred connecting to aws.")

        mock_get_secret.side_effect = mock_error

        with self.assertRaises(Exception) as e:
            CodeOceanCredentials(
                aws_secrets_name="mocked_secret", domain="a_url", token="tkn"
            )
        self.assertEqual(
            "Exception('An error occurred connecting to aws.')",
            repr(e.exception),
        )

    @patch.dict(os.environ, EXAMPLE_ENV_VARS, clear=True)
    @patch(
        "builtins.open", new_callable=mock_open, read_data=EXAMPLE_CONFIG_FILE
    )
    @patch("os.path.isfile")
    def test_from_file(self, mock_is_file: MagicMock, mock_file: MagicMock):
        """Tests setting creds from file."""
        mock_is_file.return_value = True
        creds_from_file = CodeOceanCredentials(
            config_file="mocked_file", domain="some_url"
        )
        # Assert init is set
        self.assertEqual("some_url", creds_from_file.domain)
        self.assertEqual("123-abc-c", creds_from_file.token.get_secret_value())
        mock_file.assert_called_once_with("mocked_file", "r")

    @patch.dict(os.environ, EXAMPLE_ENV_VARS, clear=True)
    @patch(
        "builtins.open", new_callable=mock_open, read_data=EXAMPLE_CONFIG_FILE
    )
    @patch("os.path.isfile")
    def test_from_file_error(
        self, mock_is_file: MagicMock, mock_file: MagicMock
    ):
        """Tests case where an error is raised when attempting to access a
        file"""

        # Mock an issue where the file doesn't exist
        mock_is_file.return_value = False
        # Assert if config_file is in init args, and an error occurs, then
        # just raise an Exception instead of attempting to fallback
        with self.assertRaises(Exception) as e:
            CodeOceanCredentials(config_file="mocked_file", domain="some_url")

        err_message = (
            "FileNotFoundError('mocked_file is defined, but file not found.')"
        )
        self.assertEqual(err_message, repr(e.exception))

        mock_file.assert_not_called()

    @patch(
        "builtins.open", new_callable=mock_open, read_data=EXAMPLE_CONFIG_FILE
    )
    @patch("os.path.isfile")
    def test_fallback_to_default_file(
        self, mock_is_file: MagicMock, mock_file: MagicMock
    ):
        """Tests that final fallback is to search for the default file."""
        mock_is_file.return_value = True
        creds_from_file = CodeOceanCredentials()
        # Assert the domain set in the file overrides the domain set in init
        self.assertEqual("http://acmecorp-cfg.com", creds_from_file.domain)
        self.assertEqual("123-abc-c", creds_from_file.token.get_secret_value())
        default_path = creds_from_file.config_file
        mock_file.assert_called_once_with(default_path, "r")

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_save_to_file(self, mock_mkdir: MagicMock, mock_file: MagicMock):
        """Test save to file method."""
        creds = CodeOceanCredentials(domain="domain", token="token")
        creds2 = CodeOceanCredentials(domain="domain", token="token")
        creds2.config_file = TEST_DIR / "creds1.json"
        default_path = creds.config_file
        creds.save_credentials_to_file(creds.config_file)
        creds.save_credentials_to_file(output_path=(TEST_DIR / "creds2.json"))
        creds2.save_credentials_to_file(creds2.config_file)
        mock_mkdir.assert_has_calls(
            [
                call(parents=True, exist_ok=True),
                call(parents=True, exist_ok=True),
                call(parents=True, exist_ok=True),
            ]
        )

        mock_file.assert_has_calls(
            [
                call(default_path, "w+"),
                call((TEST_DIR / "creds1.json"), "w+"),
                call(TEST_DIR / "creds2.json", "w+"),
            ],
            any_order=True,
        )

    @patch("boto3.client")
    def test_get_secret_success(self, mock_boto3_client: MagicMock):
        """Tests that secret is retrieved as expected"""
        # Mock the Secrets Manager client and response
        mock_client = Mock()
        mock_boto3_client.return_value = mock_client
        mock_secret_string = (
            '{"username": "admin",'
            ' "password": "secret_password",'
            ' "host": "some host",'
            ' "database": "some database"}'
        )
        mock_response = {"SecretString": mock_secret_string}
        mock_client.get_secret_value.return_value = mock_response

        # Call the get_secret method with a mock secret name
        secret_name = "my_secret"
        secret_value = AWSConfigSettingsSource._get_secret(secret_name)

        # Assert that the client was called with the correct arguments
        mock_boto3_client.assert_called_with("secretsmanager")
        mock_client.get_secret_value.assert_called_with(SecretId=secret_name)

        # Assert that the secret value returned matches the expected value
        expected_value = {
            "username": "admin",
            "password": "secret_password",
            "host": "some host",
            "database": "some database",
        }
        self.assertEqual(secret_value, expected_value)

    @patch("boto3.client")
    def test_get_secret_permission_denied(self, mock_boto3_client: MagicMock):
        """Tests  secret retrieval fails with incorrect aws permissions"""
        mock_boto3_client.return_value.get_secret_value.side_effect = (
            ClientError(
                {
                    "Error": {
                        "Code": "AccessDeniedException",
                        "HTTPStatusCode": 403,
                    }
                },
                "get_secret_value",
            )
        )
        # Assert that ClientError is raised
        with self.assertRaises(ClientError):
            AWSConfigSettingsSource._get_secret("my_secret")


class TestConfigFileCreation(unittest.TestCase):
    """Tests configuration file creation"""

    @patch("builtins.input")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_with_config_file(
        self,
        mock_mkdir: MagicMock,
        mock_file: MagicMock,
        mock_input: MagicMock,
    ):
        """Tests that a user-defined config file path will be used"""

        mock_inputs = [
            "some_output_path/my_configs.json",
            "http://domain",
            "abc-123",
        ]
        mock_input.side_effect = mock_inputs
        create_config_file()
        mock_input.assert_called()
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file.assert_called_once_with(
            Path("some_output_path/my_configs.json"), "w+"
        )

    @patch("builtins.input")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_default_config_file(
        self,
        mock_mkdir: MagicMock,
        mock_file: MagicMock,
        mock_input: MagicMock,
    ):
        """Tests that a default config path will be used if input is blank"""

        mock_inputs = ["", "http://domain", "abc-123"]
        mock_input.side_effect = mock_inputs
        create_config_file()
        mock_input.assert_called()
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file.assert_called_once_with(
            CodeOceanCredentials.model_fields["config_file"].default_factory(),
            "w+",
        )


if __name__ == "__main__":
    unittest.main()
