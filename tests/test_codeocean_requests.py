"""Tests CodeOcean API python interface"""
import unittest
from unittest import mock
from code_ocean_api import CodeOceanDataAssetRequests, CodeOceanCapsuleRequests, CodeOceanComputationRequests

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

    @mock.patch(
        "code_ocean_api.CodeOceanDataAssetRequests.register_data_asset"
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

class MockResponse:
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code

class TestCodeOceanCapsuleRequests(unittest.TestCase):
    """Tests Data Capsule Requests class methods"""

    domain = "https://acmecorp.codeocean.com"
    auth_token = "CODEOCEAN_API_TOKEN"

    co_client = CodeOceanCapsuleRequests(domain, auth_token)

    @staticmethod
    def mocked_request_get(success_message: dict) -> MockResponse:
        return MockResponse(status_code=200, message=success_message)

    @staticmethod
    def mocked_request_post(success_message: dict) -> MockResponse:
        return MockResponse(status_code=200, message=success_message)

    @mock.patch(
        "code_ocean_api.CodeOceanCapsuleRequests.get_capsule"
    )
    def test_get_capsule(self, mock_api_call):
        """Tests the response of get capsule"""

        expected_json_data = {
            'cloned_from_url': 'https://github.com/AllenNeuralDynamics/terastitcher-module.git', 
            'created': 1665287322, 
            'description': 'A tool for fast automatic 3D-stitching of teravoxel-sized microscopy images using cloud computing resources and TeraStitcher.', 
            'field': '', 
            'id': '9b41eecc-8qz2-4f5f-ada7-2e62d0008a63', 
            'keywords': None, 
            'name': 'TeraStitcher Module', 
            'owner': 'c3c3ezz1-dd26-49ab-a101-200a3011aded', 
            'published_capsule': '', 
            'slug': '0000000', 
            'status': 'non-published'
        }

        expected_request_response = {
            'cloned_from_url': expected_json_data['cloned_from_url'], 
            "created": expected_json_data['created'],
            "description": expected_json_data["description"],
            "field": '',
            "id": "9b41eecc-8qz2-4f5f-ada7-2e62d0008a63",
            'keywords': None, 
            "name": expected_json_data["name"],
            'owner': expected_json_data['owner'], 
            'published_capsule': '', 
            'slug': '0000000', 
            'status': 'non-published'
        }

        success_message = {
            'cloned_from_url': expected_json_data['cloned_from_url'], 
            'created': expected_json_data['created'], 
            'description': expected_json_data['description'],
            'field': '', 
            'id': '9b41eecc-8qz2-4f5f-ada7-2e62d0008a63', 
            'keywords': None, 
            'name': expected_json_data['name'], 
            'owner': 'c3c3ezz1-dd26-49ab-a101-200a3011aded', 
            'published_capsule': '', 
            'slug': '0000000', 
            'status': 'non-published'
        }

        mock_api_call.return_value = self.mocked_request_get(
            success_message
        )
        response = self.co_client.get_capsule(
            json_data=expected_json_data
        )
        self.assertEqual(response.message, expected_request_response)
        self.assertEqual(response.status_code, 200)

    @mock.patch(
        "code_ocean_api.CodeOceanCapsuleRequests.get_capsule_computations"
    )
    def test_get_capsule_computations(self, mock_api_call):
        """Tests the response of getting list of computations"""

        expected_json_data = [
            # Testing two possible cases, when it's running and when it's completed
            {
                'created': 1667400000, 
                'has_results': True, 
                'id': '8ae000de-02fa-47f8-9zzz-2bb8160003e4', 
                'name': 'Run With Parameters 0000000', 
                'parameters': [{'name': '--input_data', 'value': 'SmartSPIM_597305_2022-09-27_00-07-58'}, 
                {'name': 'bucket_path', 'value': 'aind-open-data'}], 
                'run_time': 95024, 
                'state': 'running'
            },
            {
                'cloud_workstation': True, 
                'created': 1667330000, 
                'end_status': 'succeeded', 
                'has_results': True, 
                'id': '6c64620d-czzz-4fe3-99f2-702ec560000', 
                'name': 'Run With Parameters 6760910', 
                'run_time': 1009, 
                'state': 'completed'
            }
        ]

        expected_request_response = [
            # Testing two possible cases, when it's running and when it's completed
            {
                'created': expected_json_data[0]['created'], 
                'has_results': expected_json_data[0]['has_results'], 
                'id': expected_json_data[0]['id'], 
                'name': 'Run With Parameters 0000000', 
                'parameters': expected_json_data[0]['parameters'], 
                'run_time': 95024, 
                'state': 'running'
            },
            {
                'cloud_workstation': expected_json_data[1]['cloud_workstation'], 
                'created': expected_json_data[1]['created'], 
                'end_status': 'succeeded', 
                'has_results': True, 
                'id': expected_json_data[1]['id'], 
                'name': expected_json_data[1]['name'], 
                'run_time': expected_json_data[1]['run_time'], 
                'state': 'completed'
            }
        ]

        success_message = [
            {
                'created': 1667400000, 
                'has_results': True, 
                'id': '8ae000de-02fa-47f8-9zzz-2bb8160003e4', 
                'name': 'Run With Parameters 0000000', 
                'parameters': [{'name': '--input_data', 'value': 'SmartSPIM_597305_2022-09-27_00-07-58'}, 
                {'name': 'bucket_path', 'value': 'aind-open-data'}], 
                'run_time': 95024, 
                'state': 'running'
            },
            {
                'cloud_workstation': True, 
                'created': 1667330000, 
                'end_status': 'succeeded', 
                'has_results': True, 
                'id': '6c64620d-czzz-4fe3-99f2-702ec560000', 
                'name': 'Run With Parameters 6760910', 
                'run_time': 1009, 
                'state': 'completed'
            }
        ]

        mock_api_call.return_value = self.mocked_request_get(
            success_message
        )
        response = self.co_client.get_capsule_computations(
            json_data=expected_json_data
        )

        self.assertListEqual(response.message, expected_request_response)
        self.assertEqual(response.message, expected_request_response)
        self.assertEqual(response.status_code, 200)

    @mock.patch(
        "code_ocean_api.CodeOceanCapsuleRequests.run_capsule"
    )
    def test_run_capsule(self, mock_api_call):
        """Tests the response of running a capsule"""

        expected_json_data = {
            'created': 1667310000, 
            'has_results': False, 
            'id': 'e227d4fa-4zzz-4d34-b20c-8c037d9a0000', 
            'name': 'Run With Parameters 7318400', 
            'parameters': [
                {'name': '', 'value': 'SmartSPIM_623711_2022-10-27_16-48-54'}, 
                {'name': '', 'value': 'SmartSPIM_623711_2022-10-27_16-48-54'}, 
                {'name': '', 'value': 'aind-open-data'}
            ], 
            'run_time': 1, 
            'state': 'initializing'
        }

        expected_request_response = {
            'created': expected_json_data['created'], 
            'has_results': False, 
            'id': expected_json_data['id'], 
            'name': expected_json_data['name'], 
            'parameters': expected_json_data['parameters'], 
            'run_time': 1, 
            'state': 'initializing'
        }

        success_message = {
            'created': expected_json_data['created'], 
            'has_results': False, 
            'id': expected_json_data['id'], 
            'name': expected_json_data['name'], 
            'parameters': expected_json_data['parameters'], 
            'run_time': 1, 
            'state': 'initializing'
        }

        mock_api_call.return_value = self.mocked_request_post(
            success_message
        )
        response = self.co_client.run_capsule(
            json_data=expected_json_data
        )
        self.assertEqual(response.message, expected_request_response)
        self.assertEqual(response.status_code, 200)


class TestCodeOceanComputationRequests(unittest.TestCase):
    """Tests Data Computation Requests class methods"""

    domain = "https://acmecorp.codeocean.com"
    auth_token = "CODEOCEAN_API_TOKEN"

    co_client = CodeOceanComputationRequests(domain, auth_token)

    @staticmethod
    def mocked_request_get(success_message: dict) -> MockResponse:
        return MockResponse(status_code=200, message=success_message)

    @staticmethod
    def mocked_request_post(success_message: dict) -> MockResponse:
        return MockResponse(status_code=200, message=success_message)

    @mock.patch(
        "code_ocean_api.CodeOceanComputationRequests.get_computation"
    )
    def test_get_computation(
        self, 
        mock_api_call
    ):
        """Tests the response of get computation"""

        expected_json_data = {
            'created': 1667400000, 
            'has_results': False, 
            'id': '8ae93zzz-02fa-47f8-93b5-2bb81608000', 
            'name': 'Run With Parameters 7407003', 
            'parameters': [
                {'name': '--input_data', 'value': 'SmartSPIM_597305_2022-09-27_00-07-58'}, 
                {'name': 'bucket_path', 'value': 'aind-open-data'}
            ], 
            'run_time': 98790, 
            'state': 'running'
        }
        
        expected_request_response = {
            'created': expected_json_data['created'], 
            'has_results': False, 
            'id': expected_json_data['id'], 
            'name': expected_json_data['name'], 
            'parameters': expected_json_data['parameters'], 
            'run_time': expected_json_data['run_time'], 
            'state': 'running'
        }

        success_message = {
            'created': expected_json_data['created'], 
            'has_results': False, 
            'id': expected_json_data['id'], 
            'name': expected_json_data['name'], 
            'parameters': expected_json_data['parameters'], 
            'run_time': expected_json_data['run_time'], 
            'state': 'running'
        }

        mock_api_call.return_value = self.mocked_request_get(
            success_message
        )
        response = self.co_client.get_computation(
            json_data=expected_json_data
        )
        self.assertEqual(response.message, expected_request_response)
        self.assertEqual(response.status_code, 200)

    @mock.patch(
        "code_ocean_api.CodeOceanComputationRequests.get_list_result_items"
    )
    def test_get_list_result_items(self, mock_api_call):
        """Tests the response of getting list of computed items"""

        expected_json_data = {
            'items': [
                {'name': 'buildLog', 'path': 'buildLog', 'size': 2225086, 'type': 'file'},
                {'name': 'output', 'path': 'output', 'size': 2225086, 'type': 'file'}
            ]
        }

        success_message = {
            'items': expected_json_data['items']
        }

        mock_api_call.return_value = self.mocked_request_get(
            success_message
        )
        response = self.co_client.get_list_result_items(
            json_data=expected_json_data
        )

        self.assertEqual(response.message, expected_json_data)
        self.assertEqual(response.status_code, 200)

    @mock.patch(
        "code_ocean_api.CodeOceanComputationRequests.get_result_file_download_url"
    )
    def test_get_result_file_download_url(self, mock_api_call):
        """Tests the response of get a result file download url"""

        expected_json_data = {
            'url': 'https://s3.us-west-2.amazonaws.com/codeocean-s3resultsbucket-1182nktl2bh9f/b7c3e431-dd26-49ab-a101-200a3011aded/9b41eecc-8f0a-4f5f-ada7-2e62d6858a63/8ae936de-02fa-47f8-93b5-2bb8160843e4/buildLog?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAWZ4O6ZMIFJ6D3OGL%2F20221103%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20221103T201124Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjENf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJGMEQCIE6zy2qP2zdgbNR14eJilVQr3IZe7i7P28esDAfJfudLAiAhcczeGeO%2B2Oi5pb9JVX1GTfEyhTeyQ9BGnS%2Fd%2FkzueirVBAjA%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAAaDDQ2NzkxNDM3ODAwMCIMncKIcF7VnLkGVvIZKqkEsZ%2BN%2BM%2BcDtgpFlU8cgSHcSuB33PoWcI3IPMUCaI9MdQwZaSQy0eBF3sSZK6T7HXsGFxGPfzVs0E9XRQ1nnP59mVNaQcDE%2BUj1jMLMgDPBJHCtvSKepYIuXZ9xUuHbd80gjLOkG9X%2FETRKCvBzE2K3%2ByF6JYCmkORuPaPN%2FiYznv9FgnXHVnMtnfNRNKLrkG717HtxrM1QqvjRSNza1gfbeN8o6ZHk%2FotmCkhAS2i5Qpb8WsbOmcTIbvW0K5s4AdmCMxzpCjJUcbs0VZAMfNPyKlK1W4Ar%2F44%2Fu7NVId1O%2BZlAFm9vR4ZcfcKLN3gSsltdBvV2FJ%2BfW4cAQ6%2FAZ4g9duPL42ZU%2BwAuH77uSnaU1YvksIDeiVEMg71Cfrtsb6SlOTE8u3aIg6NJ01jHYo2cMlJUb%2FrE5%2BF8ejiH1BsGEoku2076KOpJkDakh%2Fy8DMx1cohiJMqYn9r%2F8gN4juHhov2%2Bxf9NdxR%2FPkJxN1HTlX%2FM5jrX1apTZujXBgtfXM%2FiLQw0oUCFue4Rbemgdw%2FYk4j3qtRA3tOhLsyHoAsrstOMDS7wdHKYdnHcP4ScbsrkfgYwAKaTkhrsyMjpkrz5HRE8TG3mjWY8xWY3f3ZfwEfzzRnQvnsx91WYDa5EKS7%2BYUa4IiYtE7wK28qYB4CvwtMBpeYEEf4iRLyt9cSgj9tInbHyQdc96yblnsgWUU2eTGl4JWMFU8oE20hsNxEZbHoM%2F7Cgz59MDDOrY%2BbBjqqAVr%2FPW4msnwt17w3vZPGh0PvHpqIDLtGUWpnOQrPPRU%2BaXOv4uxxLmnm0A2brxzBOonOVrbY6VpqRdAw03Yqz9kTyrApe9w77Z9ayC8JWUMdqe3Dq0dPDyaintut9ZxUjmPJr205Ity0m3EIUjwk5UrSuHdbaZIDjBHUKeFHZeClaeuxidIHVaXbsb9Te51J27j1J%2Fcpunw9M7pip1qg47QVdoE0foBOgw%2Fs&X-Amz-SignedHeaders=host&response-content-disposition=attachment%3B%20filename%3DbuildLog&X-Amz-Signature=920bb69265bceb0e272b062c65c4dbff0b000f7df9b38166b072fbee662b294a'
        }

        success_message = {
            'url': expected_json_data['url']
        }

        mock_api_call.return_value = self.mocked_request_post(
            success_message
        )
        response = self.co_client.get_result_file_download_url(
            json_data=expected_json_data
        )
        self.assertEqual(response.message, expected_json_data)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
