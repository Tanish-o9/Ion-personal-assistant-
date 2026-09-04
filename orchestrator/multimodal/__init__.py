from orchestrator.multimodal.models import (
    MultimodalInput,
    MultimodalContext,
    UnifiedMultimodalContext,
    MAX_IMAGE_SIZE,
    MAX_DOCUMENT_SIZE,
    VALID_IMAGE_MIMES,
    VALID_DOC_EXTENSIONS,
)
from orchestrator.multimodal.image import BaseVisionProvider, MockVisionProvider, ImageProcessor
from orchestrator.multimodal.document import DocumentProcessor
from orchestrator.multimodal.processor import MultimodalProcessor

# Shared default instances
default_image_processor = ImageProcessor()
default_document_processor = DocumentProcessor()
default_multimodal_processor = MultimodalProcessor(
    image_processor=default_image_processor,
    document_processor=default_document_processor,
)

from orchestrator.multimodal.unified import UnifiedMultimodalContext as UnifiedMultimodalContext3, MultimodalPerceptionEngine, default_multimodal_perception_engine

__all__ = [
    "MultimodalInput",
    "MultimodalContext",
    "UnifiedMultimodalContext",
    "UnifiedMultimodalContext3",
    "MAX_IMAGE_SIZE",
    "MAX_DOCUMENT_SIZE",
    "VALID_IMAGE_MIMES",
    "VALID_DOC_EXTENSIONS",
    "BaseVisionProvider",
    "MockVisionProvider",
    "ImageProcessor",
    "DocumentProcessor",
    "MultimodalProcessor",
    "MultimodalPerceptionEngine",
    "default_image_processor",
    "default_document_processor",
    "default_multimodal_processor",
    "default_multimodal_perception_engine",
]

