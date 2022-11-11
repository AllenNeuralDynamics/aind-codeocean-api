"""Tests CodeOcean API python interface"""
import unittest
from unittest import mock

from aind_codeocean_api.codeocean import CodeOceanClient


class MockResponse:
    """Mocks a rest request response"""

    def __init__(self, content, status_code):
        self.content = content
        self.status_code = status_code


class TestCodeOceanDataAssetRequests(unittest.TestCase):
    """Tests Data Asset Requests class methods"""

    domain = "https://acmecorp.codeocean.com"
    auth_token = "CODEOCEAN_API_TOKEN"

    co_client = CodeOceanClient(domain, auth_token)

    @staticmethod
    def mock_success_response(map_input_to_success_message, req_type):
        def request_post_response(json):
            success_message = map_input_to_success_message(json)
            return MockResponse(status_code=200, content=success_message)

        def request_get_response(url):
            success_message = map_input_to_success_message(url)
            return MockResponse(status_code=200, content=success_message)

        def request_put_response(url, json):
            success_message = map_input_to_success_message(url, json)
            return MockResponse(status_code=200, content=success_message)

        if req_type == "post":
            return request_post_response
        elif req_type == "get":
            return request_get_response
        else:
            return request_put_response

    @mock.patch("requests.post")
    def test_register_data_asset(self, mock_api_post):
        """Tests the response of registering a data asset"""
        asset_name = "ASSET_NAME"
        mount = "MOUNT_NAME"
        bucket = "BUCKET_NAME"
        prefix = "PREFIX_NAME"
        access_key_id = "AWS_ACCESS_KEY"
        secret_access_key = "AWS_SECRET_KEY"

        input_json_data = {
            "name": asset_name,
            "description": "",
            "mount": mount,
            "tags": [],
            "source": {
                "aws": {
                    "bucket": bucket,
                    "prefix": prefix,
                    "keep_on_external_storage": True,
                    "index_data": True,
                    "access_key_id": access_key_id,
                    "secret_access_key": secret_access_key
                },
            },
        }

        def map_to_success_message(input_json):
            success_message = {
                "created": 1641420832,
                "description": input_json["description"],
                "files": 0,
                "id": "44ec16c3-cb5a-45f5-93d1-cba8be800c24",
                "lastUsed": 0,
                "name": input_json["name"],
                "sizeInBytes": 0,
                "state": "DATA_ASSET_STATE_DRAFT",
                "tags": input_json["tags"],
                "type": "DATA_ASSET_TYPE_DATASET",
            }
            return success_message

        expected_request_response = {
            "created": 1641420832,
            "description": input_json_data["description"],
            "files": 0,
            "id": "44ec16c3-cb5a-45f5-93d1-cba8be800c24",
            "lastUsed": 0,
            "name": input_json_data["name"],
            "sizeInBytes": 0,
            "state": "DATA_ASSET_STATE_DRAFT",
            "tags": input_json_data["tags"],
            "type": "DATA_ASSET_TYPE_DATASET",
        }

        mocked_success_post = self.mock_success_response(
            map_to_success_message, req_type="post"
        )
        mock_api_post.return_value = mocked_success_post(json=input_json_data)

        response = self.co_client.register_data_asset(
            asset_name=asset_name,
            mount=mount,
            bucket=bucket,
            prefix=prefix, access_key_id=access_key_id,
            secret_access_key= secret_access_key
        )
        self.assertEqual(response.content, expected_request_response)
        self.assertEqual(response.status_code, 200)

    @mock.patch("requests.get")
    def test_get_data_asset(self, mock_api_get):
        def map_to_success_message(url):
            data_asset_id = url.split("/")[-1]
            success_response = {
                "created": 1666322134,
                "description": "",
                "files": 1364,
                "id": data_asset_id,
                "last_used": 0,
                "name": "ecephys_632269_2022-10-10_16-13-22",
                "size": 3632927966,
                "state": "ready",
                "tags": ["ecephys", "raw"],
                "type": "dataset",
            }
            return success_response

        mocked_success_get = self.mock_success_response(
            map_to_success_message, req_type="get"
        )

        example_data_asset_id = "5444cf28-de91-4528-9286-9c09869e00ec"

        mock_api_get.return_value = mocked_success_get(
            url=f"{self.co_client.asset_url}/{example_data_asset_id}"
        )

        response = self.co_client.get_data_asset(
            data_asset_id=example_data_asset_id
        )

        expected_response = {
            "created": 1666322134,
            "description": "",
            "files": 1364,
            "id": example_data_asset_id,
            "last_used": 0,
            "name": "ecephys_632269_2022-10-10_16-13-22",
            "size": 3632927966,
            "state": "ready",
            "tags": ["ecephys", "raw"],
            "type": "dataset",
        }

        self.assertEqual(response.content, expected_response)
        self.assertEqual(response.status_code, 200)

    @mock.patch("requests.put")
    def test_update_data_asset(self, mock_api_put):
        def map_to_success_message(url, json):
            data_asset_id = url.split("/")[-1]
            success_response = {
                "created": 1633277005,
                "description": json["description"],
                "files": 0,
                "id": data_asset_id,
                "last_used": 0,
                "name": json["name"],
                "size": 0,
                "state": "ready",
                "tags": json["tags"],
                "type": "dataset",
            }
            return success_response

        example_data_asset_id = "5444cf28-de91-4528-9286-9c09869e00ec"
        example_json = {
            "name": "modified name",
            "description": "a new description",
            "tags": ["aaa", "bbb"],
            "mount": "newmount",
        }
        mocked_success_put = self.mock_success_response(
            map_to_success_message, req_type="put"
        )
        mock_api_put.return_value = mocked_success_put(
            url=f"{self.co_client.asset_url}/{example_data_asset_id}",
            json=example_json,
        )

        response = self.co_client.update_data_asset(
            data_asset_id=example_data_asset_id,
            new_name="modified name",
            new_description="a new description",
            new_tags=["aaa", "bbb"],
            new_mount="newmount",
        )

        expected_response = {
            "created": 1633277005,
            "description": "a new description",
            "files": 0,
            "id": example_data_asset_id,
            "last_used": 0,
            "name": "modified name",
            "size": 0,
            "state": "ready",
            "tags": ["aaa", "bbb"],
            "type": "dataset",
        }

        self.assertEqual(expected_response, response.content)
        self.assertEqual(response.status_code, 200)

    @mock.patch("requests.post")
    def test_run_capsule(self, mock_api_post):
        def map_to_success_message(input_json):

            success_message = {
                "created": 1646943238,
                "has_results": False,
                "id": input_json["capsule_id"],
                "name": "Run 6943238",
                "run_time": 1,
                "state": "initializing",
            }
            return success_message

        example_capsule_id = "648473aa-791e-4372-bd25-205cc587ec56"
        input_json_data = {"capsule_id": example_capsule_id, "data_assets": []}

        mocked_success_post = self.mock_success_response(
            map_to_success_message, req_type="post"
        )
        mock_api_post.return_value = mocked_success_post(json=input_json_data)

        response = self.co_client.run_capsule(
            capsule_id=example_capsule_id, data_assets=[], parameters=['FOO']
        )
        expected_response = {
            "created": 1646943238,
            "has_results": False,
            "id": example_capsule_id,
            "name": "Run 6943238",
            "run_time": 1,
            "state": "initializing",
        }
        self.assertEqual(expected_response, response.content)
        self.assertEqual(response.status_code, 200)

    @mock.patch("requests.get")
    def test_get_capsule(self, mock_api_get):
        def map_to_success_message(url):
            capsule_id = url.split("/")[-1]
            success_response = {
                "cloned_from_url": "",
                "created": 1668106299,
                "description": "Test capsule",
                "field": "",
                "id": capsule_id,
                "keywords": None,
                "name": "test_capsule",
                "owner": "08774c66-1d22-4b0c-996b-349e09751da9",
                "published_capsule": "",
                "slug": "9464917",
                "status": "non-published",
            }
            return success_response

        mocked_success_get = self.mock_success_response(
            map_to_success_message, req_type="get"
        )

        example_capsule_id = "648473aa-791e-4372-bd25-205cc587ec56"

        mock_api_get.return_value = mocked_success_get(
            url=f"{self.co_client.asset_url}/{example_capsule_id}"
        )

        response = self.co_client.get_capsule(capsule_id=example_capsule_id)

        expected_response = {
            "cloned_from_url": "",
            "created": 1668106299,
            "description": "Test capsule",
            "field": "",
            "id": example_capsule_id,
            "keywords": None,
            "name": "test_capsule",
            "owner": "08774c66-1d22-4b0c-996b-349e09751da9",
            "published_capsule": "",
            "slug": "9464917",
            "status": "non-published",
        }

        self.assertEqual(response.content, expected_response)
        self.assertEqual(response.status_code, 200)

    @mock.patch("requests.get")
    def test_get_capsule_computations(self, mock_api_get):

        expected_response = [
            {
                "created": 1668125314,
                "end_status": "succeeded",
                "has_results": False,
                "id": "da8dd108-2a10-471d-82b9-1e671b107bf8",
                "name": "Run With Parameters 8125314",
                "parameters": [
                    {"name": "", "value": '{"p_1": {"p1_1": "some_path"}}'}
                ],
                "run_time": 8,
                "state": "completed",
            },
            {
                "created": 1668125128,
                "end_status": "succeeded",
                "has_results": False,
                "id": "26a3c3ce-c83b-4710-a513-1753afcc1ce9",
                "name": "Run With Parameters 8125314",
                "parameters": [
                    {"name": "", "value": '{"p_1": {"p1_1": "some_path"}}'}
                ],
                "run_time": 5,
                "state": "completed",
            },
        ]

        def map_to_success_message(url):
            return expected_response

        mocked_success_get = self.mock_success_response(
            map_to_success_message, req_type="get"
        )

        example_capsule_id = "648473aa-791e-4372-bd25-205cc587ec56"

        mock_api_get.return_value = mocked_success_get(url=None)

        response = self.co_client.get_capsule_computations(
            capsule_id=example_capsule_id
        )

        self.assertEqual(response.content, expected_response)
        self.assertEqual(response.status_code, 200)

    @mock.patch("requests.get")
    def test_get_computation(self, mock_api_get):
        def map_to_success_message(url):
            computation_id = url.split("/")[-1]
            success_response = {
                "created": 1668125314,
                "end_status": "succeeded",
                "has_results": False,
                "id": computation_id,
                "name": "Run With Parameters 8125314",
                "parameters": [
                    {"name": "", "value": '{"p_1": {"p1_1": "some_path"}}'}
                ],
                "run_time": 8,
                "state": "completed",
            }
            return success_response

        mocked_success_get = self.mock_success_response(
            map_to_success_message, req_type="get"
        )

        example_computation_id = "da8dd108-2a10-471d-82b9-1e671b107bf8"

        mock_api_get.return_value = mocked_success_get(
            url=f"{self.co_client.asset_url}/{example_computation_id}"
        )

        response = self.co_client.get_computation(
            computation_id=example_computation_id
        )

        expected_response = {
            "created": 1668125314,
            "end_status": "succeeded",
            "has_results": False,
            "id": example_computation_id,
            "name": "Run With Parameters 8125314",
            "parameters": [
                {"name": "", "value": '{"p_1": {"p1_1": "some_path"}}'}
            ],
            "run_time": 8,
            "state": "completed",
        }

        self.assertEqual(response.content, expected_response)
        self.assertEqual(response.status_code, 200)

    @mock.patch("requests.post")
    def test_get_list_result_items(self, mock_api_post):
        expected_response = {
            "items": [
                {
                    "name": "fig1.png",
                    "path": "fig1.png",
                    "size": 34003,
                    "type": "file",
                },
                {
                    "name": "output",
                    "path": "output",
                    "size": 20,
                    "type": "file",
                },
            ]
        }

        def map_to_success_message(json):
            success_response = expected_response
            return success_response

        example_computation_id = "39f087db-2f18-489a-b1a0-98e01acba251"

        mocked_success_post = self.mock_success_response(
            map_to_success_message, req_type="post"
        )
        mock_api_post.return_value = mocked_success_post(json=None)

        response = self.co_client.get_list_result_items(example_computation_id)

        self.assertEqual(response.content, expected_response)
        self.assertEqual(response.status_code, 200)

    @mock.patch("requests.get")
    def test_get_result_file_download_url(self, mock_api_get):

        expected_response_url = (
            "https://s3.us-west-2.amazonaws.com/BUCKET/A-BUNCH-OF-STUFF"
        )

        expected_response = {"url": expected_response_url}

        def map_to_success_message(url):
            success_response = expected_response
            return success_response

        mocked_success_get = self.mock_success_response(
            map_to_success_message, req_type="get"
        )

        example_computation_id = "da8dd108-2a10-471d-82b9-1e671b107bf8"
        example_file_name = "output"

        mock_api_get.return_value = mocked_success_get(url=None)

        response = self.co_client.get_result_file_download_url(
            computation_id=example_computation_id,
            path_to_file=example_file_name,
        )

        self.assertEqual(response.content, expected_response)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
