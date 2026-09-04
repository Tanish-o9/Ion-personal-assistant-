import logging
from typing import List, Optional
from orchestrator.multimodal.models import MultimodalInput, MultimodalContext
from orchestrator.multimodal.image import ImageProcessor
from orchestrator.multimodal.document import DocumentProcessor

logger = logging.getLogger(__name__)

class MultimodalProcessor:
    """
    Coordinates multimodal input processing across text, images, and documents.
    """
    def __init__(
        self,
        image_processor: Optional[ImageProcessor] = None,
        document_processor: Optional[DocumentProcessor] = None,
    ):
        self.image_processor = image_processor or ImageProcessor()
        self.document_processor = document_processor or DocumentProcessor()

    def process_inputs(self, inputs: List[MultimodalInput], user_query: str = "") -> MultimodalContext:
        """
        Processes a list of MultimodalInputs and constructs a MultimodalContext object.
        """
        if not inputs:
            return MultimodalContext()

        visual_parts = []
        doc_parts = []

        for item in inputs:
            if item.input_type == "image":
                v_desc = self.image_processor.process(item, prompt=user_query)
                visual_parts.append(v_desc)
            elif item.input_type == "document":
                doc_summary, _ = self.document_processor.process(item)
                doc_parts.append(doc_summary)

        visual_context = "\n".join(visual_parts) if visual_parts else ""
        document_context = "\n".join(doc_parts) if doc_parts else ""

        return MultimodalContext(
            visual_context=visual_context,
            document_context=document_context,
        )
