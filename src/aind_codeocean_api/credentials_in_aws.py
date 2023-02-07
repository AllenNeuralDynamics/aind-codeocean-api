"""Create CodeOceanCredentials from AWS Secrets Manager."""
import base64
import json
import os
from pathlib import Path

import boto3
import botocore.session 
from botocore.exceptions import ClientError
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig

import aind_codeocean_api.credentials as credentials


def _get_secret(secret_name: str) -> str:
    """Get secret from AWS Secrets Manager."""
    # session = boto3.session.Session()
    # client = session.client(
    #     service_name="secretsmanager",
    #     region_name=os.environ.get("AWS_REGION", "us-west-2"),
    # )

    client = botocore.session.get_session().create_client('secretsmanager')
    cache_config = SecretCacheConfig()
    cache = SecretCache( config = cache_config, client = client)

    try:
        get_secret_string_response = cache.get_secret_string(
            secret_id=secret_name
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "DecryptionFailure":
            print("Can't decrypt the secret text using the provided key:", e)
        elif e.response["Error"]["Code"] == "InternalServiceError":
            print("An error occurred on the server:", e)
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            print("The request had invalid parameters:", e)
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            print("The request was invalid due to:", e)
        elif e.response["Error"]["Code"] == "ResourceNotFoundException":
            print("Secret named '" + secret_name + "' not found")
        # raise e
    else:
        print("Secret '" + secret_name + "' found")
        print("Response: " + get_secret_string_response)
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if "SecretString" in get_secret_string_response:
            secret = get_secret_string_response["SecretString"]
        else:
            secret = base64.b64decode(get_secret_string_response["SecretBinary"])
    
    return secret


def create_credentials_from_aws_secrets_manager(
    secret_name: str,
    file_location: str = None,
) -> None:
    """Create CodeOceanCredentials from AWS Secrets Manager."""
    if file_location is None:
        file_location = str(credentials.DEFAULT_HOME_PATH)
    else:
        file_location = os.path.join(file_location, credentials.CREDENTIALS_FILENAME)

    Path(file_location).parent.mkdir(exist_ok=True, parents=True)

    secret = _get_secret(secret_name)
    secret_dict = json.loads(secret)
    credentials.CodeOceanCredentials.create_credentials(
        secret_dict["api_domain"],
        secret_dict["access_token"],
        file_location,
    )
