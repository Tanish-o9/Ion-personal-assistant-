import os
from typing import List, Optional
from orchestrator.knowledge.models import KnowledgeChunk

class KnowledgeLoader:
    """
    Loads text (.txt) and Markdown (.md) documents and splits them into KnowledgeChunks.
    """
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        """
        Splits text into chunks of specified size and overlap.
        """
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text.strip()]

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap

        return chunks

    def load_file(self, filepath: str) -> List[KnowledgeChunk]:
        """
        Reads a single file (.txt or .md) and returns its KnowledgeChunks.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: '{filepath}'")

        ext = os.path.splitext(filepath)[1].lower()
        if ext not in {".txt", ".md"}:
            return []

        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            raw_text = f.read()

        raw_chunks = self.split_text(raw_text)
        chunks = []

        for idx, chunk_text in enumerate(raw_chunks):
            chunk = KnowledgeChunk(
                content=chunk_text,
                source=filename,
                metadata={
                    "filepath": filepath,
                    "filename": filename,
                    "chunk_index": idx,
                    "total_chunks": len(raw_chunks),
                    "file_type": ext,
                },
            )
            chunks.append(chunk)

        return chunks

    def load_directory(self, dirpath: str) -> List[KnowledgeChunk]:
        """
        Recursively scans a directory for .txt and .md files and loads all chunks.
        """
        if not os.path.exists(dirpath):
            return []

        all_chunks: List[KnowledgeChunk] = []
        for root, _, files in os.walk(dirpath):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in {".txt", ".md"}:
                    full_path = os.path.join(root, file)
                    all_chunks.extend(self.load_file(full_path))

        return all_chunks
