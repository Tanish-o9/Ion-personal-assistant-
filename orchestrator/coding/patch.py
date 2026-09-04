import difflib
from typing import Any, Dict
from pydantic import BaseModel

class PatchResult(BaseModel):
    file_path: str
    original_content: str
    new_content: str
    diff: str

class PatchGenerator:
    """
    Generates structured code diffs and validates patch paths without shell execution.
    """
    @staticmethod
    def generate_patch(file_path: str, original_content: str, new_content: str) -> PatchResult:
        orig_lines = original_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)

        diff = "".join(
            difflib.unified_diff(
                orig_lines,
                new_lines,
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
            )
        )

        return PatchResult(
            file_path=file_path,
            original_content=original_content,
            new_content=new_content,
            diff=diff or "No changes detected.",
        )
