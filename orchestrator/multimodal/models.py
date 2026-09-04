import base64
from typing import Any, Dict, List, Optional

MAX_IMAGE_SIZE = 10 * 1024 * 1024       # 10 MB limit for images
MAX_DOCUMENT_SIZE = 5 * 1024 * 1024     # 5 MB limit for documents
VALID_IMAGE_MIMES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
VALID_DOC_EXTENSIONS = {".txt", ".md"}

class MultimodalInput:
    """
    Represents a single multimodal input item (image, document, or text).
    """
    def __init__(
        self,
        input_type: str,
        content_bytes: bytes,
        filename: str = "file",
        mime_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        if input_type.lower() not in {"text", "image", "document"}:
            raise ValueError(f"Invalid input_type '{input_type}'. Must be 'text', 'image', or 'document'.")
        if not content_bytes or len(content_bytes) == 0:
            raise ValueError("content_bytes must be non-empty.")

        self.input_type = input_type.lower().strip()
        self.content_bytes = content_bytes
        self.filename = filename
        self.mime_type = (mime_type or "application/octet-stream").lower().strip()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_type": self.input_type,
            "filename": self.filename,
            "mime_type": self.mime_type,
            "size_bytes": len(self.content_bytes),
            "content_base64": base64.b64encode(self.content_bytes).decode("ascii"),
            "metadata": self.metadata,
        }

class MultimodalContext:
    """
    Encapsulates processed visual and document context for agent injection.
    """
    def __init__(
        self,
        visual_context: Optional[str] = None,
        document_context: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.visual_context = visual_context or ""
        self.document_context = document_context or ""
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "visual_context": self.visual_context,
            "document_context": self.document_context,
            "metadata": self.metadata,
        }

class UnifiedMultimodalContext:
    """
    Unified Multimodal 2.0 reasoning context aggregating text, image, document, audio transcript,
    retrieved RAG knowledge, research context, and permanent ingestion flags.
    """
    def __init__(
        self,
        text_context: Optional[str] = None,
        image_context: Optional[str] = None,
        document_context: Optional[str] = None,
        audio_transcript: Optional[str] = None,
        retrieved_knowledge: Optional[List[Dict[str, Any]]] = None,
        research_context: Optional[str] = None,
        is_permanent_ingestion: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.text_context = text_context or ""
        self.image_context = image_context or ""
        self.document_context = document_context or ""
        self.audio_transcript = audio_transcript or ""
        self.retrieved_knowledge = retrieved_knowledge or []
        self.research_context = research_context or ""
        self.is_permanent_ingestion = is_permanent_ingestion
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text_context": self.text_context,
            "image_context": self.image_context,
            "document_context": self.document_context,
            "audio_transcript": self.audio_transcript,
            "retrieved_knowledge": self.retrieved_knowledge,
            "research_context": self.research_context,
            "is_permanent_ingestion": self.is_permanent_ingestion,
            "metadata": self.metadata,
        }
