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
                    "index_data": True
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
            map_to_success_message, req_type="post")
        mock_api_post.return_value = mocked_success_post(
            json=input_json_data
        )

        response = self.co_client.register_data_asset(
            asset_name=asset_name,
            mount=mount,
            bucket=bucket,
            prefix=prefix
        )
        self.assertEqual(response.content, expected_request_response)
        self.assertEqual(response.status_code, 200)

    @mock.patch("requests.get")
    def test_get_data_asset(self, mock_api_get):

        def map_to_success_message(url):
            data_asset_id = url.split("/")[-1]
            success_response = (
                {'created': 1666322134,
                 'description': '',
                 'files': 1364, 'id': data_asset_id,
                 'last_used': 0,
                 'name': 'ecephys_632269_2022-10-10_16-13-22',
                 'size': 3632927966,
                 'state': 'ready',
                 'tags': ['ecephys', 'raw'],
                 'type': 'dataset'}
            )
            return success_response

        mocked_success_get = self.mock_success_response(
            map_to_success_message, req_type="get")

        example_data_asset_id = "5444cf28-de91-4528-9286-9c09869e00ec"

        mock_api_get.return_value = mocked_success_get(
            url=f"{self.co_client.asset_url}/{example_data_asset_id}"
        )

        response = self.co_client.get_data_asset(
            data_asset_id=example_data_asset_id
        )

        expected_response = (
            {'created': 1666322134,
             'description': '',
             'files': 1364, 'id': example_data_asset_id,
             'last_used': 0,
             'name': 'ecephys_632269_2022-10-10_16-13-22',
             'size': 3632927966,
             'state': 'ready',
             'tags': ['ecephys', 'raw'],
             'type': 'dataset'}
        )

        self.assertEqual(response.content, expected_response)
        self.assertEqual(response.status_code, 200)

    @mock.patch("requests.put")
    def test_update_data_asset(self, mock_api_put):

        def map_to_success_message(url, json):
            data_asset_id = url.split("/")[-1]
            success_response = (
                {
                    "created": 1633277005,
                    "description": json["description"],
                    "files": 0,
                    "id": data_asset_id,
                    "last_used": 0,
                    "name": json["name"],
                    "size": 0,
                    "state": "ready",
                    "tags": json["tags"],
                    "type": "dataset"
                }

            )
            return success_response

        example_data_asset_id = "5444cf28-de91-4528-9286-9c09869e00ec"
        example_json = ({
            "name": "modified name",
            "description": "a new description",
            "tags": ["aaa", "bbb"],
            "mount": "newmount"
        })
        mocked_success_put = self.mock_success_response(
            map_to_success_message, req_type="put")
        mock_api_put.return_value = mocked_success_put(
            url=f"{self.co_client.asset_url}/{example_data_asset_id}",
            json=example_json
        )

        response = self.co_client.update_data_asset(
            data_asset_id=example_data_asset_id,
            new_name="modified name",
            new_description="a new description",
            new_tags=["aaa", "bbb"],
            new_mount="newmount"
        )

        expected_response = (
            {'created': 1633277005,
             'description': 'a new description',
             'files': 0,
             'id': example_data_asset_id,
             'last_used': 0,
             'name': 'modified name',
             'size': 0,
             'state': 'ready',
             'tags': ['aaa', 'bbb'],
             'type': 'dataset'}
        )

        self.assertEqual(expected_response, response.content)
        self.assertEqual(response.status_code, 200)

    @mock.patch("requests.post")
    def test_run_capsule(self, mock_api_post):

        def map_to_success_message(input_json):

            success_message = ({
                "created": 1646943238,
                "has_results": False,
                "id": input_json["capsule_id"],
                "name": "Run 6943238",
                "run_time": 1,
                "state": "initializing"
            })
            return success_message

        example_capsule_id = "648473aa-791e-4372-bd25-205cc587ec56"
        input_json_data = {
            'capsule_id': example_capsule_id,
            'data_assets': []
        }

        mocked_success_post = self.mock_success_response(
            map_to_success_message, req_type="post")
        mock_api_post.return_value = mocked_success_post(
            json=input_json_data
        )

        response = self.co_client.run_capsule(capsule_id=example_capsule_id,
                                              data_assets=[],
                                              parameters=[])
        expected_response = (
            {'created': 1646943238,
             'has_results': False,
             'id': example_capsule_id,
             'name': 'Run 6943238',
             'run_time': 1,
             'state': 'initializing'}
        )
        self.assertEqual(expected_response, response.content)
        self.assertEqual(response.status_code, 200)

    @mock.patch("requests.get")
    def test_get_capsule(self, mock_api_get):
        def map_to_success_message(url):
            capsule_id = url.split("/")[-1]
            success_response = (
                {'cloned_from_url': '',
                 'created': 1668106299,
                 'description': 'Test capsule',
                 'field': '',
                 'id': capsule_id,
                 'keywords': None,
                 'name': 'test_capsule',
                 'owner': '08774c66-1d22-4b0c-996b-349e09751da9',
                 'published_capsule': '',
                 'slug': '9464917',
                 'status': 'non-published'}
            )
            return success_response

        mocked_success_get = self.mock_success_response(
            map_to_success_message, req_type="get")

        example_capsule_id = "648473aa-791e-4372-bd25-205cc587ec56"

        mock_api_get.return_value = mocked_success_get(
            url=f"{self.co_client.asset_url}/{example_capsule_id}"
        )

        response = self.co_client.get_capsule(
            capsule_id=example_capsule_id
        )

        expected_response = (
            {'cloned_from_url': '',
             'created': 1668106299,
             'description': 'Test capsule',
             'field': '',
             'id': example_capsule_id,
             'keywords': None,
             'name': 'test_capsule',
             'owner': '08774c66-1d22-4b0c-996b-349e09751da9',
             'published_capsule': '',
             'slug': '9464917',
             'status': 'non-published'}
        )

        self.assertEqual(response.content, expected_response)
        self.assertEqual(response.status_code, 200)

