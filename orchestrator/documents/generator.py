import os
from typing import Any, Dict

class DocumentGenerator:
    """
    Generates structured output documents (TXT, Markdown, report files) safely with user ownership metadata.
    """
    @staticmethod
    def generate_document(filename: str, content: str, user_id: str, format_type: str = "markdown") -> Dict[str, Any]:
        ext = "md" if format_type == "markdown" else "txt"
        out_filename = f"{filename}.{ext}" if not filename.endswith(f".{ext}") else filename

        header = f"<!-- Owner: {user_id} | Format: {format_type} -->\n"
        full_content = header + content

        return {
            "filename": out_filename,
            "format": format_type,
            "user_id": user_id,
            "content": full_content,
            "size_bytes": len(full_content.encode("utf-8")),
        }
