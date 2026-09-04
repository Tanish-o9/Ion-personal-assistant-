from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class DatasetCase(BaseModel):
    case_id: str
    input_prompt: str
    expected_output: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DatasetVersion(BaseModel):
    dataset_id: str
    version: str = "1.0.0"
    authorized_by: str
    cases: List[DatasetCase] = Field(default_factory=list)

class ModelRegistryEntry(BaseModel):
    model_id: str
    provider: str
    version: str
    status: str = "development" # development, evaluation, candidate, production, retired
    capabilities: List[str] = Field(default_factory=list)
    evaluation_pass_rate: Optional[float] = None
