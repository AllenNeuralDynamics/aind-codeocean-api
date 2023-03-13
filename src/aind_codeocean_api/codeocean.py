"""Module to interface with Code Ocean's backend.
"""
import json
import logging
from enum import Enum
from typing import Dict, List, Optional

import requests


class CodeOceanClient:
    """Client that will connect to Code Ocean"""

    _MAX_SEARCH_BATCH_REQUEST = 1000

    class _URLStrings(Enum):
        """Enum class for CodeOcean's url strings"""

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
        self.domain = domain
        self.token = token
        self.api_version = api_version
        self.logger = logging.getLogger('aind-codeocean-api')
        self.asset_url = (
            f"{self.domain}/api/v{self.api_version}/"
            f"{self._URLStrings.DATA_ASSETS.value}"
        )
        self.capsule_url = (
            f"{self.domain}/api/v{self.api_version}/"
            f"{self._URLStrings.CAPSULES.value}"
        )
        self.computation_url = (
            f"{self.domain}/api/v{self.api_version}/"
            f"{self._URLStrings.COMPUTATIONS.value}"
        )

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
        optional_params = locals()
        query_params = {}

        for param, val in optional_params.items():
            if val is not None:
                query_params[param] = val

        response = requests.get(
            self.asset_url, params=query_params, auth=(self.token, "")
        )

        self.logger.info(response.url)

        return response

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
        optional_params = locals()
        query_params = {}

        for param, val in optional_params.items():
            if val is not None:
                query_params[param] = val

        requests_session = requests.Session()
        all_results = []
        with requests.Session() as requests_session:
            has_more = True
            status_code = 200
            start_index = 0
            limit = self._MAX_SEARCH_BATCH_REQUEST
            while has_more and status_code == 200:
                query_params[self._Fields.START.value] = start_index
                query_params[self._Fields.LIMIT.value] = limit
                response = requests_session.get(
                    self.asset_url, params=query_params, auth=(self.token, "")
                )

                self.logger.info(response.url)

                status_code = response.status_code
                if status_code == 200:
                    has_more = response.json()[self._Fields.HAS_MORE.value]
                    response_results = response.json()[
                        self._Fields.RESULTS.value
                    ]
                    num_of_results = len(response_results)
                    all_results.extend(response_results)
                    has_more = has_more if num_of_results > 0 else False
                    start_index += num_of_results
                else:
                    return response

        all_response = requests.Response()
        all_response.status_code = 200
        all_response._content = json.dumps({"results": all_results}).encode(
            "utf-8"
        )
        return all_response

    def register_data_asset(
        self,
        asset_name: str,
        mount: str,
        bucket: str,
        prefix: str,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        tags: Optional[List[str]] = None,
        asset_description: Optional[str] = "",
        keep_on_external_storage: Optional[bool] = True,
        index_data: Optional[bool] = True,
    ) -> requests.models.Response:
        """
        Parameters
        ---------------
        asset_name : string
            Name of the asset
        mount : string
            Mount point
        bucket : string
            Bucket name. Currently only aws buckets are allowed.
        prefix : string
            The object prefix in the bucket
        access_key_id : Optional[str]
            AWS access key. It's not necessary for public buckets.
            Default None (not provided).
        secret_access_key : Optional[str]
            AWS secret access key. It's not necessary for public buckets.
            Default None (not provided).
        tags : Optional[List[str]]
            A list of tags to attach to the data asset.
            Default None (empty list).
        asset_description : Optional[str]
            A description of the data asset. Default blanks.
        keep_on_external_storage : Optional[bool]
            Keep data asset on external storage. Defaults to True.
        index_data : Optional[bool]
            Whether to index the data asset. Defaults to True.
        Returns
        ---------------
        requests.models.Response
        """

        tags_to_attach = [] if tags is None else tags
        json_data = {
            self._Fields.NAME.value: asset_name,
            self._Fields.DESCRIPTION.value: asset_description,
            self._Fields.MOUNT.value: mount,
            self._Fields.TAGS.value: tags_to_attach,
            self._Fields.SOURCE.value: {
                self._Fields.AWS.value: {
                    self._Fields.BUCKET.value: bucket,
                    self._Fields.PREFIX.value: prefix,
                    self._Fields.KEEP_ON_EXTERNAL_STORAGE.value: (
                        keep_on_external_storage
                    ),
                    self._Fields.INDEX_DATA.value: index_data,
                }
            },
        }

        if access_key_id and secret_access_key:
            json_data[self._Fields.SOURCE.value][self._Fields.AWS.value][
                self._Fields.ACCESS_KEY_ID.value
            ] = access_key_id
            json_data[self._Fields.SOURCE.value][self._Fields.AWS.value][
                self._Fields.SECRET_ACCESS_KEY.value
            ] = secret_access_key

        response = requests.post(
            self.asset_url, json=json_data, auth=(self.token, "")
        )
        return response

    def register_result_as_data_asset(
        self,
        computation_id: str,
        asset_name: str,
        asset_description: Optional[str] = "",
        mount: Optional[str] = None,
        tags: Optional[List] = None,
    ) -> requests.models.Response:
        """
        Parameters
        ---------------
        computation_id : string
            Computation id
        asset_name : string
            Name of the data asset.
        asset_description : Optional[str]
            A description of the data asset. Default blanks.
        mount : string
            Mount point. Default None (Mount point equal to the asset name)
        tags : Optional[List[str]]
            A list of tags to attach to the data asset.
            Default None (empty list).

        keep_on_external_storage : Optional[bool]
            Keep data asset on external storage. Defaults to True.
        index_data : Optional[bool]
            Whether to index the data asset. Defaults to True.
        Returns
        ---------------
        requests.models.Response
        """

        tags_to_attach = [] if tags is None else tags

        if mount is None:
            mount = asset_name

        json_data = {
            self._Fields.NAME.value: asset_name,
            self._Fields.DESCRIPTION.value: asset_description,
            self._Fields.MOUNT.value: mount,
            self._Fields.TAGS.value: tags_to_attach,
            self._Fields.SOURCE.value: {
                self._Fields.COMPUTATION.value: {
                    self._Fields.ID.value: computation_id
                }
            },
        }

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

        response = requests.put(url, json=data, auth=(self.token, ""))

        return response

    def run_capsule(
        self,
        capsule_id: str,
        data_assets: List[Dict],
        version: Optional[int] = None,
        parameters: Optional[List] = None,
    ) -> requests.models.Response:
        """
        This will run a capsule/pipeline using a POST request to Code Ocean
        API.

        Parameters
        ---------------
        capsule_id : string
            ID of the capsule
        data_assets : List[dict]
            List of dictionaries containing the following keys: 'id' which
            refers to the data asset id in Code Ocean and 'mount' which
            refers to the data asset mount folder.
        version : Optional[int]
            Capsule version to be run. Defaults to None.
        parameters : List
            Parameters given to the capsule. Default None which means
            the capsule runs with no parameters.
            The parameters should match in order to the parameters given in the
            capsule, e.g.
            'parameters': [
            'input_folder',
            'output_folder',
            'bucket_name'
            ]
            where position one refers to the parameter #1 ('input_folder'),
            parameter #2 ('output_folder'), and parameter #3 ('bucket_name')
        Returns
        ---------------
        requests.models.Response
        """

        data = {
            self._Fields.CAPSULE_ID.value: capsule_id,
            self._Fields.DATA_ASSETS.value: data_assets,
        }

        if parameters:
            data[self._Fields.PARAMETERS.value] = parameters
        if version:
            data[self._Fields.VERSION.value] = version

        response = requests.post(
            url=self.computation_url, json=data, auth=(self.token, "")
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
        users: List[Dict] = [],
        groups: List[Dict] = [],
        everyone: bool = None,
    ) -> requests.models.Response:
        """
        This will update permissions of a data asset from a POST request to
        Code Ocean API.

        Parameters
        ---------------
        data_asset_id : string
            ID of the data asset
        users: List[Dict] (optional, default [])
            list of dictionaries containing keys 'email' and 'role'
        groups: List[Dict] (optional, default [])
            list of dictionaries containing keys 'group' and 'role'
          'role' is 'owner' or 'viewer'
        everyone: bool (optional, default True)
            boolean value indicating whether the data asset is public

        Returns
        ---------------
        requests.models.Response
        """

        if not everyone:
            permissions = {
                self._Fields.USERS.value: users,
                self._Fields.GROUPS.value: groups,
            }
        else:
            permissions = {
                self._Fields.USERS.value: users,
                self._Fields.GROUPS.value: groups,
                self._Fields.EVERYONE.value: everyone,
            }
        url = (
            f"{self.asset_url}/{data_asset_id}/"
            f"{self._URLStrings.PERMISSIONS.value}"
        )
        response = requests.post(url, json=permissions, auth=(self.token, ""))
        return response