#
# class MockResponse:
#     def __init__(self, message, status_code):
#         self.message = message
#         self.status_code = status_code
#
# class TestCodeOceanCapsuleRequests(unittest.TestCase):
#     """Tests Data Capsule Requests class methods"""
#
#     domain = "https://acmecorp.codeocean.com"
#     auth_token = "CODEOCEAN_API_TOKEN"
#
#     co_client = CodeOceanCapsuleRequests(domain, auth_token)
#
#     @staticmethod
#     def mocked_request_get(success_message: dict) -> MockResponse:
#         return MockResponse(status_code=200, message=success_message)
#
#     @staticmethod
#     def mocked_request_post(success_message: dict) -> MockResponse:
#         return MockResponse(status_code=200, message=success_message)
#
#     @mock.patch(
#         "aind_codeocean_api.CodeOceanCapsuleRequests.get_capsule"
#     )
#     def test_get_capsule(self, mock_api_call):
#         """Tests the response of get capsule"""
#
#         expected_json_data = {
#             'cloned_from_url': 'https://github.com/AllenNeuralDynamics/terastitcher-module.git',
#             'created': 1665287322,
#             'description': 'A tool for fast automatic 3D-stitching of teravoxel-sized microscopy images using cloud computing resources and TeraStitcher.',
#             'field': '',
#             'id': '9b41eecc-8qz2-4f5f-ada7-2e62d0008a63',
#             'keywords': None,
#             'name': 'TeraStitcher Module',
#             'owner': 'c3c3ezz1-dd26-49ab-a101-200a3011aded',
#             'published_capsule': '',
#             'slug': '0000000',
#             'status': 'non-published'
#         }
#
#         expected_request_response = {
#             'cloned_from_url': expected_json_data['cloned_from_url'],
#             "created": expected_json_data['created'],
#             "description": expected_json_data["description"],
#             "field": '',
#             "id": "9b41eecc-8qz2-4f5f-ada7-2e62d0008a63",
#             'keywords': None,
#             "name": expected_json_data["name"],
#             'owner': expected_json_data['owner'],
#             'published_capsule': '',
#             'slug': '0000000',
#             'status': 'non-published'
#         }
#
#         success_message = {
#             'cloned_from_url': expected_json_data['cloned_from_url'],
#             'created': expected_json_data['created'],
#             'description': expected_json_data['description'],
#             'field': '',
#             'id': '9b41eecc-8qz2-4f5f-ada7-2e62d0008a63',
#             'keywords': None,
#             'name': expected_json_data['name'],
#             'owner': 'c3c3ezz1-dd26-49ab-a101-200a3011aded',
#             'published_capsule': '',
#             'slug': '0000000',
#             'status': 'non-published'
#         }
#
#         mock_api_call.return_value = self.mocked_request_get(
#             success_message
#         )
#         response = self.co_client.get_capsule(
#             json_data=expected_json_data
#         )
#         self.assertEqual(response.message, expected_request_response)
#         self.assertEqual(response.status_code, 200)
#
#     @mock.patch(
#         "aind_codeocean_api.CodeOceanCapsuleRequests.get_capsule_computations"
#     )
#     def test_get_capsule_computations(self, mock_api_call):
#         """Tests the response of getting list of computations"""
#
#         expected_json_data = [
#             # Testing two possible cases, when it's running and when it's completed
#             {
#                 'created': 1667400000,
#                 'has_results': True,
#                 'id': '8ae000de-02fa-47f8-9zzz-2bb8160003e4',
#                 'name': 'Run With Parameters 0000000',
#                 'parameters': [{'name': '--input_data', 'value': 'SmartSPIM_597305_2022-09-27_00-07-58'},
#                 {'name': 'bucket_path', 'value': 'aind-open-data'}],
#                 'run_time': 95024,
#                 'state': 'running'
#             },
#             {
#                 'cloud_workstation': True,
#                 'created': 1667330000,
#                 'end_status': 'succeeded',
#                 'has_results': True,
#                 'id': '6c64620d-czzz-4fe3-99f2-702ec560000',
#                 'name': 'Run With Parameters 6760910',
#                 'run_time': 1009,
#                 'state': 'completed'
#             }
#         ]
#
#         expected_request_response = [
#             # Testing two possible cases, when it's running and when it's completed
#             {
#                 'created': expected_json_data[0]['created'],
#                 'has_results': expected_json_data[0]['has_results'],
#                 'id': expected_json_data[0]['id'],
#                 'name': 'Run With Parameters 0000000',
#                 'parameters': expected_json_data[0]['parameters'],
#                 'run_time': 95024,
#                 'state': 'running'
#             },
#             {
#                 'cloud_workstation': expected_json_data[1]['cloud_workstation'],
#                 'created': expected_json_data[1]['created'],
#                 'end_status': 'succeeded',
#                 'has_results': True,
#                 'id': expected_json_data[1]['id'],
#                 'name': expected_json_data[1]['name'],
#                 'run_time': expected_json_data[1]['run_time'],
#                 'state': 'completed'
#             }
#         ]
#
#         success_message = [
#             {
#                 'created': 1667400000,
#                 'has_results': True,
#                 'id': '8ae000de-02fa-47f8-9zzz-2bb8160003e4',
#                 'name': 'Run With Parameters 0000000',
#                 'parameters': [{'name': '--input_data', 'value': 'SmartSPIM_597305_2022-09-27_00-07-58'},
#                 {'name': 'bucket_path', 'value': 'aind-open-data'}],
#                 'run_time': 95024,
#                 'state': 'running'
#             },
#             {
#                 'cloud_workstation': True,
#                 'created': 1667330000,
#                 'end_status': 'succeeded',
#                 'has_results': True,
#                 'id': '6c64620d-czzz-4fe3-99f2-702ec560000',
#                 'name': 'Run With Parameters 6760910',
#                 'run_time': 1009,
#                 'state': 'completed'
#             }
#         ]
#
#         mock_api_call.return_value = self.mocked_request_get(
#             success_message
#         )
#         response = self.co_client.get_capsule_computations(
#             json_data=expected_json_data
#         )
#
#         self.assertListEqual(response.message, expected_request_response)
#         self.assertEqual(response.message, expected_request_response)
#         self.assertEqual(response.status_code, 200)
#
#     @mock.patch(
#         "aind_codeocean_api.CodeOceanCapsuleRequests.run_capsule"
#     )
#     def test_run_capsule(self, mock_api_call):
#         """Tests the response of running a capsule"""
#
#         expected_json_data = {
#             'created': 1667310000,
#             'has_results': False,
#             'id': 'e227d4fa-4zzz-4d34-b20c-8c037d9a0000',
#             'name': 'Run With Parameters 7318400',
#             'parameters': [
#                 {'name': '', 'value': 'SmartSPIM_623711_2022-10-27_16-48-54'},
#                 {'name': '', 'value': 'SmartSPIM_623711_2022-10-27_16-48-54'},
#                 {'name': '', 'value': 'aind-open-data'}
#             ],
#             'run_time': 1,
#             'state': 'initializing'
#         }
#
#         expected_request_response = {
#             'created': expected_json_data['created'],
#             'has_results': False,
#             'id': expected_json_data['id'],
#             'name': expected_json_data['name'],
#             'parameters': expected_json_data['parameters'],
#             'run_time': 1,
#             'state': 'initializing'
#         }
#
#         success_message = {
#             'created': expected_json_data['created'],
#             'has_results': False,
#             'id': expected_json_data['id'],
#             'name': expected_json_data['name'],
#             'parameters': expected_json_data['parameters'],
#             'run_time': 1,
#             'state': 'initializing'
#         }
#
#         mock_api_call.return_value = self.mocked_request_post(
#             success_message
#         )
#         response = self.co_client.run_capsule(
#             json_data=expected_json_data
#         )
#         self.assertEqual(response.message, expected_request_response)
#         self.assertEqual(response.status_code, 200)
#
#
# class TestCodeOceanComputationRequests(unittest.TestCase):
#     """Tests Data Computation Requests class methods"""
#
#     domain = "https://acmecorp.codeocean.com"
#     auth_token = "CODEOCEAN_API_TOKEN"
#
#     co_client = CodeOceanComputationRequests(domain, auth_token)
#
#     @staticmethod
#     def mocked_request_get(success_message: dict) -> MockResponse:
#         return MockResponse(status_code=200, message=success_message)
#
#     @staticmethod
#     def mocked_request_post(success_message: dict) -> MockResponse:
#         return MockResponse(status_code=200, message=success_message)
#
#     @mock.patch(
#         "aind_codeocean_api.CodeOceanComputationRequests.get_computation"
#     )
#     def test_get_computation(
#         self,
#         mock_api_call
#     ):
#         """Tests the response of get computation"""
#
#         expected_json_data = {
#             'created': 1667400000,
#             'has_results': False,
#             'id': '8ae93zzz-02fa-47f8-93b5-2bb81608000',
#             'name': 'Run With Parameters 7407003',
#             'parameters': [
#                 {'name': '--input_data', 'value': 'SmartSPIM_597305_2022-09-27_00-07-58'},
#                 {'name': 'bucket_path', 'value': 'aind-open-data'}
#             ],
#             'run_time': 98790,
#             'state': 'running'
#         }
#
#         expected_request_response = {
#             'created': expected_json_data['created'],
#             'has_results': False,
#             'id': expected_json_data['id'],
#             'name': expected_json_data['name'],
#             'parameters': expected_json_data['parameters'],
#             'run_time': expected_json_data['run_time'],
#             'state': 'running'
#         }
#
#         success_message = {
#             'created': expected_json_data['created'],
#             'has_results': False,
#             'id': expected_json_data['id'],
#             'name': expected_json_data['name'],
#             'parameters': expected_json_data['parameters'],
#             'run_time': expected_json_data['run_time'],
#             'state': 'running'
#         }
#
#         mock_api_call.return_value = self.mocked_request_get(
#             success_message
#         )
#         response = self.co_client.get_computation(
#             json_data=expected_json_data
#         )
#         self.assertEqual(response.message, expected_request_response)
#         self.assertEqual(response.status_code, 200)
#
#     @mock.patch(
#         "aind_codeocean_api.CodeOceanComputationRequests.get_list_result_items"
#     )
#     def test_get_list_result_items(self, mock_api_call):
#         """Tests the response of getting list of computed items"""
#
#         expected_json_data = {
#             'items': [
#                 {'name': 'buildLog', 'path': 'buildLog', 'size': 2225086, 'type': 'file'},
#                 {'name': 'output', 'path': 'output', 'size': 2225086, 'type': 'file'}
#             ]
#         }
#
#         success_message = {
#             'items': expected_json_data['items']
#         }
#
#         mock_api_call.return_value = self.mocked_request_get(
#             success_message
#         )
#         response = self.co_client.get_list_result_items(
#             json_data=expected_json_data
#         )
#
#         self.assertEqual(response.message, expected_json_data)
#         self.assertEqual(response.status_code, 200)
#
#     @mock.patch(
#         "aind_codeocean_api.CodeOceanComputationRequests.get_result_file_download_url"
#     )
#     def test_get_result_file_download_url(self, mock_api_call):
#         """Tests the response of get a result file download url"""
#
#         expected_json_data = {
#             'url': 'https://s3.us-west-2.amazonaws.com/codeocean-s3resultsbucket-1182nktl2bh9f/b7c3e431-dd26-49ab-a101-200a3011aded/9b41eecc-8f0a-4f5f-ada7-2e62d6858a63/8ae936de-02fa-47f8-93b5-2bb8160843e4/buildLog?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAWZ4O6ZMIFJ6D3OGL%2F20221103%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20221103T201124Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjENf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJGMEQCIE6zy2qP2zdgbNR14eJilVQr3IZe7i7P28esDAfJfudLAiAhcczeGeO%2B2Oi5pb9JVX1GTfEyhTeyQ9BGnS%2Fd%2FkzueirVBAjA%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAAaDDQ2NzkxNDM3ODAwMCIMncKIcF7VnLkGVvIZKqkEsZ%2BN%2BM%2BcDtgpFlU8cgSHcSuB33PoWcI3IPMUCaI9MdQwZaSQy0eBF3sSZK6T7HXsGFxGPfzVs0E9XRQ1nnP59mVNaQcDE%2BUj1jMLMgDPBJHCtvSKepYIuXZ9xUuHbd80gjLOkG9X%2FETRKCvBzE2K3%2ByF6JYCmkORuPaPN%2FiYznv9FgnXHVnMtnfNRNKLrkG717HtxrM1QqvjRSNza1gfbeN8o6ZHk%2FotmCkhAS2i5Qpb8WsbOmcTIbvW0K5s4AdmCMxzpCjJUcbs0VZAMfNPyKlK1W4Ar%2F44%2Fu7NVId1O%2BZlAFm9vR4ZcfcKLN3gSsltdBvV2FJ%2BfW4cAQ6%2FAZ4g9duPL42ZU%2BwAuH77uSnaU1YvksIDeiVEMg71Cfrtsb6SlOTE8u3aIg6NJ01jHYo2cMlJUb%2FrE5%2BF8ejiH1BsGEoku2076KOpJkDakh%2Fy8DMx1cohiJMqYn9r%2F8gN4juHhov2%2Bxf9NdxR%2FPkJxN1HTlX%2FM5jrX1apTZujXBgtfXM%2FiLQw0oUCFue4Rbemgdw%2FYk4j3qtRA3tOhLsyHoAsrstOMDS7wdHKYdnHcP4ScbsrkfgYwAKaTkhrsyMjpkrz5HRE8TG3mjWY8xWY3f3ZfwEfzzRnQvnsx91WYDa5EKS7%2BYUa4IiYtE7wK28qYB4CvwtMBpeYEEf4iRLyt9cSgj9tInbHyQdc96yblnsgWUU2eTGl4JWMFU8oE20hsNxEZbHoM%2F7Cgz59MDDOrY%2BbBjqqAVr%2FPW4msnwt17w3vZPGh0PvHpqIDLtGUWpnOQrPPRU%2BaXOv4uxxLmnm0A2brxzBOonOVrbY6VpqRdAw03Yqz9kTyrApe9w77Z9ayC8JWUMdqe3Dq0dPDyaintut9ZxUjmPJr205Ity0m3EIUjwk5UrSuHdbaZIDjBHUKeFHZeClaeuxidIHVaXbsb9Te51J27j1J%2Fcpunw9M7pip1qg47QVdoE0foBOgw%2Fs&X-Amz-SignedHeaders=host&response-content-disposition=attachment%3B%20filename%3DbuildLog&X-Amz-Signature=920bb69265bceb0e272b062c65c4dbff0b000f7df9b38166b072fbee662b294a'
#         }
#
#         success_message = {
#             'url': expected_json_data['url']
#         }
#
#         mock_api_call.return_value = self.mocked_request_post(
#             success_message
#         )
#         response = self.co_client.get_result_file_download_url(
#             json_data=expected_json_data
#         )
#         self.assertEqual(response.message, expected_json_data)
#         self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
