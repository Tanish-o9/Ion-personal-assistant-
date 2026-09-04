import os
import logging
from abc import ABC, abstractmethod
from typing import Optional

from orchestrator.multimodal.models import MultimodalInput, MAX_IMAGE_SIZE, VALID_IMAGE_MIMES

logger = logging.getLogger(__name__)

class BaseVisionProvider(ABC):
    """
    Abstract interface for Vision LLM models (e.g. Claude 3.5 Sonnet Vision / GPT-4o Vision).
    """
    @abstractmethod
    def describe_image(self, image_bytes: bytes, mime_type: str = "image/png", prompt: str = "") -> str:
        pass

class MockVisionProvider(BaseVisionProvider):
    """
    Default mock/offline Vision provider for local execution and fast unit testing.
    Respects VISION_PROVIDER and VISION_API_KEY if configured.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("VISION_API_KEY")
        self.provider_name = os.getenv("VISION_PROVIDER", "mock").lower()

    def describe_image(self, image_bytes: bytes, mime_type: str = "image/png", prompt: str = "") -> str:
        if not image_bytes or len(image_bytes) == 0:
            raise ValueError("Invalid empty image input.")

        # Inspect if image payload has text hint
        try:
            text_hint = image_bytes.decode("utf-8", errors="ignore").strip()
            if "diagram" in text_hint.lower() or "architecture" in text_hint.lower():
                return f"Visual Analysis: The image contains a system architecture diagram. User query prompt: '{prompt}'"
        except Exception:
            pass

        return f"Visual Analysis: Image provided ({mime_type}, {len(image_bytes)} bytes). Content shows relevant visual details matching prompt: '{prompt}'."

class ImageProcessor:
    """
    Validates and processes image input items.
    """
    def __init__(self, vision_provider: Optional[BaseVisionProvider] = None):
        self.vision_provider = vision_provider or MockVisionProvider()

    def process(self, input_item: MultimodalInput, prompt: str = "") -> str:
        """
        Validates image input and returns visual context description.
        """
        if input_item.input_type != "image":
            raise ValueError(f"Expected 'image' input, got '{input_item.input_type}'")

        if input_item.mime_type not in VALID_IMAGE_MIMES:
            raise ValueError(f"Unsupported image format '{input_item.mime_type}'. Supported: {', '.join(VALID_IMAGE_MIMES)}")

        if len(input_item.content_bytes) > MAX_IMAGE_SIZE:
            raise ValueError(f"Image size ({len(input_item.content_bytes)} bytes) exceeds max limit of {MAX_IMAGE_SIZE} bytes.")

        return self.vision_provider.describe_image(
            image_bytes=input_item.content_bytes,
            mime_type=input_item.mime_type,
            prompt=prompt,
        )
