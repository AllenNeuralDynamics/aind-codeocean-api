"""Test credentials in AWS"""
import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock
from unittest.mock import patch

import boto3
import botocore
from aws_secretsmanager_caching import SecretCache
from moto import mock_secretsmanager, mock_sts

from aind_codeocean_api import credentials_in_aws
from aind_codeocean_api.credentials import CodeOceanCredentials

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
FAKE_CREDENTIALS_PATH = TEST_DIR / "resources" / "fake_credentials.json"
FAKE_PATH_USER_INPUT = TEST_DIR / "resources"
AWS_ROLE_ARN = "arn:aws:iam::467914378000:role/codeocean-secret-retriever"
DOMAIN = "https://acmecorp.codeocean.com"
TOKEN = "fake_token"
SECRET_NAME = "codeocean-service-account"
CREDENTIALS_FILENAME = "credentials.json"
CREDENTIALS_DIR = ".codeocean"
DEFAULT_ENV_VAR = "CODEOCEAN_CREDENTIALS_PATH"
DEFAULT_HOME_PATH = Path.home() / CREDENTIALS_DIR / CREDENTIALS_FILENAME


class MockSecretCache:
    """Mock of the boto3 secrets cache client."""
    def get_secret_string(*args, **kwargs):
        return json.dumps({"domain": "https://acmecorp.codeocean.com", "token": "fake_token"})


class TestCredentialsInAWS(unittest.TestCase):
    """Tests credentials in AWS methods."""
    @mock_secretsmanager
    @mock_sts
    def test__get_secret(self):
        """Tests _get_secret method."""
        # Mock _get_secrets_cache_client() method to return the fake secrets cache client
        with patch.object(credentials_in_aws, "_get_secrets_cache_client") as mock_get_secrets_cache_client:
            mock_get_secrets_cache_client.return_value = MockSecretCache()
            secret = credentials_in_aws._get_secret(secret_name=SECRET_NAME)
        
        self.assertEqual(secret, json.dumps({"domain": DOMAIN, "token": TOKEN}))

    @patch("json.dump")
    @patch("builtins.open", new_callable=unittest.mock.mock_open())
    def test_create_credentials_from_aws(self, m, m_json):
        """Tests that credentials are loaded from AWS."""
        # Create a mock for the _get_secret method that returns the fake credentials from a mocked secretsmanager
        with patch.object(credentials_in_aws, "_get_secret") as mock_get_secret:
            mock_get_secret.return_value = json.dumps({"domain": DOMAIN, "token": TOKEN})
            credentials_in_aws.create_credentials_from_aws_secrets_manager(
                secret_name=SECRET_NAME,
                file_location="mock_file.json"
            )

        m.assert_called_once_with("mock_file.json", "w+")
        m_json.assert_called_with(
            {"domain": DOMAIN, "token": TOKEN},
            m.return_value.__enter__.return_value,
            indent=4,
        )

    @patch("json.dump")
    @patch("builtins.open", new_callable=unittest.mock.mock_open())
    def test_create_credentials_from_aws_no_inputs(self, m, m_json):
        """Tests that credentials are loaded from AWS."""
        # Create a mock for the _get_secret method that returns the fake credentials from a mocked secretsmanager
        with patch.object(credentials_in_aws, "_get_secret") as mock_get_secret:
            mock_get_secret.return_value = json.dumps({"domain": DOMAIN, "token": TOKEN})
            credentials_in_aws.create_credentials_from_aws_secrets_manager()

        m.assert_called_once_with(str(DEFAULT_HOME_PATH), "w+")
        m_json.assert_called_with(
            {"domain": DOMAIN, "token": TOKEN},
            m.return_value.__enter__.return_value,
            indent=4,
        )

    @mock_secretsmanager
    @mock_sts
    def test__get_secrets_cache_client(self):
        """Tests _get_secrets_cache_client method."""
        # Mock _get_credentials() method to return the fake credentials
        fake_assumed_role_object = boto3.client("sts").assume_role(
                    RoleArn=AWS_ROLE_ARN,
                    RoleSessionName="AssumeCodeoceanRoleSession",
                )
        with patch.object(credentials_in_aws, "_get_credentials") as mock_get_credentials:
            mock_get_credentials.return_value = fake_assumed_role_object["Credentials"]  
            cache = credentials_in_aws._get_secrets_cache_client()
        self.assertIsInstance(cache, SecretCache)

    @mock_secretsmanager
    @mock_sts
    def test__get_credentials(self):
        """Tests _get_credentials method."""
        credentials = credentials_in_aws._get_credentials()
        self.assertIsNotNone(credentials)

    # test for ClientError when assuming role
    def test__get_credentials_client_error(self):
        """Tests _get_credentials method for ClientError."""
        with patch.object(boto3.client("sts"), "assume_role") as mock_assume_role:
            mock_assume_role.side_effect = botocore.exceptions.ClientError(
                error_response={"Error": {"Code": "ClientError"}},
                operation_name="assume_role",
            )
            with self.assertRaises(botocore.exceptions.ClientError):
                credentials_in_aws._get_credentials()

    # test for ClientError when getting secret
    @mock_secretsmanager
    @mock_sts
    def test__get_secret_client_error(self):
        """Tests _get_secret method for ClientError."""
        with self.assertRaises(botocore.exceptions.ClientError):
            credentials_in_aws._get_secret(secret_name="wrong")
    