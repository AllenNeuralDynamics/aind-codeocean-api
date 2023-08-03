"""Tests credentials loader."""
import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, mock_open, patch, Mock
from botocore.exceptions import ClientError

from aind_codeocean_api.credentials import CodeOceanCredentials, get_secret

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
    @patch("aind_codeocean_api.credentials.get_secret")
    def test_from_aws(self, mock_get_secret: MagicMock):
        """Tests pulling credentials from aws secrets manager."""

        mock_get_secret.return_value = self.EXAMPLE_AWS_SECRETS
        creds_from_aws = CodeOceanCredentials(aws_secrets_name="mocked_secret")
        creds_from_aws2 = CodeOceanCredentials(
            aws_secrets_name="mocked_secret", domain="a_url", token="tkn"
        )
        self.assertEqual("http://acmecorp-aws.com", creds_from_aws.domain)
        self.assertEqual("123-abc-a", creds_from_aws.token.get_secret_value())
        self.assertEqual("http://acmecorp-aws.com", creds_from_aws2.domain)
        self.assertEqual("123-abc-a", creds_from_aws2.token.get_secret_value())

    @patch.dict(os.environ, EXAMPLE_ENV_VARS, clear=True)
    @patch("aind_codeocean_api.credentials.get_secret")
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
        # Assert the domain set in the file overrides the domain set in init
        self.assertEqual("http://acmecorp-cfg.com", creds_from_file.domain)
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
            "ValidationError(model='CodeOceanCredentials', "
            "errors=["
            "{'loc': ('domain',), 'msg': 'field required', 'type':"
            " 'value_error.missing'}, "
            "{'loc': ('token',), 'msg': 'field required', 'type':"
            " 'value_error.missing'}])"
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
        default_path = creds_from_file.default_config_file_path()
        mock_file.assert_called_once_with(default_path, "r")

    @patch("builtins.open", new_callable=mock_open)
    def test_save_to_file(self, mock_file: MagicMock):
        """Test save to file method."""
        creds = CodeOceanCredentials(domain="domain", token="token")
        creds2 = CodeOceanCredentials(domain="domain", token="token")
        creds2.config_file = Path("some_path")
        default_path = creds.default_config_file_path()
        creds.save_credentials_to_file()
        creds.save_credentials_to_file(output_path=Path("a_path"))
        creds2.save_credentials_to_file()

        mock_file.assert_has_calls(
            [
                call(default_path, "w+"),
                call(Path("a_path"), "w+"),
                call(Path("some_path"), "w+"),
            ],
            any_order=True,
        )

    @patch("boto3.client")
    def test_get_secret_success(self, mock_boto3_client):
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
        secret_value = get_secret(secret_name)

        # Assert that the client was called with the correct arguments
        mock_boto3_client.assert_called_with("secretsmanager")
        mock_client.get_secret_value.assert_called_with(
            SecretId=secret_name)

        # Assert that the secret value returned matches the expected value
        expected_value = {
            "username": "admin",
            "password": "secret_password",
            "host": "some host",
            "database": "some database",
        }
        self.assertEqual(secret_value, expected_value)

    @patch("boto3.client")
    def test_get_secret_permission_denied(self, mock_boto3_client):
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
            get_secret("my_secret")


if __name__ == "__main__":
    unittest.main()
