"""Tests credentials loader."""
import os
import unittest
from pathlib import Path
from unittest import mock

from aind_codeocean_api.credentials import CodeOceanCredentials

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
FAKE_CREDENTIALS_PATH = TEST_DIR / "resources" / "fake_credentials.json"


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
