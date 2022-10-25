"""Module to interface with codeocean api.
"""
import requests
from typing import List, Dict

class CodeOceanDataAssetRequests():
    """This class will handle the methods needed to manage data assets stored
    on Code Ocean's platform.
    """

    def __init__(self, domain:str, token:str) -> None:
        """
        Parameters
        ---------------
        domain : string
            Domain of VPC
        token : string
            Authorization token
        """

        self.domain = domain
        self.token = token
        self.api_version = 1
        self.asset_url = f"/api/v{self.api_version}/data_assets"

    def get_data_asset(self, data_asset_id:str) -> dict:
        """
        This will get data from a GET request to code ocean API.
        
        Parameters
        ---------------
        data_asset_id : string
            ID of the data asset
        
        Returns
        ---------------
        A json object as documented by CodeOcean's v1 api docs.
        """

        url = f"{self.domain}{self.asset_url}/{data_asset_id}"
        response = requests.get(url, auth=(self.token, ""))
        return response.json()

    def register_data_asset(self, 
        asset_name:str,
        mount:str,
        bucket:str,
        prefix:str,
        access_key_id:str,
        secret_access_key:str,
        tags:List[str]=None,
        asset_description:str="",
        keep_on_external_storage:bool=True,
        index_data:bool=True
    ) -> dict:
        """
        This will create a json object that will be attached to a post request.
        Args:
            asset_name (str): Name of the asset
            mount (str): Mount point
            bucket (str): Currently only aws buckets are allowed
            prefix (str): The object prefix in the bucket
            access_key_id (str): AWS access key
            secret_access_key (str): AWS secret access key
            tags (list[str]): A list of tags to attach to the data asset
            asset_description (str): A description of the data asset.
              Defaults to blank.
            keep_on_external_storage (bool): Keep data asset on external
              storage. Defaults to True.
            index_data (bool): Whether to index the data asset.
              Defaults to True.
        Returns:
            A json object as documented by CodeOcean's v1 api docs.
        """

        url = f"{self.domain}{self.asset_url}"

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
                    "access_key_id": access_key_id,
                    "secret_access_key": secret_access_key,
                },
            },
        }

        response = requests.post(url, json=json_data, auth=(self.token, ""))
        return response

    def update_data_asset(
        self, 
        data_asset_id:str, 
        new_name:str, 
        new_description:str=None, 
        new_tags:List[str]=None, 
        new_mount:str=None
    ) -> dict:

        url = f"{self.domain}{self.asset_url}/{data_asset_id}"
        data = {
            'name': new_name
        }

        if new_description:
            data['description'] = new_description
        
        if new_tags:
            data['tags'] = new_tags
        
        if new_mount:
            data['mount'] = new_mount

        response = requests.put(
            url,
            json=data,
            auth=(self.token, "")
        )

        return response.json()


class CodeOceanCapsuleRequests():
    """This class will handle the methods needed to manage capsules stored
    on Code Ocean's platform.
    """

    def __init__(self, domain:str, token:str) -> None:
        """
        Parameters
        ---------------
        domain : string
            Domain of VPC
        token : string
            Authorization token
        """

        self.domain = domain
        self.token = token
        self.api_version = 1
        self.asset_url = f"/api/v{self.api_version}/data_assets"
        self.capsule_url = f"/api/v{self.api_version}/capsules"
        self.computation_url = f"/api/v{self.api_version}/computations"

    def get_capsule(self, capsule_id:str) -> dict:
        """
        This will get metadata from a GET request to code ocean API.
        
        Parameters
        ---------------
        capsule_id : string
            ID of the capsule
        
        Returns
        ---------------
        A json object as documented by CodeOcean's v1 api docs.
        """

        url = f"{self.domain}{self.capsule_url}/{capsule_id}"
        response = requests.get(url, auth=(self.token, ""))
        return response.json()

    def get_capsule_computations(self, capsule_id:str) -> dict:
        """
        This will get computation's metadata from a GET request to code ocean API.
        
        Parameters
        ---------------
        capsule_id : string
            ID of the capsule
        
        Returns
        ---------------
        A json object as documented by CodeOcean's v1 api docs.
        """

        url = f"{self.domain}{self.capsule_url}/{capsule_id}/computations"
        response = requests.get(url, auth=(self.token, ""))
        return response.json()

    def run_capsule(
        self, 
        capsule_id:str, 
        data_assets:Dict,
        parameters:List=None,
    ) -> dict:
        """
        This will run a capsule/pipeline using a POST request to code ocean API.
        
        Parameters
        ---------------
        capsule_id : string
            ID of the capsule
        data_assets : Dict
            Dictionary containing the following keys: 'id' which refers to the
            data asset id in Code Ocean and 'mount' which refers to the data asset
            mount folder.
        parameters : List
            List of parameters given to the capsule. Default None which means the
            capsule runs with no parameters.
            
            The parameters should match in order to the parameters given in the capsule.
            
            e.g. 
            'parameters': [
                'input_folder', 
                'output_folder', 
                'bucket_name'
            ]
            
            where position one refers to the parameter #1 ('input_folder'), parameter #2 ('output_folder'), 
            and parameter #3 ('bucket_name')
        
        Returns
        ---------------
        A json object as documented by CodeOcean's v1 api docs.
        """

        url = f"{self.domain}{self.computation_url}"

        data = {
            'capsule_id': capsule_id,
            'data_assets': [data_assets]
        }

        if parameters:
            data['parameters'] = parameters

        response = requests.post(
            url=url,
            json=data,
            auth=(self.token, "")
        )

        return response.json()
