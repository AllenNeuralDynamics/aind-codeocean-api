"""Test credentials in AWS"""
import os
import sys
import unittest
from pathlib import Path
from unittest import mock
from unittest.mock import patch

from aind_codeocean_api.credentials import CodeOceanCredentials
from aind_codeocean_api import credentials_in_aws


TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
FAKE_CREDENTIALS_PATH = TEST_DIR / "resources" / "fake_credentials.json"
FAKE_PATH_USER_INPUT = TEST_DIR / "resources"


class TestCredentialsInAWS(unittest.TestCase):
    """Tests credentials in AWS methods."""


    def test_create_credentials_from_aws(self):
        """Tests that credentials are loaded from AWS."""
        
        credentials_in_aws.create_credentials_from_aws_secrets_manager(
            secret_name="test_secret",
            file_location="mock_file.json"
        )

        co_creds = CodeOceanCredentials()
        self.assertEqual({"token": "a_fake_token"}, co_creds.credentials)

    @patch("json.dump")
    @patch("builtins.open", new_callable=unittest.mock.mock_open())
    def test_create_credentials(self, m, m_json):
        """Tests create_credentials method."""
        domain = "https://acmecorp.codeocean.com"
        token = "fake_token"

        create

        m.assert_called_once_with("mock_file.json", "w+")
        m_json.assert_called_with(
            {"domain": domain, "token": token},
            m.return_value.__enter__.return_value,
            indent=4,
        )

