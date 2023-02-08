"""Create CodeOceanCredentials from AWS Secrets Manager."""
import json
import os
from pathlib import Path

import boto3
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig
from botocore.exceptions import ClientError

import aind_codeocean_api.credentials as co_credentials

AWS_ROLE_ARN = "arn:aws:iam::467914378000:role/codeocean-secret-retriever"


def _get_secrets_cache_client(credentials: dict = None):
    """
    Get a boto3 client for AWS Secrets Manager,
    using SecretCache to improve performance.
    """
    if credentials is None:
        credentials = _get_credentials()
    session = boto3.session.Session(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
    )
    client = session.client(
        service_name="secretsmanager",
        region_name=os.environ.get("AWS_REGION", "us-west-2"),
    )
    cache_config = SecretCacheConfig()
    cache = SecretCache(
        config = cache_config,
        client = client,
    )
    return cache


def _get_credentials(aws_role_arn: str = AWS_ROLE_ARN):
    """
    Get credentials for the given AWS role.
    The environment must be authorized to AWS.
    """
    credentials = None
    try:
        assumed_role_object = boto3.client("sts").assume_role(
            RoleArn=aws_role_arn,
            RoleSessionName="AssumeCodeoceanRoleSession",
        )
    except ClientError as e:
        print("Error assuming role:", e)
        raise
    else:
        credentials=assumed_role_object['Credentials']
        return credentials


def _get_secret(secret_name: str, credentials: dict = None) -> str:
    """Get secret from AWS Secrets Manager."""
    secret = None
    cache = _get_secrets_cache_client(credentials)

    try:
        secret = cache.get_secret_string(
            secret_id=secret_name
        )
    except ClientError as e:
        print("Error retrieving secret:", e)
        raise
    else:
        return secret


def create_credentials_from_aws_secrets_manager(
    secret_name: str = "codeocean-service-account",
    file_location: str = None,
) -> None:
    """Create CodeOceanCredentials from AWS Secrets Manager."""
    if file_location is None:
        file_location = str(co_credentials.DEFAULT_HOME_PATH)

    Path(file_location).parent.mkdir(exist_ok=True, parents=True)

    secret = _get_secret(secret_name)
    secret_dict = json.loads(secret)
    co_credentials.CodeOceanCredentials.create_credentials(
        api_domain=secret_dict["domain"],
        access_token=secret_dict["token"],
        file_location=file_location
    )
