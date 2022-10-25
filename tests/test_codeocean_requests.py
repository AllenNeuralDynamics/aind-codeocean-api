"""Tests CodeOcean API python interface"""
import unittest
from unittest import mock

from code_ocean_api import CodeOceanDataAssetRequests

class TestCodeOceanDataAssetRequests(unittest.TestCase):
    """Tests Data Asset Requests class methods"""

    domain = "https://acmecorp.codeocean.com"
    auth_token = "CODEOCEAN_API_TOKEN"

    co_client = CodeOceanDataAssetRequests(domain, auth_token)

    expected_json_data = {
        "name": "ecephys_625463_2022-10-06_10-14-25",
        "description": "",
        "mount": "ecephys_625463_2022-10-06_10-14-25",
        "tags": ["ecephys"],
        "source": {
            "aws": {
                "bucket": "aind-test-bucket",
                "prefix": "ecephys_625463_2022-10-06_10-14-25",
                "keep_on_external_storage": True,
                "index_data": True,
                "access_key_id": "AWS_ACCESS_KEY",
                "secret_access_key": "AWS_SECRET_ACCESS_KEY",
            }
        },
    }

    expected_request_response = {
        "created": 1641420832,
        "description": expected_json_data["description"],
        "files": 0,
        "id": "44ec16c3-cb5a-45f5-93d1-cba8be800c24",
        "lastUsed": 0,
        "name": expected_json_data["name"],
        "sizeInBytes": 0,
        "state": "DATA_ASSET_STATE_DRAFT",
        "tags": expected_json_data["tags"],
        "type": "DATA_ASSET_TYPE_DATASET",
    }

    @staticmethod
    def mocked_request_post(json_data: dict):
        """
        Used to mock a response for testing purposes.
        Args:
            json_data (json): Data sent alongside a request
        Returns:
            A Mocked Response (message: json, status_code: int)
        """

        class MockResponse:
            def __init__(self, message, status_code):
                self.message = message
                self.status_code = status_code

        success_message = {
            "created": 1641420832,
            "description": json_data["description"],
            "files": 0,
            "id": "44ec16c3-cb5a-45f5-93d1-cba8be800c24",
            "lastUsed": 0,
            "name": json_data["name"],
            "sizeInBytes": 0,
            "state": "DATA_ASSET_STATE_DRAFT",
            "tags": json_data["tags"],
            "type": "DATA_ASSET_TYPE_DATASET",
        }

        return MockResponse(status_code=200, message=success_message)

    def test_json_data(self):
        """Tests that the json data is created correctly"""
        created_json_data = self.co_client.create_post_json_data(
            asset_name="ecephys_625463_2022-10-06_10-14-25",
            mount="ecephys_625463_2022-10-06_10-14-25",
            bucket="aind-test-bucket",
            prefix="ecephys_625463_2022-10-06_10-14-25",
            access_key_id="AWS_ACCESS_KEY",
            secret_access_key="AWS_SECRET_ACCESS_KEY",
            tags=["ecephys"],
        )

        self.assertEqual(self.expected_json_data, created_json_data)

    @mock.patch(
        "transfer.codeocean.CodeOceanDataAssetRequests.register_data_asset"
    )
    def test_register_data_asset(self, mock_api_call):
        """Tests the response of registering a data asset"""
        client = CodeOceanDataAssetRequests(
            domain=self.domain, token=self.auth_token
        )
        mock_api_call.return_value = self.mocked_request_post(
            self.expected_json_data
        )
        response = client.register_data_asset(
            json_data=self.expected_json_data
        )
        self.assertEqual(response.message, self.expected_request_response)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
