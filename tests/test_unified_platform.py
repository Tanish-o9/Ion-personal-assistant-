"""
Unit & Integration Tests for Phase 65: JARVIS 3.0 Final Unified Platform.
"""

import pytest
from orchestrator.platform.unified import (
    UnifiedCapabilityPipeline,
    JarvisErrorCategory,
)

def test_unified_capability_execution_pipeline():
    pipeline = UnifiedCapabilityPipeline()
    user_id = "user_unified_1"

    # Successful execution
    res = pipeline.execute_capability(
        user_id=user_id,
        capability_name="calculator",
        capability_type="tool",
        payload={"expression": "10 + 20"}
    )
    assert res.status == "SUCCESS"
    assert res.error_category is None
    assert res.result["executed"] is True

def test_unified_pipeline_error_categorization():
    pipeline = UnifiedCapabilityPipeline()
    user_id = "user_unified_2"

    # Input blocked by guardrails -> VALIDATION_ERROR
    res_blocked = pipeline.execute_capability(
        user_id=user_id,
        capability_name="chat",
        capability_type="tool",
        payload=""  # Empty payload triggers guardrail rejection
    )
    # Check that status is REJECTED and error category is correctly categorized
    assert res_blocked.status == "REJECTED"
    assert res_blocked.error_category == JarvisErrorCategory.VALIDATION_ERROR

