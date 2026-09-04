import pytest
from orchestrator.multimodal.unified_context import (
    InteractionRequest, ContextStreamItem, UnifiedMultimodalContext,
    ModalityRouter, CrossModalEvidenceTree, VoiceMultimodalPipeline,
    ContextBudgetManager, PrivacyTracker
)

def test_interaction_request_and_context():
    req = InteractionRequest(
        user_id="u1",
        session_id="s1",
        text="What does this image show?",
        images=["data:image/png;base64,123"]
    )
    context = UnifiedMultimodalContext()
    context.add_item("visual", ContextStreamItem(source="camera", content="An image of a cat"))
    summary = context.get_summary()
    assert summary["visual"] == 1
    assert summary["text"] == 0

def test_modality_router():
    router = ModalityRouter()
    req = InteractionRequest(user_id="u1", session_id="s1", text="Summarize this PDF document and check device status")
    modalities = router.determine_required_modalities(req)
    assert "DOCUMENT" in modalities
    assert "DEVICE" in modalities

def test_cross_modal_evidence_tree():
    tree = CrossModalEvidenceTree()
    tree.add_evidence("VISION", "Image 1", "Cat sitting on couch", 0.95)
    tree.add_evidence("DOCUMENT", "Vet Report.pdf", "Feline health normal", 0.90)
    panel = tree.format_evidence_panel()
    assert panel["total_nodes"] == 2
    assert "VISION" in panel["modalities"]

def test_voice_multimodal_pipeline():
    pipeline = VoiceMultimodalPipeline()
    context = UnifiedMultimodalContext()
    res = pipeline.process_voice_interaction(b"audio_bytes", context)
    assert res["status"] == "COMPLETED"
    assert res["tts_audio_generated"] is True

def test_context_budget_manager():
    budget = ContextBudgetManager(max_images=2)
    req = InteractionRequest(user_id="u1", session_id="s1", images=["img1", "img2", "img3"])
    with pytest.raises(ValueError):
        budget.validate_request_budget(req)

def test_privacy_tracker():
    tracker = PrivacyTracker()
    tracker.track_processing("VISION", is_local=True, scope="SESSION")
    assert len(tracker.log) == 1
    assert tracker.log[0]["is_local"] is True
