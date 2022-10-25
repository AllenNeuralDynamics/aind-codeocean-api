import os, json

def load_json(path):
    assert os.path.exists(path), f"credentials file {CREDENTIALS_PATH} does not exist"
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    

CREDENTIALS_PATH = os.environ.get('CODEOCEAN_CREDENTIALS_PATH', 'credentials.json')
CREDENTIALS = load_json(CREDENTIALS_PATH)
