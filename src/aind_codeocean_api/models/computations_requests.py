"""Module for class to send a request to the computation endpoint"""

from dataclasses import dataclass
from typing import List, Optional

from aind_codeocean_api.models.basic_request import BasicRequest


@dataclass
class ComputationDataAsset:
    """The data asset input has a different structure than in other classes"""

    id: str
    mount: str


@dataclass
class ComputationNamedParameter:
    """Named parameters can be input into a request, but look like:
    {"param_name": "key", "value": "value"}"""

    param_name: str
    value: str


@dataclass
class ComputationProcess:
    """Computation process"""

    name: str
    parameters: Optional[List[str]] = None
    named_parameters: Optional[List[ComputationNamedParameter]] = None


@dataclass
class RunCapsuleRequest(BasicRequest):
    """Request used to run a capsule or a pipeline."""

    capsule_id: Optional[str] = None
    pipeline_id: Optional[str] = None
    version: Optional[int] = None
    resume_run_id: Optional[str] = None
    data_assets: Optional[List[ComputationDataAsset]] = None
    parameters: Optional[List[str]] = None
    named_parameters: Optional[List[ComputationNamedParameter]] = None
    processes: Optional[List[ComputationProcess]] = None
