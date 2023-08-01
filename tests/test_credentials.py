"""Tests credentials loader."""
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from aind_codeocean_api.credentials import CodeOceanCredentials

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
FAKE_CREDENTIALS_PATH = TEST_DIR / "resources" / "fake_credentials.json"
FAKE_PATH_USER_INPUT = TEST_DIR / "resources"


class TestCredentials(unittest.TestCase):
    """Tests credentials class methods."""

    def test_basic_init(self):
        """Tests that the credentials can be instantiated with class
        constructor."""
        creds = CodeOceanCredentials(
            domain="http://acmecorp.com/", token="123-abc"
        )

        # Trailing slashes should be stripped
        self.assertEqual("http://acmecorp.com", creds.domain)
        self.assertEqual("123-abc", creds.token.get_secret_value())

    @patch.dict(
        os.environ,
        (
            {
                "CODEOCEAN_DOMAIN": "http://acmecorp-env.com",
                "CODEOCEAN_TOKEN": "123-abc-e",
            }
        ),
        clear=True,
    )
    def test_env_vars(self):
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


if __name__ == "__main__":
    unittest.main()
