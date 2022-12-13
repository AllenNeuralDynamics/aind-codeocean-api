"""Tests credentials loader."""
import os
import unittest
from pathlib import Path
from unittest import mock
from unittest.mock import mock_open, patch

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
        self.assertEqual(str(FAKE_CREDENTIALS_PATH), co_creds.credentials_path)
        self.assertEqual({"token": "a_fake_token"}, co_creds.credentials)

    def test_create_credentials(self):
        domain = "https://acmecorp.codeocean.com"
        token = "fake_token"

        with patch("fake_credentials.json", mock_open()) as mocked_file:
            CodeOceanCredentials().create_credentials(
                api_domain=domain,
                access_token=token,
                file_location=FAKE_PATH_USER_INPUT,
            )

            mocked_file.assert_called_once_with(FAKE_PATH_USER_INPUT, "w")

            mocked_file.write.assert_called_once_with(
                {"domain": domain, "token": token}
            )


if __name__ == "__main__":
    unittest.main()
