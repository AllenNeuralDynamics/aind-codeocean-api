"""Module for class to send a request to the data assets endpoint"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from aind_codeocean_api.models.basic_request import BasicRequest


class Sources:
    """Currently, three different sources can be defined. AWS, GCP, and a
    Computation from a capsule"""

    @dataclass
    class AWS:
        """Fields required to create a data asset from aws"""

        bucket: str
        prefix: Optional[str] = None
        keep_on_external_storage: Optional[bool] = None
        public: Optional[bool] = None

    @dataclass
    class GCP:
        """Fields required to create a data asset from gcp"""

        bucket: str
        prefix: Optional[str] = None
        client_id: Optional[str] = None
        client_secret: Optional[str] = None

    @dataclass
    class Computation:
        """Fields required to create a data asset from a computation"""

        id: str
        path: Optional[str] = None


@dataclass
class Source:
    """Source needs to be one of aws, gcp, or computation"""

    aws: Optional[Sources.AWS] = None
    gcp: Optional[Sources.GCP] = None
    computation: Optional[Sources.Computation] = None

    def __post_init__(self):
        """Basic validation on fields to verify at least one is set"""
        nones = [
            a for a in [self.aws, self.gcp, self.computation] if a is None
        ]
        if len(nones) == 3:
            raise Exception("At least one source is required")


class Targets:
    """Targets to send data to"""

    @dataclass
    class AWS:
        """AWS bucket and prefix"""

        bucket: str
        prefix: Optional[str] = None


@dataclass
class Target:
    """Target field needs to be aws with potential to expand in the future"""

    aws: Targets.AWS


@dataclass
class CreateDataAssetRequest(BasicRequest):
    """Request used to create a data asset from an external source or a
    capsule computation."""

    name: str
    tags: List[str]
    mount: str
    description: Optional[str] = None
    source: Optional[Source] = None
    target: Optional[Target] = None
    custom_metadata: Optional[Dict[str, Any]] = None
