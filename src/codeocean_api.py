import requests
import logging
import os, json
from credentials import CREDENTIALS

DATA_ASSET_API = "https://codeocean.allenneuraldynamics.org/api/v1/data_assets"


def send_post(url, data=None):
    api_key = CREDENTIALS['codeocean']['api_key']
    return requests.post(url, json=data, auth=(f"'{api_key}", "'"))

def send_get(url, data=None):
    api_key = CREDENTIALS['codeocean']['api_key']
    return requests.get(url, params=data, auth=(f"'{api_key}", "'"))

def send_patch(url, data=None):
    api_key = CREDENTIALS['codeocean']['api_key']
    return requests.patch(url, params=data, auth=(f"'{api_key}", "'"))

def check_if_exists(asset_name):
    data = {
        "query": f"name:{asset_name}"
    }
    response = send_get(DATA_ASSET_API, data)

    logging.info(response.request.url)

    data = response.json()
    
    return len(data['results']) > 0
    
def register_data_asset(bucket_name, bucket_path, description="", tags=None):
    data = {
        "name": bucket_path,
        "description": description,
        "mount": bucket_path,
        "tags": tags,
        "source": {
            "aws": {
                "access_key_id": CREDENTIALS['aws']['access_key_id'],
                "secret_access_key": CREDENTIALS['aws']['secret_access_key'],
                "bucket": bucket_name,
                "prefix": bucket_path,
                "keep_on_external_storage": True,
                "index_data": True
                }
            }  
    }

    response = send_post(DATA_ASSET_API, data)
    logging.info(response.request.url)

def list_data_assets(query=None, archived=None):
    start = 0
    get_more = True
    while get_more:
        data = {
            "start": start
        }

        if query is not None:
            data['query'] = query

        if archived is not None:
            data['archived'] = archived

        response = send_get(DATA_ASSET_API, data)
        logging.info(response.request.url)
        
        r = response.json()            
        
        
        yield from r['results']

        if r['has_more']:
            start += len(r['results'])
        else:
            get_more = False

def get_data_asset(data_asset_id):
    response = send_get(f"{DATA_ASSET_API}/{data_asset_id}")
    return response.json()


def archive_data_asset(data_asset_id):
    response = send_patch(f"{DATA_ASSET_API}/{data_asset_id}/archive", { "archive": "true" })
    logging.info(response.request.url)
    logging.info(response.text)
