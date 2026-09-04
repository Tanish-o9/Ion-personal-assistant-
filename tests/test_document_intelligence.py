import pytest
from orchestrator.documents import (
    DocumentIntelligencePipeline,
    DocumentComparator,
    DocumentGenerator,
)

def test_document_pipeline_parsing():
    content = b"## Architecture Overview\nJARVIS AT SCALE document pipeline."
    doc = DocumentIntelligencePipeline.parse_document("architecture.md", content)

    assert doc.filename == "architecture.md"
    assert doc.file_type == "md"
    assert len(doc.sections) >= 1
    assert "JARVIS AT SCALE" in doc.sections[0].content

def test_spreadsheet_parsing():
    content = b"Header1,Header2\nVal1,Val2"
    doc = DocumentIntelligencePipeline.parse_document("data.xlsx", content)

    assert doc.file_type == "xlsx"
    assert len(doc.tables) >= 1

def test_document_comparison():
    doc1 = DocumentIntelligencePipeline.parse_document("doc1.txt", b"Original content section A")
    doc2 = DocumentIntelligencePipeline.parse_document("doc2.txt", b"Updated content section B")

    comp = DocumentComparator.compare(doc1, doc2)
    assert comp.doc1_name == "doc1.txt"
    assert comp.doc2_name == "doc2.txt"

def test_document_generation():
    gen = DocumentGenerator.generate_document(
        filename="report",
        content="# Final Report\nJARVIS document analysis completed.",
        user_id="user_doc_1",
        format_type="markdown",
    )
    assert gen["filename"] == "report.md"
    assert gen["user_id"] == "user_doc_1"
    assert "Final Report" in gen["content"]
