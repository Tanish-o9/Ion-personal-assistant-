"""
Phase 69: Multimodal Perception 3.0 & Prompt Injection Defense.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from orchestrator.security import InputSanitizer
from orchestrator.multimodal.models import MultimodalInput


class UnifiedMultimodalContext(BaseModel):
    """Unified container for text, images, audio transcripts, documents, and structured tables."""
    text_prompt: str = ""
    image_paths: List[str] = Field(default_factory=list)
    document_paths: List[str] = Field(default_factory=list)
    audio_transcripts: List[str] = Field(default_factory=list)
    structured_tables: List[Dict[str, Any]] = Field(default_factory=list)
    sanitized_prompt: str = ""
    supported_modalities: List[str] = Field(default_factory=list)

class MultimodalPerceptionEngine:
    """Manages modality routing, resource bounds checks, and prompt injection boundaries on media content."""

    def assemble_and_sanitize_context(
        self,
        text_prompt: str,
        image_paths: Optional[List[str]] = None,
        document_paths: Optional[List[str]] = None,
        audio_transcripts: Optional[List[str]] = None,
        structured_tables: Optional[List[Dict[str, Any]]] = None,
        max_attachments: int = 10
    ) -> UnifiedMultimodalContext:

        imgs = image_paths or []
        docs = document_paths or []
        audios = audio_transcripts or []

        # Attachment count limit
        if len(imgs) + len(docs) + len(audios) > max_attachments:
            raise ValueError(f"Attachment count exceeds limit of {max_attachments}")

        # Determine modalities present
        modalities = ["text"]
        if imgs:
            modalities.append("image")
        if docs:
            modalities.append("document")
        if audios:
            modalities.append("audio")
        if structured_tables:
            modalities.append("structured_data")

        # Sanitize and isolate untrusted media contents
        sanitized_parts = [text_prompt]
        for idx, doc in enumerate(docs, start=1):
            sanitized_parts.append(InputSanitizer.wrap_untrusted_context(f"Doc Path: {doc}", f"Document {idx}"))

        for idx, tr in enumerate(audios, start=1):
            sanitized_parts.append(InputSanitizer.wrap_untrusted_context(tr, f"Audio Transcript {idx}"))

        combined_prompt = "\n\n".join(sanitized_parts)

        return UnifiedMultimodalContext(
            text_prompt=text_prompt,
            image_paths=imgs,
            document_paths=docs,
            audio_transcripts=audios,
            structured_tables=structured_tables or [],
            sanitized_prompt=combined_prompt,
            supported_modalities=modalities
        )

    def route_modality_model(self, context: UnifiedMultimodalContext, target_model_capabilities: List[str]) -> bool:
        """Verifies if target model capabilities support all requested modalities."""
        for mod in context.supported_modalities:
            if mod != "text" and mod not in target_model_capabilities:
                return False
        return True

default_multimodal_perception_engine = MultimodalPerceptionEngine()
