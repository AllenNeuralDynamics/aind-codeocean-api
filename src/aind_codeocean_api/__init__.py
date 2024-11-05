"""
Python wrapper of CodeOcean's REST API.

DEPRECATION WARNING. Code Ocean has published their own SDK:

https://github.com/codeocean/codeocean-sdk-python

We will be dropping support of this package in favor of the official SDK.
"""
import warnings

__version__ = "0.5.0"

warnings.warn(
    "This package is deprecated and will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2,
)
