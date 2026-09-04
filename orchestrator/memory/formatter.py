from typing import Any, Dict, List, Union
from orchestrator.memory.store import MemoryRecord

def format_memories_for_context(memories: List[Union[MemoryRecord, Dict[str, Any]]]) -> str:
    """
    Converts a list of MemoryRecords (or memory dictionaries) into a clean,
    prompt-ready text format for agent context injection.
    """
    if not memories:
        return ""

    lines = ["Relevant user memories:"]
    for item in memories:
        if isinstance(item, MemoryRecord):
            category = item.memory_type.upper()
            content = item.content
        elif isinstance(item, dict):
            category = item.get("memory_type", "preference").upper()
            content = item.get("content", "")
        else:
            continue

        if content:
            lines.append(f"- [{category}] {content}")

    if len(lines) == 1:
        return ""

    return "\n".join(lines)
