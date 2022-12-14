"""Tests credentials loader."""
import os
import unittest
from pathlib import Path
from unittest import mock
from unittest.mock import patch

from aind_codeocean_api.credentials import CodeOceanCredentials

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
FAKE_CREDENTIALS_PATH = TEST_DIR / "resources" / "fake_credentials.json"
FAKE_PATH_USER_INPUT = TEST_DIR / "resources"


class TestCredentials(unittest.TestCase):
    """Tests credentials class methods."""

    @mock.patch.dict(
        os.environ,
        ({"CODEOCEAN_CREDENTIALS_PATH": str(FAKE_CREDENTIALS_PATH)}),
    )
    def test_credentials(self):
        """Tests credentials are loaded correctly."""
        co_creds = CodeOceanCredentials()
        self.assertEqual({"token": "a_fake_token"}, co_creds.credentials)

    @patch("json.load")
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=unittest.mock.mock_open())
    @mock.patch.dict(os.environ, {}, clear=True)
    def test_credentials_path(self, m, m_path_exists, m_json):
        """Tests credentials path."""
        m_path_exists.return_value = True
        m_json.return_value = {}
        m_json.assert_called_once_with(m.return_value.__enter__.return_value)

    @patch("json.dump")
    @patch("builtins.open", new_callable=unittest.mock.mock_open())
    def test_create_credentials(self, m, m_json):
        domain = "https://acmecorp.codeocean.com"
        token = "fake_token"

        CodeOceanCredentials.create_credentials(
            api_domain=domain,
            access_token=token,
            file_location="mock_file.json",
        )

        m.assert_called_once_with("mock_file.json", "w+")
        m_json.assert_called_with(
            {"domain": domain, "token": token},
            m.return_value.__enter__.return_value,
            indent=4,
        )


if __name__ == "__main__":
    unittest.main()
