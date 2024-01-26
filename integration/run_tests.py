"""Script that will run a basic set of api calls to test that they work after
 a version upgrade. To use, set the environment variables listed below and run:
 python run_tests.py
 """

import os
from datetime import datetime

from dotenv import load_dotenv

from aind_codeocean_api.codeocean import CodeOceanClient
from aind_codeocean_api.models.computations_requests import (
    ComputationDataAsset,
    RunCapsuleRequest,
)
from aind_codeocean_api.models.data_assets_requests import (
    CreateDataAssetRequest,
    Source,
    Sources,
)

# Create a .env file in the integration directory using the .env.template

load_dotenv()

TOKEN = os.getenv("CODEOCEAN_TOKEN")
DOMAIN = os.getenv("CODEOCEAN_DOMAIN")
TEST_CAPSULE_ID = os.getenv("TEST_CAPSULE_ID")
TEST_DATA_ASSET_BUCKET_PRIVATE = os.getenv("TEST_DATA_ASSET_BUCKET_PRIVATE")
TEST_DATA_ASSET_PREFIX_PRIVATE = os.getenv("TEST_DATA_ASSET_PREFIX_PRIVATE")
TEST_DATA_ASSET_BUCKET_PUBLIC = os.getenv("TEST_DATA_ASSET_BUCKET_PUBLIC")
TEST_DATA_ASSET_PREFIX_PUBLIC = os.getenv("TEST_DATA_ASSET_PREFIX_PUBLIC")


def _check_status_code(response, api_call: str, expected_status_code: int):
    """Helper function to test whether the status code is 200 or 204"""
    if expected_status_code == 200 and response.status_code != 200:
        raise AssertionError(
            f"{api_call} failed!"
            f" Expected: 200."
            f" Received: {response.status_code}."
            f" Response: {response.json()}"
        )
    elif expected_status_code == 204 and response.status_code != 204:
        raise AssertionError(
            f"{api_call} failed!"
            f" Expected: 204."
            f" Received: {response.status_code}."
        )
    else:
        pass


def test_search_data_asset(co_client: CodeOceanClient):
    """Tests the search_data_assets api call"""
    response = co_client.search_data_assets(limit=10)
    _check_status_code(
        response=response,
        api_call="search_data_assets",
        expected_status_code=200,
    )
    return response


def test_register_private_data_asset(co_client: CodeOceanClient):
    """Tests the create_data_asset api call with a private asset"""
    utcnow_str = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%SZ")
    asset_name = (
        f"asset_generated_from_test_register_private_data_asset_{utcnow_str}"
    )
    mount = TEST_DATA_ASSET_PREFIX_PRIVATE
    bucket = TEST_DATA_ASSET_BUCKET_PRIVATE
    prefix = TEST_DATA_ASSET_PREFIX_PRIVATE
    tags = ["test", "private_bucket"]
    aws_source = Sources.AWS(
        bucket=bucket,
        prefix=prefix,
        keep_on_external_storage=True,
        public=False,
    )
    source = Source(aws=aws_source)
    create_data_asset_request = CreateDataAssetRequest(
        name=asset_name,
        tags=tags,
        mount=mount,
        source=source,
    )
    response = co_client.create_data_asset(request=create_data_asset_request)
    _check_status_code(
        response=response,
        api_call="create_data_asset (private)",
        expected_status_code=200,
    )
    return response


def test_register_public_data_asset(co_client: CodeOceanClient):
    """Tests the create_data_asset api call with a public asset"""
    utcnow_str = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%SZ")
    asset_name = (
        f"asset_generated_from_test_register_public_data_asset_{utcnow_str}"
    )
    mount = TEST_DATA_ASSET_PREFIX_PUBLIC
    bucket = TEST_DATA_ASSET_BUCKET_PUBLIC
    prefix = TEST_DATA_ASSET_PREFIX_PUBLIC
    tags = ["test", "public_bucket"]
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
    )
    response = co_client.create_data_asset(request=create_data_asset_request)
    _check_status_code(
        response=response,
        api_call="create_data_asset (public)",
        expected_status_code=200,
    )
    return response


def test_update_private_data_asset_permissions(
    co_client: CodeOceanClient, data_asset_id
):
    """Tests the update_permissions api call in a private asset"""
    response = co_client.update_permissions(
        data_asset_id=data_asset_id, everyone="viewer"
    )
    _check_status_code(
        response=response,
        api_call="update_permissions (private)",
        expected_status_code=204,
    )
    return response


def test_update_public_data_asset_permissions(
    co_client: CodeOceanClient, data_asset_id
):
    """Tests the update_permissions api call in a public asset"""
    response = co_client.update_permissions(
        data_asset_id=data_asset_id, everyone="viewer"
    )
    _check_status_code(
        response=response,
        api_call="update_permissions (public)",
        expected_status_code=204,
    )
    return response


def test_run_capsule(co_client: CodeOceanClient, data_asset_id, mount):
    """Tests the run_capsule api call"""
    capsule_id = TEST_CAPSULE_ID
    data_assets = [ComputationDataAsset(id=data_asset_id, mount=mount)]
    run_capsule_request = RunCapsuleRequest(
        capsule_id=capsule_id, data_assets=data_assets
    )
    response = co_client.run_capsule(request=run_capsule_request)
    _check_status_code(
        response=response, api_call="run_capsule", expected_status_code=200
    )
    return response


def run_tests():
    """Run all api call tests and print responses"""
    co_client = CodeOceanClient(domain=DOMAIN, token=TOKEN)
    search_data_asset_response = test_search_data_asset(co_client=co_client)
    print(search_data_asset_response.json())
    register_private_data_asset_response = test_register_private_data_asset(
        co_client=co_client
    )
    print(register_private_data_asset_response.json())
    private_data_asset_id = register_private_data_asset_response.json()["id"]
    register_public_data_asset_response = test_register_public_data_asset(
        co_client=co_client
    )
    print(register_public_data_asset_response.json())
    public_data_asset_id = register_public_data_asset_response.json()["id"]
    update_private_permissions_response = (
        test_update_private_data_asset_permissions(
            co_client=co_client, data_asset_id=private_data_asset_id
        )
    )
    print(update_private_permissions_response)
    update_public_permissions_response = (
        test_update_public_data_asset_permissions(
            co_client=co_client, data_asset_id=public_data_asset_id
        )
    )
    print(update_public_permissions_response)
    test_run_capsule_response = test_run_capsule(
        co_client=co_client,
        data_asset_id=private_data_asset_id,
        mount=TEST_DATA_ASSET_PREFIX_PRIVATE,
    )
    print(test_run_capsule_response)
    return None


if __name__ == "__main__":
    print("STARTING TESTS")
    run_tests()
    print("FINISHED TESTS")
