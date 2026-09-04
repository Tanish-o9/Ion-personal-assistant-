"""
Cross-Phase End-to-End Integration Tests for JARVIS 4.0 (Phases 66–70).
"""

import pytest
from database.connection import init_db
from orchestrator.context import default_cognitive_manager
from orchestrator.personalization import default_personal_twin_manager
from orchestrator.voice import default_voice_streaming_pipeline, VoiceEventType
from orchestrator.multimodal import default_multimodal_perception_engine
from orchestrator.connectors import default_universal_connector_sdk, PermissionScope

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

def test_jarvis_4_integrated_flow():
    user_id = "user_jarvis_4"
    session_id = "sess_jarvis_4"

    # 1. Cognitive Context Assembly
    cog = default_cognitive_manager.assemble_cognitive_context(
        user_id=user_id,
        session_id=session_id,
        current_request="Analyze image and update connector"
    )
    assert cog.user_id == user_id

    # 2. Personal AI Twin Working-Style Resolution
    default_personal_twin_manager.update_working_style(user_id, {"response_preferences": "concise"})
    pref = default_personal_twin_manager.resolve_effective_preference(user_id)
    assert pref["response_style"] == "concise"

    # 3. Multimodal Context Perception
    multi_ctx = default_multimodal_perception_engine.assemble_and_sanitize_context(
        text_prompt="Analyze provided diagram",
        image_paths=["/tmp/diagram.png"]
    )
    assert "image" in multi_ctx.supported_modalities

    # 4. Natural Voice Stream Event
    voice_evt = default_voice_streaming_pipeline.process_streaming_transcript(session_id, "Explain diagram concise", is_final=True)
    assert voice_evt.event_type == VoiceEventType.TRANSCRIPT_FINAL

    # 5. Universal Connector SDK Execution
    conn_desc = default_universal_connector_sdk.register_connector_definition(
        name="Docs Connector",
        provider="DocsApp",
        capabilities=["write_doc"],
        permissions=[PermissionScope.CREATE],
        risk_level="LOW"
    )
    conn_res = default_universal_connector_sdk.execute_connector_operation(
        conn_desc.connector_id,
        user_id,
        "create",
        {"content": multi_ctx.sanitized_prompt}
    )
    assert conn_res["status"] == "success"
