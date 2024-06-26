"""Tests CodeOcean API python interface"""

import json
import unittest
from typing import Any, Callable, List
from unittest import mock
from unittest.mock import call

import requests

from aind_codeocean_api.codeocean import CodeOceanClient
from aind_codeocean_api.credentials import CodeOceanCredentials
from aind_codeocean_api.models.computations_requests import (
    ComputationDataAsset,
    RunCapsuleRequest,
)
from aind_codeocean_api.models.data_assets_requests import (
    CreateDataAssetRequest,
    Source,
    Sources,
)


class MockResponse:
    """Mocks a rest request response"""

    def __init__(self, content: dict, status_code: int, url: str) -> None:
        """
        Creates a Mocked Response
        Parameters
        ----------
        content : dict
        status_code : int
        """
        self.content = content
        self.status_code = status_code
        self.url = url


class TestCodeOceanDataAssetRequests(unittest.TestCase):
    """Tests Data Asset Requests class methods"""

    domain = "https://acmecorp.codeocean.com"
    auth_token = "CODEOCEAN_API_TOKEN"

    co_client = CodeOceanClient(domain, auth_token)

    @staticmethod
    def mock_success_response(
        map_input_to_success_message: Callable[..., Any], req_type: str
    ) -> Callable[..., MockResponse]:
        """
        Helper method to mock out a success response
        Parameters
        ----------
        map_input_to_success_message : Callable
            A function that maps inputs to a dict
        req_type : str
            TODO: Change this to an enum

        Returns
        -------
        Callable
            A function that maps to a MockResponse

        """

        def request_post_response(json: dict) -> MockResponse:
            """Mock a post response"""
            success_message = map_input_to_success_message(json)
            return MockResponse(
                status_code=200, content=success_message, url=""
            )

        def request_get_response(url: str) -> MockResponse:
            """Mock a get response"""
            success_message = map_input_to_success_message(url)
            return MockResponse(
                status_code=200, content=success_message, url=url
            )

        def request_put_response(url: str, json: dict) -> MockResponse:
            """Mock a put response"""
            success_message = map_input_to_success_message(url, json)
            return MockResponse(
                status_code=200, content=success_message, url=url
            )

        def request_patch_response(url: str) -> MockResponse:
            """Mock a patch response"""
            success_message = map_input_to_success_message(url)
            return MockResponse(
                status_code=204, content=success_message, url=url
            )

        def request_delete_response(url: str) -> MockResponse:
            """Mock a delete response"""
            success_message = map_input_to_success_message(url)
            return MockResponse(
                status_code=204, content=success_message, url=url
            )

        # TODO: Change these to enums
        if req_type == "post":
            return request_post_response
        elif req_type == "get":
            return request_get_response
        elif req_type == "patch":
            return request_patch_response
        elif req_type == "delete":
            return request_delete_response
        else:
            return request_put_response

    def test_source_raise_exception(self):
        """Tests and exception is raised if Source is missing fields"""
        with self.assertRaises(Exception) as e:
            Source()
        self.assertEqual(
            "Exception('At least one source is required')", repr(e.exception)
        )

    @mock.patch("requests.post")
    def test_register_aws_data_asset(
        self, mock_api_post: unittest.mock.MagicMock
    ) -> None:
        """Tests the response of registering a data asset"""
        asset_name = "ASSET_NAME"
        mount = "MOUNT_NAME"
        bucket = "BUCKET_NAME"
        prefix = "PREFIX_NAME"
        tags = ["tag1", "tag2"]
        custom_metadata = {"modality": "ecephys", "subject id": "567890"}
        aws_source = Sources.AWS(
            bucket=bucket,
            prefix=prefix,
            keep_on_external_storage=True,
            public=True,
        )
        source = Source(aws=aws_source)
        create_data_asset_request = CreateDataAssetRequest(
            name=asset_name,
            tags=tags,
            mount=mount,
            source=source,
            custom_metadata=custom_metadata,
        )

        input_json_data = json.loads(create_data_asset_request.json_string)

        def map_to_success_message(input_json: dict) -> dict:
            """Map to a success message"""
            success_message = {
                "created": 1641420832,
                "description": "",
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
            "description": "",
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

        # Input request as dict
        response = self.co_client.create_data_asset(request=input_json_data)
        self.assertEqual(response.content, expected_request_response)
        self.assertEqual(response.status_code, 200)

        # Input request as class
        response2 = self.co_client.create_data_asset(
            request=create_data_asset_request
        )
        self.assertEqual(response2.content, expected_request_response)
        self.assertEqual(response2.status_code, 200)

    @mock.patch("requests.post")
    def test_register_gcp_data_asset(
        self, mock_api_post: unittest.mock.MagicMock
    ) -> None:
        """Tests the response of registering a data asset"""
        asset_name = "ASSET_NAME"
        mount = "MOUNT_NAME"
        bucket = "BUCKET_NAME"
        prefix = "PREFIX_NAME"
        tags = ["tag1", "tag2"]
        custom_metadata = {"modality": "ecephys", "subject id": "567890"}
        gcp_source = Sources.GCP(
            bucket=bucket,
            prefix=prefix,
            client_id="GCP_CLIENT_ID",
            client_secret="GCP_SECRET",
        )
        source = Source(gcp=gcp_source)
        create_data_asset_request = CreateDataAssetRequest(
            name=asset_name,
            tags=tags,
            mount=mount,
            source=source,
            custom_metadata=custom_metadata,
        )

        input_json_data = json.loads(create_data_asset_request.json_string)

        def map_to_success_message(input_json: dict) -> dict:
            """Map to a success message"""
            success_message = {
                "created": 1641420832,
                "description": "",
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
            "description": "",
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

        # Input request as dict
        response = self.co_client.create_data_asset(request=input_json_data)
        self.assertEqual(response.content, expected_request_response)
        self.assertEqual(response.status_code, 200)

        # Input request as class
        response2 = self.co_client.create_data_asset(
            request=create_data_asset_request
        )
        self.assertEqual(response2.content, expected_request_response)
        self.assertEqual(response2.status_code, 200)

    @mock.patch("requests.post")
    def test_register_computation_data_asset(
        self, mock_api_post: unittest.mock.MagicMock
    ) -> None:
        """Tests the response of registering a data asset"""
        asset_name = "ASSET_NAME"
        mount = "MOUNT_NAME"
        computation_id = "12345-abcdef"
        tags = ["tag1", "tag2"]
        custom_metadata = {"modality": "ecephys", "subject id": "567890"}
        computation_source = Sources.Computation(id=computation_id)
        source = Source(computation=computation_source)
        create_data_asset_request = CreateDataAssetRequest(
            name=asset_name,
            tags=tags,
            mount=mount,
            source=source,
            custom_metadata=custom_metadata,
        )

        input_json_data = json.loads(create_data_asset_request.json_string)

        def map_to_success_message(input_json: dict) -> dict:
            """Map to a success message"""
            success_message = {
                "created": 1641420832,
                "description": "",
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
            "description": "",
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

        # Input request as dict
        response = self.co_client.create_data_asset(request=input_json_data)
        self.assertEqual(response.content, expected_request_response)
        self.assertEqual(response.status_code, 200)

        # Input request as class
        response2 = self.co_client.create_data_asset(
            request=create_data_asset_request
        )
        self.assertEqual(response2.content, expected_request_response)
        self.assertEqual(response2.status_code, 200)

    def test_create_from_credentials(self):
        """Tests that the client can be constructed from a
        CodeOceanCredentials object"""
        creds = CodeOceanCredentials(domain="some_domain", token="some_token")
        client = CodeOceanClient.from_credentials(credentials=creds)
        self.assertEqual("some_domain", client.domain)
        self.assertEqual("some_token", client.token)

    @mock.patch("requests.get")
    def test_get_data_asset(
        self, mock_api_get: unittest.mock.MagicMock
    ) -> None:
        """Tests get_data_asset method."""

        def map_to_success_message(url: str) -> dict:
            """Map to a success message"""
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

    @mock.patch("requests.get")
    def test_search_data_assets(
        self, mock_api_get: unittest.mock.MagicMock
    ) -> None:
        """Tests search_data_assets method."""

        def map_to_success_message(url: str) -> dict:
            """Map to a success message"""
            success_response = {
                "created": 1670206314,
                "description": "",
                "files": 1551,
                "id": "6260cf28-de91-4528-9286-9c09869e00ec",
                "last_used": 0,
                "name": "ecephys_632269_2022-10-10_16-13-22",
                "size": 3632927970,
                "state": "ready",
                "tags": ["ecephys", "raw"],
                "type": "dataset",
            }
            return success_response

        mocked_success_get = self.mock_success_response(
            map_to_success_message, req_type="get"
        )

        example_data_asset_id = "6260cf28-de91-4528-9286-9c09869e00ec"
        example_query = "tag:ecephys"
        example_favorite = True
        example_archived = True

        mock_api_get.return_value = mocked_success_get(
            url=f"{self.co_client.asset_url}"
        )

        response = self.co_client.search_data_assets(
            query=example_query,
            favorite=example_favorite,
            archived=example_archived,
        )

        expected_response = {
            "created": 1670206314,
            "description": "",
            "files": 1551,
            "id": example_data_asset_id,
            "last_used": 0,
            "name": "ecephys_632269_2022-10-10_16-13-22",
            "size": 3632927970,
            "state": "ready",
            "tags": ["ecephys", "raw"],
            "type": "dataset",
        }

        mock_api_get.assert_called_once_with(
            "https://acmecorp.codeocean.com/api/v1/data_assets",
            params={
                "favorite": True,
                "archived": True,
                "query": "tag:ecephys",
            },
            auth=("CODEOCEAN_API_TOKEN", ""),
        )
        self.assertEqual(response.content, expected_response)
        self.assertEqual(response.status_code, 200)

    @mock.patch("requests.Session.get")
    def test_search_all_data_assets(
        self, mock_api_get: unittest.mock.MagicMock
    ) -> None:
        """Tests search_all_data_assets method."""

        mocked_response1 = requests.Response()
        mocked_response1.status_code = 200
        mocked_response1._content = json.dumps(
            {
                "has_more": True,
                "results": [
                    {"id": "abc123", "type": "dataset"},
                    {"id": "def456", "type": "result"},
                ],
            }
        ).encode("utf-8")

        mocked_response2 = requests.Response()
        mocked_response2.status_code = 200
        mocked_response2._content = json.dumps(
            {
                "has_more": False,
                "results": [
                    {"id": "ghi789", "type": "result"},
                    {"id": "jkl101", "type": "result"},
                ],
            }
        ).encode("utf-8")

        mock_api_get.side_effect = [mocked_response1, mocked_response2]
        response = self.co_client.search_all_data_assets()

        expected_response = {
            "results": [
                {"id": "abc123", "type": "dataset"},
                {"id": "def456", "type": "result"},
                {"id": "ghi789", "type": "result"},
                {"id": "jkl101", "type": "result"},
            ]
        }

        actual_response = response.json()

        mock_api_get.assert_has_calls(
            [
                call(
                    "https://acmecorp.codeocean.com/api/v1/data_assets",
                    params={"start": 2, "limit": 1000},
                    auth=("CODEOCEAN_API_TOKEN", ""),
                ),
                call(
                    "https://acmecorp.codeocean.com/api/v1/data_assets",
                    params={"start": 2, "limit": 1000},
                    auth=("CODEOCEAN_API_TOKEN", ""),
                ),
            ]
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_response, actual_response)

    @mock.patch("requests.Session.get")
    @mock.patch("aind_codeocean_api.codeocean.sleep", return_value=None)
    def test_search_all_data_assets_bad_response_max_retry_once(
        self,
        mock_sleep: unittest.mock.MagicMock,
        mock_api_get: unittest.mock.MagicMock,
    ) -> None:
        """Tests search_all_data_assets method when a bad response is
        returned once and then a good response is returned."""

        mocked_response1 = requests.Response()
        mocked_response1.status_code = 200
        mocked_response1._content = json.dumps(
            {
                "has_more": True,
                "results": [
                    {"id": "abc123", "type": "dataset"},
                    {"id": "def456", "type": "result"},
                ],
            }
        ).encode("utf-8")

        mocked_response2 = requests.Response()
        mocked_response2.status_code = 200
        mocked_response2._content = json.dumps(
            {
                "has_more": False,
                "results": [
                    {"id": "ghi789", "type": "result"},
                    {"id": "jkl101", "type": "result"},
                ],
            }
        ).encode("utf-8")

        bad_response = requests.Response()
        bad_response.status_code = 500
        bad_response._content = json.dumps(
            {"message": "Internal Server Error"}
        ).encode("utf-8")

        mock_api_get.side_effect = [
            mocked_response1,
            bad_response,
            mocked_response2,
        ]
        expected_response = {
            "results": [
                {"id": "abc123", "type": "dataset"},
                {"id": "def456", "type": "result"},
                {"id": "ghi789", "type": "result"},
                {"id": "jkl101", "type": "result"},
            ]
        }
        response = self.co_client.search_all_data_assets()
        actual_response = response.json()
        self.assertEqual(expected_response, actual_response)
        mock_sleep.assert_has_calls([call(1)])

    @mock.patch("requests.Session.get")
    @mock.patch("aind_codeocean_api.codeocean.sleep", return_value=None)
    def test_search_all_data_assets_bad_response_max_retries(
        self,
        mock_sleep: unittest.mock.MagicMock,
        mock_api_get: unittest.mock.MagicMock,
    ) -> None:
        """Tests search_all_data_assets method when a bad response is
        returned."""

        mocked_response1 = requests.Response()
        mocked_response1.status_code = 200
        mocked_response1._content = json.dumps(
            {
                "has_more": True,
                "results": [
                    {"id": "abc123", "type": "dataset"},
                    {"id": "def456", "type": "result"},
                ],
            }
        ).encode("utf-8")

        bad_response = requests.Response()
        bad_response.status_code = 500
        bad_response._content = json.dumps(
            {"message": "Internal Server Error"}
        ).encode("utf-8")

        mock_api_get.side_effect = [
            mocked_response1,
            bad_response,
            bad_response,
            bad_response,
            bad_response,
        ]
        with self.assertRaises(ConnectionError) as e:
            self.co_client.search_all_data_assets()
        self.assertEqual(
            "There was an error getting data from Code Ocean: 500",
            e.exception.args[0],
        )
        mock_sleep.assert_has_calls([call(1), call(4), call(9)])

    @mock.patch("requests.put")
    def test_update_data_asset(
        self, mock_api_put: unittest.mock.MagicMock
    ) -> None:
        """Tests update_data_asset_method"""

        def map_to_success_message(url: str, json: dict) -> dict:
            """Map to a success message"""
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
            "custom_metadata": {"key": "value"},
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
            new_custom_metadata={"key": "value"},
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
    def test_run_capsule(self, mock_api_post: unittest.mock.MagicMock) -> None:
        """Tests run_capsule with capsule id method."""

        def map_to_success_message(input_json: dict) -> dict:
            """Map to a success message"""
            input_id = input_json.get("capsule_id")
            success_message = {
                "created": 1646943238,
                "has_results": False,
                "id": input_id,
                "name": "Run 6943238",
                "run_time": 1,
                "state": "initializing",
            }
            return success_message

        capsule_id = "xyz-890"
        data_assets = [
            ComputationDataAsset(id="12345-abcdef", mount="SOME_MOUNT")
        ]
        run_capsule_request = RunCapsuleRequest(
            capsule_id=capsule_id, data_assets=data_assets
        )
        run_capsule_request_json = json.loads(run_capsule_request.json_string)
        mocked_success_post = self.mock_success_response(
            map_to_success_message, req_type="post"
        )

        mock_api_post.return_value = mocked_success_post(
            json=run_capsule_request_json
        )

        run_capsule_response1 = self.co_client.run_capsule(
            request=run_capsule_request_json
        )
        run_capsule_response2 = self.co_client.run_capsule(
            request=run_capsule_request
        )
        expected_capsule_response = {
            "created": 1646943238,
            "has_results": False,
            "id": capsule_id,
            "name": "Run 6943238",
            "run_time": 1,
            "state": "initializing",
        }
        self.assertEqual(
            expected_capsule_response, run_capsule_response1.content
        )
        self.assertEqual(run_capsule_response1.status_code, 200)
        self.assertEqual(
            expected_capsule_response, run_capsule_response2.content
        )
        self.assertEqual(run_capsule_response2.status_code, 200)

    @mock.patch("requests.post")
    def test_run_pipeline(
        self, mock_api_post: unittest.mock.MagicMock
    ) -> None:
        """Tests run_capsule with pipeline id method."""

        def map_to_success_message(input_json: dict) -> dict:
            """Map to a success message"""
            input_id = input_json.get("pipeline_id")
            success_message = {
                "created": 1646943238,
                "has_results": False,
                "id": input_id,
                "name": "Run 6943238",
                "run_time": 1,
                "state": "initializing",
            }
            return success_message

        pipeline_id = "p-54524-adfnjkdbf"
        run_pipeline_request = RunCapsuleRequest(pipeline_id=pipeline_id)
        run_pipeline_request_json = json.loads(
            run_pipeline_request.json_string
        )
        mocked_success_post = self.mock_success_response(
            map_to_success_message, req_type="post"
        )

        mock_api_post.return_value = mocked_success_post(
            json=run_pipeline_request_json
        )

        run_pipeline_response1 = self.co_client.run_capsule(
            request=run_pipeline_request_json
        )
        expected_pipeline_response = {
            "created": 1646943238,
            "has_results": False,
            "id": pipeline_id,
            "name": "Run 6943238",
            "run_time": 1,
            "state": "initializing",
        }
        self.assertEqual(
            expected_pipeline_response, run_pipeline_response1.content
        )
        self.assertEqual(run_pipeline_response1.status_code, 200)

    @mock.patch("requests.get")
    def test_get_capsule(self, mock_api_get: unittest.mock.MagicMock) -> None:
        """Tests get_capsule method."""

        def map_to_success_message(url: str) -> dict:
            """Map to a success message"""
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
    def test_get_capsule_computations(
        self, mock_api_get: unittest.mock.MagicMock
    ) -> None:
        """Test get_capsule_computations method."""

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

        def map_to_success_message(_) -> List[dict]:
            """Map to a success message"""
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
    def test_get_computation(
        self, mock_api_get: unittest.mock.MagicMock
    ) -> None:
        """Tests get_computation_method"""

        def map_to_success_message(url: str) -> dict:
            """Map to a success message"""
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
    def test_get_list_result_items(
        self, mock_api_post: unittest.mock.MagicMock
    ) -> None:
        """Tests get_list_result_items_method"""
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

        def map_to_success_message(_) -> dict:
            """Map to a success message"""
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
    def test_get_result_file_download_url(
        self, mock_api_get: unittest.mock.MagicMock
    ) -> None:
        """Tests get_result_file_download_url method"""

        expected_response_url = (
            "https://s3.us-west-2.amazonaws.com/BUCKET/A-BUNCH-OF-STUFF"
        )

        expected_response = {"url": expected_response_url}

        def map_to_success_message(_) -> dict:
            """Map to a success message"""
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

    @mock.patch("requests.post")
    def test_update_permissions(
        self, mock_api_post: unittest.mock.MagicMock
    ) -> None:
        """Tests the response of updating permissions"""

        def mock_success_response() -> Callable[..., MockResponse]:
            """Mock a successful response"""

            def request_post_response(json: dict) -> MockResponse:
                """Mock a post response"""
                return MockResponse(status_code=204, content={}, url="")

            return request_post_response

        users = [{"email": "user2@email.com", "role": "viewer"}]
        groups = [{"group": "group4", "role": "viewer"}]
        everyone = "viewer"

        example_data_asset_id = "648473aa-791e-4372-bd25-205cc587ec56"
        input_json_data = {
            "data_asset_id": example_data_asset_id,
            "users": users,
            "groups": groups,
            "everyone": everyone,
        }

        mocked_success_post = mock_success_response()
        mock_api_post.return_value = mocked_success_post(json=input_json_data)

        response = self.co_client.update_permissions(
            data_asset_id=example_data_asset_id,
            users=users,
            groups=groups,
            everyone=everyone,
        )
        self.assertEqual(response.status_code, 204)

    @mock.patch("requests.post")
    def test_update_permissions_everyone_none(
        self, mock_api_post: unittest.mock.MagicMock
    ) -> None:
        """Tests the response of updating permissions"""

        def mock_success_response() -> Callable[..., MockResponse]:
            """Mock a success response"""

            def request_post_response(json: dict) -> MockResponse:
                """Mock a post response"""
                return MockResponse(status_code=204, content={}, url="")

            return request_post_response

        users: List[dict] = [{"email": "user2@email.com", "role": "viewer"}]
        groups: List[dict] = [{"group": "group4", "role": "viewer"}]

        example_data_asset_id = "648473aa-791e-4372-bd25-205cc587ec56"
        input_json_data = {
            "data_asset_id": example_data_asset_id,
            "users": users,
            "groups": groups,
        }

        mocked_success_post = mock_success_response()
        mock_api_post.return_value = mocked_success_post(json=input_json_data)

        response = self.co_client.update_permissions(
            data_asset_id=example_data_asset_id, users=users, groups=groups
        )
        self.assertEqual(response.status_code, 204)

    @mock.patch("requests.patch")
    def test_archive_data_asset(
        self, mock_api_patch: unittest.mock.MagicMock
    ) -> None:
        """Tests the response of archiving a data asset"""

        def map_to_success_message(_) -> dict:
            """Map to a success message"""
            return {}

        mocked_success_patch = self.mock_success_response(
            map_to_success_message, req_type="patch"
        )

        example_data_asset_id = "da8dd108-2a10-471d-82b9-1e671b107bf8"
        expected_url = (
            f"{self.co_client.asset_url}/"
            "{example_data_asset_id}/archive?archive=True"
        )

        mock_api_patch.return_value = mocked_success_patch(url=expected_url)

        response = self.co_client.archive_data_asset(
            data_asset_id=example_data_asset_id, archive=True
        )

        self.assertEqual(response.url, expected_url)
        self.assertEqual(response.status_code, 204)

    @mock.patch("requests.delete")
    def test_delete_data_asset(
        self, mock_api_delete: unittest.mock.MagicMock
    ) -> None:
        """Tests the response of deleting a data asset"""

        def map_to_success_message(_) -> dict:
            """Map to a success message"""
            return {}

        mocked_success_delete = self.mock_success_response(
            map_to_success_message, req_type="delete"
        )

        example_data_asset_id = "da8dd108-2a10-471d-82b9-1e671b107bf8"
        expected_url = f"{self.co_client.asset_url}/{example_data_asset_id}"

        mock_api_delete.return_value = mocked_success_delete(url=expected_url)

        response = self.co_client.delete_data_asset(
            data_asset_id=example_data_asset_id
        )

        self.assertEqual(response.url, expected_url)
        self.assertEqual(response.status_code, 204)


if __name__ == "__main__":
    unittest.main()
