import os
import tempfile
import logging
from typing import Any, Dict, List, Optional, Tuple
from orchestrator.multimodal.models import MultimodalInput, MAX_DOCUMENT_SIZE, VALID_DOC_EXTENSIONS
from orchestrator.knowledge.loader import KnowledgeLoader
from orchestrator.knowledge.models import KnowledgeChunk

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Processes user-supplied text (.txt) and Markdown (.md) documents.
    Reuses Phase 9 KnowledgeLoader for chunking and provides temporary context.
    """
    def __init__(self, loader: Optional[KnowledgeLoader] = None):
        self.loader = loader or KnowledgeLoader(chunk_size=500, chunk_overlap=50)

    def process(self, input_item: MultimodalInput) -> Tuple[str, List[KnowledgeChunk]]:
        """
        Validates uploaded document, extracts text/chunks, and returns (document_context_summary, chunks).
        """
        if input_item.input_type != "document":
            raise ValueError(f"Expected 'document' input, got '{input_item.input_type}'")

        if len(input_item.content_bytes) > MAX_DOCUMENT_SIZE:
            raise ValueError(f"Document size ({len(input_item.content_bytes)} bytes) exceeds max limit of {MAX_DOCUMENT_SIZE} bytes.")

        ext = os.path.splitext(input_item.filename)[1].lower()
        if ext not in VALID_DOC_EXTENSIONS:
            raise ValueError(f"Unsupported document extension '{ext}'. Supported formats: {', '.join(VALID_DOC_EXTENSIONS)}")

        # Write bytes to temporary file for KnowledgeLoader reading
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = os.path.join(tmpdir, input_item.filename)
            with open(tmp_path, "wb") as f:
                f.write(input_item.content_bytes)

            chunks = self.loader.load_file(tmp_path)

        extracted_text = "\n".join([f"[{c.source}] {c.content}" for c in chunks])
        summary = f"Uploaded Document '{input_item.filename}' Content:\n{extracted_text}"

        return summary, chunks
