from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class InteractionRequest:
    user_id: str
    session_id: str
    text: Optional[str] = None
    audio: Optional[bytes] = None
    images: List[str] = field(default_factory=list) # Base64 or URIs
    documents: List[Dict[str, Any]] = field(default_factory=list)
    structured_data: Dict[str, Any] = field(default_factory=dict)
    device_context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContextStreamItem:
    source: str
    timestamp: str = field(default_factory=utc_now)
    scope: str = "SESSION" # SESSION, WORKSPACE, USER
    relevance: float = 1.0
    trust_level: str = "HIGH" # HIGH, MEDIUM, LOW
    content: Any = None

class UnifiedMultimodalContext:
    def __init__(self):
        self.text_context: List[ContextStreamItem] = []
        self.audio_context: List[ContextStreamItem] = []
        self.visual_context: List[ContextStreamItem] = []
        self.document_context: List[ContextStreamItem] = []
        self.structured_context: List[ContextStreamItem] = []
        self.device_context: List[ContextStreamItem] = []
        self.knowledge_context: List[ContextStreamItem] = []
        self.research_context: List[ContextStreamItem] = []
        self.conversation_context: List[ContextStreamItem] = []

    def add_item(self, stream_name: str, item: ContextStreamItem):
        stream = getattr(self, f"{stream_name}_context", None)
        if stream is not None:
            stream.append(item)

    def get_summary(self) -> Dict[str, int]:
        return {
            "text": len(self.text_context),
            "audio": len(self.audio_context),
            "visual": len(self.visual_context),
            "document": len(self.document_context),
            "structured": len(self.structured_context),
            "device": len(self.device_context),
            "knowledge": len(self.knowledge_context),
            "research": len(self.research_context),
            "conversation": len(self.conversation_context),
        }

class ModalityRouter:
    def determine_required_modalities(self, req: InteractionRequest) -> List[str]:
        required = []
        if req.text:
            prompt_lower = req.text.lower()
            if any(w in prompt_lower for w in ["image", "picture", "photo", "look"]):
                required.append("VISION")
            if any(w in prompt_lower for w in ["pdf", "document", "file", "summarize"]):
                required.append("DOCUMENT")
            if any(w in prompt_lower for w in ["device", "light", "thermostat", "online"]):
                required.append("DEVICE")
            if any(w in prompt_lower for w in ["search", "web", "latest"]):
                required.append("RESEARCH")

        if req.images and "VISION" not in required:
            required.append("VISION")
        if req.documents and "DOCUMENT" not in required:
            required.append("DOCUMENT")
        if req.audio and "AUDIO" not in required:
            required.append("AUDIO")
        if req.device_context and "DEVICE" not in required:
            required.append("DEVICE")

        return required or ["TEXT"]

@dataclass
class EvidenceNode:
    modality: str
    source_name: str
    content: str
    relevance_score: float = 1.0

class CrossModalEvidenceTree:
    def __init__(self):
        self.nodes: List[EvidenceNode] = []

    def add_evidence(self, modality: str, source_name: str, content: str, relevance: float = 1.0):
        self.nodes.append(EvidenceNode(modality=modality, source_name=source_name, content=content, relevance_score=relevance))

    def format_evidence_panel(self) -> Dict[str, Any]:
        return {
            "total_nodes": len(self.nodes),
            "modalities": list(set(n.modality for n in self.nodes)),
            "evidence": [{"modality": n.modality, "source": n.source_name, "snippet": n.content[:100]} for n in self.nodes]
        }

class VoiceMultimodalPipeline:
    def process_voice_interaction(self, audio_bytes: bytes, context: UnifiedMultimodalContext) -> Dict[str, Any]:
        # STT -> Reasoning -> TTS
        transcript = "Turn on the living room light and check document summary"
        context.add_item("audio", ContextStreamItem(source="STT", content=transcript))
        return {
            "stt_transcript": transcript,
            "reasoning_outcome": "Executing device command and document retrieval",
            "tts_audio_generated": True,
            "status": "COMPLETED",
        }

class ContextBudgetManager:
    def __init__(self, max_tokens: int = 128000, max_images: int = 5, max_documents: int = 10):
        self.max_tokens = max_tokens
        self.max_images = max_images
        self.max_documents = max_documents

    def validate_request_budget(self, req: InteractionRequest) -> Dict[str, Any]:
        if len(req.images) > self.max_images:
            raise ValueError(f"Image count ({len(req.images)}) exceeds limit of {self.max_images}")
        if len(req.documents) > self.max_documents:
            raise ValueError(f"Document count ({len(req.documents)}) exceeds limit of {self.max_documents}")

        return {"within_budget": True, "allocated_tokens": 4096}

class PrivacyTracker:
    def __init__(self):
        self.log: List[Dict[str, Any]] = []

    def track_processing(self, modality: str, is_local: bool, scope: str):
        self.log.append({
            "modality": modality,
            "is_local": is_local,
            "scope": scope,
            "timestamp": utc_now(),
        })
