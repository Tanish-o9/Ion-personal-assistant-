from typing import Dict, List, Optional
from orchestrator.adaptation.models import ModelRegistryEntry
from orchestrator.observability import jarvis_logger

class ModelRegistry:
    """
    Registry managing model versioning, capabilities, deployment release lifecycle,
    and gateway routing eligibility.
    """
    def __init__(self):
        self.models: Dict[str, ModelRegistryEntry] = {}

    def register_model(self, entry: ModelRegistryEntry) -> ModelRegistryEntry:
        self.models[entry.model_id] = entry
        jarvis_logger.info("Registered model '%s' (v%s) with status '%s'", entry.model_id, entry.version, entry.status)
        return entry

    def promote_status(self, model_id: str, new_status: str, min_pass_rate: float = 90.0) -> bool:
        model = self.models.get(model_id)
        if not model:
            return False

        if new_status == "production":
            if model.evaluation_pass_rate is None or model.evaluation_pass_rate < min_pass_rate:
                raise ValueError(f"Cannot promote model '{model_id}' to production: pass rate ({model.evaluation_pass_rate}%) is below minimum threshold ({min_pass_rate}%).")

        model.status = new_status
        return True

    def get_production_models(self) -> List[ModelRegistryEntry]:
        return [m for m in self.models.values() if m.status == "production"]

    def list_registered_models(self) -> List[ModelRegistryEntry]:
        return list(self.models.values())

default_model_registry = ModelRegistry()
