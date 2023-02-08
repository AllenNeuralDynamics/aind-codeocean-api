"""Test credentials in AWS"""
import os
import sys
import json
import unittest
from pathlib import Path
from unittest import mock
from unittest.mock import patch

from aws_secretsmanager_caching import SecretCache
import boto3
import botocore
from moto import mock_secretsmanager, mock_sts

from aind_codeocean_api.credentials import CodeOceanCredentials
from aind_codeocean_api import credentials_in_aws

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
FAKE_CREDENTIALS_PATH = TEST_DIR / "resources" / "fake_credentials.json"
FAKE_PATH_USER_INPUT = TEST_DIR / "resources"
AWS_ROLE_ARN = "arn:aws:iam::467914378000:role/codeocean-secret-retriever"
orig = botocore.client.BaseClient._make_api_call


class MockSecretCache:
    """Mock of the boto3 secrets cache client."""
    def get_secret_string(*args, **kwargs):
        print("Mock get_secret_string called")
        return json.dumps({"domain": "https://acmecorp.codeocean.com", "token": "fake_token"})

class TestCredentialsInAWS(unittest.TestCase):
    """Tests credentials in AWS methods."""
    @mock_secretsmanager
    @mock_sts
    def test__get_secret(self):
        """Tests _get_secret method."""
        domain = "https://acmecorp.codeocean.com"
        token = "fake_token"
        # 
        fake_sm = boto3.client("secretsmanager", region_name="us-west-2")
        mock_secret = fake_sm.create_secret(
            Name="codeocean-service-account",
            SecretString=json.dumps({"domain": "https://acmecorp.codeocean.com", "token": "fake_token"})
        )
        print("Mock secret created: " + json.dumps(mock_secret))

        # Mock _get_secrets_cache_client() method to return the fake secretsmanager
        with patch.object(credentials_in_aws, "_get_secrets_cache_client") as mock_get_secrets_cache_client:
            mock_get_secrets_cache_client.return_value = MockSecretCache()
            secret = credentials_in_aws._get_secret(secret_name="codeocean-service-account")
        
        self.assertEqual(secret, json.dumps({"domain": domain, "token": token}))

    @patch("json.dump")
    @patch("builtins.open", new_callable=unittest.mock.mock_open())
    def test_create_credentials_from_aws(self, m, m_json):
        """Tests that credentials are loaded from AWS."""
        domain = "https://acmecorp.codeocean.com"
        token = "fake_token"
        
        # Create a mock for the _get_secret method that returns the fake credentials from a mocked secretsmanager
        with patch.object(credentials_in_aws, "_get_secret") as mock_get_secret:
            mock_get_secret.return_value = {"domain": domain, "token": token}

        credentials_in_aws.create_credentials_from_aws_secrets_manager(
            secret_name="test_secret",
            file_location="mock_file.json"
        )

        m.assert_called_once_with("mock_file.json", "w+")
        m_json.assert_called_with(
            {"domain": domain, "token": token},
            m.return_value.__enter__.return_value,
            indent=4,
        )
        co_creds = CodeOceanCredentials()
        self.assertEqual({"token": "a_fake_token"}, co_creds.credentials)
