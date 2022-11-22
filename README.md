# aind-codeocean-api

[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)
![Code Style](https://img.shields.io/badge/code%20style-black-black)

Python wrapper around CodeOcean's REST API.

## Installation
To install from [PyPI](https://pypi.org/project/aind-codeocean-api/), run:
```
pip install aind-codeocean-api
```

To install from a clone of the repository, in the root directory, run
```
pip install -e .
```

To install the development libraries of the code, run
```
pip install -e .[dev]
```

## Usage
Example of getting data asset metadata:
```
from aind_codeocean_api.codeocean import CodeOceanClient

domain = "https://acmecorp.codeocean.com"
token = "AN_API_TOKEN" # Replace with your api token
data_asset_id = "37a93748-ce90-4980-913b-2de0908d5212"
co_client = CodeOceanClient(domain=domain, token=token)
response = co_client.get_data_asset(data_asset_id=data_asset_id)
metadata = response.json()
```

## Contributing

### Linters and testing

There are several libraries used to run linters, check documentation, and run tests.

- Please test your changes using the **coverage** library, which will run the tests and log a coverage report:

```
coverage run -m unittest discover && coverage report
```

- Use **interrogate** to check that modules, methods, etc. have been documented thoroughly:

```
interrogate .
```

- Use **flake8** to check that code is up to standards (no unused imports, etc.):
```
flake8 .
```

- Use **black** to automatically format the code into PEP standards:
```
black .
```

- Use **isort** to automatically sort import statements:
```
isort .
```

### Pull requests

For internal members, please create a branch. For external members, please fork the repo and open a pull request from the fork. We'll primarily use [Angular](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit) style for commit messages. Roughly, they should follow the pattern:
```
<type>(<scope>): <short summary>
```

where scope (optional) describes the packages affected by the code changes and type (mandatory) is one of:

- **build**: Changes that affect the build system or external dependencies (example scopes: pyproject.toml, setup.py)
- **ci**: Changes to our CI configuration files and scripts (examples: .github/workflows/ci.yml)
- **docs**: Documentation only changes
- **feat**: A new feature
- **fix**: A bug fix
- **perf**: A code change that improves performance
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **test**: Adding missing tests or correcting existing tests

### Documentation
To generate the rst files source files for documentation, run
```
sphinx-apidoc -o doc_template/source/ src 
```
Then to create the documentation html files, run
```
sphinx-build -b html doc_template/source/ doc_template/build/html
```
More info on sphinx installation can be found here: https://www.sphinx-doc.org/en/master/usage/installation.html
