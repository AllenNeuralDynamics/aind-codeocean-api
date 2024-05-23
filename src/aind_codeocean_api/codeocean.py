"""Module to interface with Code Ocean's backend.
"""

import json
import logging
from enum import Enum
from inspect import signature
from time import sleep
from typing import Dict, List, Optional, Union

import requests

from aind_codeocean_api.credentials import CodeOceanCredentials
from aind_codeocean_api.models.computations_requests import RunCapsuleRequest
from aind_codeocean_api.models.data_assets_requests import (
    CreateDataAssetRequest,
)


class CodeOceanClient:
    """Client that will connect to Code Ocean"""

    _MAX_SEARCH_BATCH_REQUEST = 1000

    class _URLStrings(Enum):
        """Enum class for CodeOcean's url strings"""

        ARCHIVE = "archive"
        CAPSULES = "capsules"
        COMPUTATIONS = "computations"
        DATA_ASSETS = "data_assets"
        PERMISSIONS = "permissions"
        RESULTS = "results"

    class _Fields(Enum):
        """Enum class for CodeOcean's API fields"""

        ACCESS_KEY_ID = "access_key_id"
        AWS = "aws"
        BUCKET = "bucket"
        CAPSULE_ID = "capsule_id"
        COMPUTATION = "computation"
        CUSTOM_METADATA = "custom_metadata"
        DATA_ASSETS = "data_assets"
        DESCRIPTION = "description"
        EVERYONE = "everyone"
        GROUPS = "groups"
        HAS_MORE = "has_more"
        ID = "id"
        INDEX_DATA = "index_data"
        KEEP_ON_EXTERNAL_STORAGE = "keep_on_external_storage"
        LIMIT = "limit"
        MOUNT = "mount"
        NAME = "name"
        PARAMETERS = "parameters"
        PREFIX = "prefix"
        RESULTS = "results"
        SECRET_ACCESS_KEY = "secret_access_key"
        START = "start"
        SOURCE = "source"
        TAGS = "tags"
        USERS = "users"
        VERSION = "version"

    def __init__(self, domain: str, token: str, api_version: int = 1) -> None:
        """
        Base client for Code Ocean's API
        Parameters
        ----------
        domain : str
            VPC domain
        token : str
            API token
        api_version : int
            Code Ocean API version
        """
        self.domain = domain.strip("/")
        self.token = token
        self.api_version = api_version
        self.logger = logging.getLogger("aind-codeocean-api")

    @property
    def asset_url(self):
        """Asset url property."""
        return (
            f"{self.domain}/api/v{self.api_version}/"
            f"{self._URLStrings.DATA_ASSETS.value}"
        )

    @property
    def capsule_url(self):
        """Capsule url property."""
        return (
            f"{self.domain}/api/v{self.api_version}/"
            f"{self._URLStrings.CAPSULES.value}"
        )

    @property
    def computation_url(self):
        """Computation url property."""
        return (
            f"{self.domain}/api/v{self.api_version}/"
            f"{self._URLStrings.COMPUTATIONS.value}"
        )

    @classmethod
    def from_credentials(
        cls, credentials: CodeOceanCredentials, api_version: int = 1
    ):
        """
        Create client using credentials object.
        Parameters
        ----------
        credentials : CodeOceanCredentials
        api_version :
          Code Ocean API version

        """
        domain = credentials.domain
        token = credentials.token.get_secret_value()
        return cls(domain=domain, token=token, api_version=api_version)

    def get_data_asset(self, data_asset_id: str) -> requests.models.Response:
        """
        This will get data from a GET request to Code Ocean API.

        Parameters
        ---------------
        data_asset_id : string
            ID of the data asset

        Returns
        ---------------
        requests.models.Response
        """

        url = f"{self.asset_url}/{data_asset_id}"
        response = requests.get(url, auth=(self.token, ""))

        self.logger.info(response.url)

        return response

    def search_data_assets(
        self,
        start: Optional[int] = None,
        limit: Optional[int] = None,
        sort_order: Optional[str] = None,
        sort_field: Optional[str] = None,
        type: Optional[str] = None,
        ownership: Optional[str] = None,
        favorite: Optional[bool] = None,
        archived: Optional[bool] = None,
        query: Optional[str] = None,
    ) -> requests.models.Response:
        """
        This will return data assets from a GET request to Code Ocean API.

        Parameters
        ---------------
        start : Optional[int]
            Describes the search from index.
        limit : Optional[int]
            Describes the upper limit to search.
        sort_order : Optional[str]
            Determines the result sort order.
        sort_field : Optional[str]
            Determines the field to sort by.
        type : Optional[str]
            Type of data asset: dataset or result.
            Returns both if omitted.
        ownership : Optional[str]
            Search data asset by ownership: owner or shared.
        favorite : Optional[bool]
            Search only favorite data assets.
        archived : Optional[bool]
            Search only archived data assets.
        query : Optional[str]
            Determines the search query.

        Returns
        ---------------
        requests.models.Response
        """
        frame_locals = locals()
        query_params = dict(
            [
                (k, frame_locals[k])
                for k, v in signature(
                    self.search_data_assets
                ).parameters.items()
                if frame_locals[k] is not None
            ]
        )

        response = requests.get(
            self.asset_url, params=query_params, auth=(self.token, "")
        )

        self.logger.info(response.url)

        return response

    def _paginate_data_assets(
        self,
        sort_order: Optional[str] = None,
        sort_field: Optional[str] = None,
        type: Optional[str] = None,
        ownership: Optional[str] = None,
        favorite: Optional[bool] = None,
        archived: Optional[bool] = None,
        query: Optional[str] = None,
    ):
        """
        Utility method to paginate through search results returned by search
        Parameters
        ----------
        sort_order : Optional[str]
            Determines the result sort order.
        sort_field : Optional[str]
            Determines the field to sort by.
        type : Optional[str]
            Type of data asset: dataset or result.
            Returns both if omitted.
        ownership : Optional[str]
            Search data asset by ownership: owner or shared.
        favorite : Optional[bool]
            Search only favorite data assets.
        archived : Optional[bool]
            Search only archived data assets.
        query : Optional[str]
            Determines the search query.

        Returns
        -------
        Iterator[List[dict]]
        """

        frame_locals = locals()
        query_params = dict(
            [
                (k, frame_locals[k])
                for k, v in signature(
                    self.search_all_data_assets
                ).parameters.items()
                if frame_locals[k] is not None
            ]
        )

        def get_page(
            r: requests.Session,
            qp: dict,
            max_retries: int = 3,
        ) -> dict:
            """
            Get a single list of results back from Code Ocean. It will retry
            a request up to the max amount of retries. It will wait
            min(retry_count**2, 15) seconds.
            Parameters
            ----------
            r : requests.Session
            qp : dict
              query parameters
            max_retries : int
              Max number of retries before raising an error

            Returns
            -------
            dict
              Response from Code Ocean
            """
            rsp = r.get(self.asset_url, params=qp, auth=(self.token, ""))
            if rsp.status_code == 200:
                return rsp.json()
            else:
                retry = 1
                while retry <= max_retries and rsp.status_code != 200:
                    logging.debug(
                        f"Backing off and retrying: {retry}. "
                        f"Reason: {rsp.status_code}"
                    )
                    sleep(min(retry**2, 15))
                    retry += 1
                    rsp = r.get(
                        self.asset_url, params=qp, auth=(self.token, "")
                    )
                if rsp.status_code == 200:
                    return rsp.json()
                else:
                    raise ConnectionError(
                        f"There was an error getting data from Code Ocean: "
                        f"{rsp.status_code}"
                    )

        with requests.Session() as requests_session:
            has_more = True
            status_code = 200
            start_index = 0
            limit = self._MAX_SEARCH_BATCH_REQUEST
            while has_more:
                query_params[self._Fields.START.value] = start_index
                query_params[self._Fields.LIMIT.value] = limit
                page = get_page(requests_session, query_params)
                has_more = page.get(self._Fields.HAS_MORE.value)
                results = page.get("results", [])
                num_of_results = len(results)
                has_more = has_more if num_of_results > 0 else False
                start_index += num_of_results
                yield results

    def search_all_data_assets(
        self,
        sort_order: Optional[str] = None,
        sort_field: Optional[str] = None,
        type: Optional[str] = None,
        ownership: Optional[str] = None,
        favorite: Optional[bool] = None,
        archived: Optional[bool] = None,
        query: Optional[str] = None,
    ) -> requests.models.Response:
        """
        Utility method to return all the search results that match a query
        Parameters
        ----------
        sort_order : Optional[str]
            Determines the result sort order.
        sort_field : Optional[str]
            Determines the field to sort by.
        type : Optional[str]
            Type of data asset: dataset or result.
            Returns both if omitted.
        ownership : Optional[str]
            Search data asset by ownership: owner or shared.
        favorite : Optional[bool]
            Search only favorite data assets.
        archived : Optional[bool]
            Search only archived data assets.
        query : Optional[str]
            Determines the search query.

        Returns
        -------
        requests.models.Response
        """

        # TODO: it'd be nice to re-use the search_data_assets function, but
        #  it'll require passing in a requests.Session object into that method.

        all_results = []

        for page in self._paginate_data_assets(
            sort_order=sort_order,
            sort_field=sort_field,
            type=type,
            ownership=ownership,
            favorite=favorite,
            archived=archived,
            query=query,
        ):
            all_results.extend(list(page))

        all_response = requests.Response()
        all_response.status_code = 200
        all_response._content = json.dumps({"results": all_results}).encode(
            "utf-8"
        )
        return all_response

    def create_data_asset(
        self, request: Union[dict, CreateDataAssetRequest]
    ) -> requests.models.Response:
        """
        Create a data asset. The request can either be a CreateDataAssetRequest
        class or a dictionary with the same shape. It's possible to create a
        data asset from: aws bucket/prefix, gcp bucket/prefix, computation id.
        More details about the other parameters can be found in the
        CreateDataAssetRequest documentation.
        Parameters
        ----------
        request : Union[dict, CreateDataAssetRequest]

        Returns
        -------
        requests.models.Response

        """
        if isinstance(request, dict):
            json_data = request
        else:
            json_data = json.loads(request.json_string)

        response = requests.post(
            self.asset_url, json=json_data, auth=(self.token, "")
        )

        return response

    def update_data_asset(
        self,
        data_asset_id: str,
        new_name: str,
        new_description: Optional[str] = None,
        new_tags: Optional[List[str]] = None,
        new_mount: Optional[str] = None,
        new_custom_metadata: Optional[dict] = None,
    ) -> requests.models.Response:
        """
        This will update a data asset from a PUT request to Code Ocean API.

        Parameters
        ---------------
        data_asset_id : string
            ID of the data asset
        new_name : str
            New name of the data asset
        new_description : Optional[str]
            New description of the data asset. Default None (not updated)
        new_tags : Optional[str]
            New tags of the data asset. Default None (not updated)
        new_mount : str
            New mount of the data asset. Default None (not updated)
        new_custom_metadata : Optional[dict]
            What key:value metadata tags to apply to the asset.

        Returns
        ---------------
        requests.models.Response
        """

        url = f"{self.asset_url}/{data_asset_id}"
        data = {self._Fields.NAME.value: new_name}

        if new_description:
            data[self._Fields.DESCRIPTION.value] = new_description

        if new_tags:
            data[self._Fields.TAGS.value] = new_tags

        if new_mount:
            data[self._Fields.MOUNT.value] = new_mount

        if new_custom_metadata:
            data[self._Fields.CUSTOM_METADATA.value] = new_custom_metadata

        response = requests.put(url, json=data, auth=(self.token, ""))

        return response

    def run_capsule(
        self, request: Union[dict, RunCapsuleRequest]
    ) -> requests.models.Response:
        """
        Run a capsule or pipeline. The request can either be a
        RunCapsuleRequest class or a dictionary with the same shape. More
        details about the other parameters can be found in the
        RunCapsuleRequest documentation.
        Parameters
        ----------
        request : Union[dict, RunCapsuleRequest]

        Returns
        -------
        requests.models.Response

        """

        if isinstance(request, dict):
            json_data = request
        else:
            json_data = json.loads(request.json_string)

        response = requests.post(
            url=self.computation_url, json=json_data, auth=(self.token, "")
        )

        return response

    def get_capsule(self, capsule_id: str) -> requests.models.Response:
        """
        This will get metadata from a GET request to Code Ocean API.

        Parameters
        ---------------
        capsule_id : string
            ID of the capsule

        Returns
        ---------------
        requests.models.Response
        """

        url = f"{self.capsule_url}/{capsule_id}"
        response = requests.get(url, auth=(self.token, ""))

        self.logger.info(response.url)

        return response

    def get_capsule_computations(
        self, capsule_id: str
    ) -> requests.models.Response:
        """
        This will get computation's metadata from a GET request to Code Ocean
        API.

        Parameters
        ---------------
        capsule_id : string
            ID of the capsule

        Returns
        ---------------
        requests.models.Response
        """
        url = (
            f"{self.capsule_url}/{capsule_id}/"
            f"{self._URLStrings.COMPUTATIONS.value}"
        )
        response = requests.get(url, auth=(self.token, ""))

        self.logger.info(response.url)

        return response

    def get_computation(self, computation_id: str) -> requests.models.Response:
        """
        This will get metadata from a GET request to Code Ocean API.

        Parameters
        ---------------
        computation_id : string
            ID of the computation

        Returns
        ---------------
        requests.models.Response
        """

        url = f"{self.computation_url}/{computation_id}"
        response = requests.get(url, auth=(self.token, ""))
        return response

    def get_list_result_items(
        self, computation_id: str
    ) -> requests.models.Response:
        """
        This will get a list of the computation's metadata from a POST request
        to Code Ocean API.

        Parameters
        ---------------
        computation_id : string
            ID of the computation

        Returns
        ---------------
        requests.models.Response
        """

        url = (
            f"{self.computation_url}/{computation_id}/"
            f"{self._URLStrings.RESULTS.value}"
        )
        response = requests.post(url, auth=(self.token, ""))
        return response

    def get_result_file_download_url(
        self, computation_id: str, path_to_file: str
    ) -> requests.models.Response:
        """
        This will get download link for a file from a GET request to
        Code Ocean API.

        Parameters
        ---------------
        computation_id : string
            ID of the computation

        path_to_file : string
            Path of the file under /results folder in Code Ocean capsule

        Returns
        ---------------
        requests.models.Response
        """

        results_suffix = f"results/download_url?path={path_to_file}"
        url = f"{self.computation_url}/{computation_id}/{results_suffix}"
        response = requests.get(url, auth=(self.token, ""))

        self.logger.info(response.url)

        return response

    def update_permissions(
        self,
        data_asset_id: str,
        users: Optional[List[Dict]] = None,
        groups: Optional[List[Dict]] = None,
        everyone: Optional[str] = None,
    ) -> requests.models.Response:
        """
        This will update permissions of a data asset from a POST request to
        Code Ocean API.

        Parameters
        ---------------
        data_asset_id : string
            ID of the data asset
        users: Optional[List[Dict]] (optional, default None)
            list of dictionaries containing keys 'email' and 'role'
        groups: Optional[List[Dict]] (optional, default None)
            list of dictionaries containing keys 'group' and 'role'
          'role' is 'owner' or 'viewer'
        everyone: str (optional, default None)
            'none': revoke global perms. 'viewer': grant viewer globally

        Returns
        ---------------
        requests.models.Response
        """

        users = [] if users is None else users
        groups = [] if groups is None else groups

        permissions = {
            self._Fields.USERS.value: users,
            self._Fields.GROUPS.value: groups,
        }

        if everyone is not None:
            permissions[self._Fields.EVERYONE.value] = everyone

        url = (
            f"{self.asset_url}/{data_asset_id}/"
            f"{self._URLStrings.PERMISSIONS.value}"
        )
        response = requests.post(url, json=permissions, auth=(self.token, ""))
        return response

    def archive_data_asset(
        self, data_asset_id: str, archive: bool = True
    ) -> requests.models.Response:
        """
        This will archive or unarchive a data asset using a PATCH request to
        the Code Ocean API.

        Parameters
        ---------------
        data_asset_id : string
            ID of the data asset

        Returns
        ---------------
        requests.models.Response
        """

        url = (
            f"{self.asset_url}/{data_asset_id}/"
            f"{self._URLStrings.ARCHIVE.value}"
        )
        response = requests.patch(
            url, params={"archive": archive}, auth=(self.token, "")
        )
        return response

    def delete_data_asset(
        self, data_asset_id: str
    ) -> requests.models.Response:
        """
        This will delete a data asset using a DELETE request to the Code Ocean
        API.

        Parameters
        ---------------
        data_asset_id : string
            ID of the data asset

        Returns
        ---------------
        requests.models.Response
        """

        url = f"{self.asset_url}/{data_asset_id}"

        response = requests.delete(url, auth=(self.token, ""))
        return response
