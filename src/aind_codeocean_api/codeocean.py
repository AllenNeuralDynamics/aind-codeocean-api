"""Module to interface with Code Ocean's backend.
"""
from typing import Dict, List, Optional

import requests


class CodeOceanClient:
    """Client that will connect to Code Ocean"""

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
        self.asset_url = f"{self.domain}/api/v{self.api_version}/data_assets"
        self.capsule_url = f"{self.domain}/api/v{self.api_version}/capsules"
        self.computation_url = (
            f"{self.domain}/api/v{self.api_version}/computations"
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
        This will return data assets from a GET requets to Code Ocean API.

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

        return response

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
            "name": asset_name,
            "description": asset_description,
            "mount": mount,
            "tags": tags_to_attach,
            "source": {
                "aws": {
                    "bucket": bucket,
                    "prefix": prefix,
                    "keep_on_external_storage": keep_on_external_storage,
                    "index_data": index_data,
                },
            },
        }

        if access_key_id and secret_access_key:
            json_data["source"]["aws"]["access_key_id"] = access_key_id
            json_data["source"]["aws"]["secret_access_key"] = secret_access_key

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
            "name": asset_name,
            "description": asset_description,
            "mount": mount,
            "tags": tags_to_attach,
            "source": {"computation": {"id": computation_id}},
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
        data = {"name": new_name}

        if new_description:
            data["description"] = new_description

        if new_tags:
            data["tags"] = new_tags

        if new_mount:
            data["mount"] = new_mount

        response = requests.put(url, json=data, auth=(self.token, ""))

        return response

    def run_capsule(
        self,
        capsule_id: str,
        data_assets: List[Dict],
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

        data = {"capsule_id": capsule_id, "data_assets": data_assets}

        if parameters:
            data["parameters"] = parameters

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

        url = f"{self.capsule_url}/{capsule_id}/computations"
        response = requests.get(url, auth=(self.token, ""))
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

        url = f"{self.computation_url}/{computation_id}/results"
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
        return response

    def update_permissions(
        self, capsule_id: str, permissions: Dict
    ) -> requests.models.Response:
        """
        This will update permissions of a capsule from a PUT request to
        Code Ocean API.

        Parameters
        ---------------
        capsule_id : string
            ID of the capsule
        permissions : dict
            Dictionary containing the following keys: 'users' and 'groups'.
            'users' is a list of dictionaries containing the following
            keys: 'id' which refers to the user id in Code Ocean and 'role'
            which refers to the user's role in the capsule.
            'groups' is a list of dictionaries containing the following
            keys: 'id' which refers to the group id in Code Ocean and 'role'
            which refers to the group's role in the capsule.
        
        Returns
        ---------------
        requests.models.Response
        """
            
        url = f"{self.capsule_url}/{capsule_id}/permissions"
        response = requests.put(url, json=permissions, auth=(self.token, ""))
        return response
