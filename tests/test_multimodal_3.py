"""
Unit Tests for Phase 69: Multimodal Perception 3.0.
"""

import pytest
from orchestrator.multimodal.unified import MultimodalPerceptionEngine

def test_multimodal_context_assembly_and_routing():
    engine = MultimodalPerceptionEngine()

    ctx = engine.assemble_and_sanitize_context(
        text_prompt="Summarize chart in image and report in doc",
        image_paths=["/tmp/chart.png"],
        document_paths=["/tmp/report.pdf"],
        audio_transcripts=["User audio question: Explain the summary"]
    )

    assert "text" in ctx.supported_modalities
    assert "image" in ctx.supported_modalities
    assert "document" in ctx.supported_modalities
    assert "audio" in ctx.supported_modalities

    # Prompt injection boundary verification
    assert "--- START UNTRUSTED DATA" in ctx.sanitized_prompt

    # Modality routing check
    text_only_models = ["gpt-3.5-turbo"]
    multimodal_models = ["image", "document", "audio"]

    assert engine.route_modality_model(ctx, text_only_models) is False
    assert engine.route_modality_model(ctx, multimodal_models) is True

def test_multimodal_attachment_limit():
    engine = MultimodalPerceptionEngine()

    with pytest.raises(ValueError, match="Attachment count exceeds limit"):
        engine.assemble_and_sanitize_context(
            text_prompt="Too many files",
            image_paths=[f"/tmp/img_{i}.png" for i in range(15)]
        )
