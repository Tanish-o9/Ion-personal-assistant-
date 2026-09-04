import base64
import pytest
from fastapi.testclient import TestClient

from orchestrator.multimodal.models import MultimodalInput, MultimodalContext
from orchestrator.multimodal.image import ImageProcessor, MockVisionProvider
from orchestrator.multimodal.document import DocumentProcessor
from orchestrator.multimodal.processor import MultimodalProcessor
from orchestrator.llm_client import LLMClient, LLMResponse
from orchestrator.graph import build_orchestrator_graph
from api.main import app

class MockLLM(LLMClient):
    async def generate(self, messages, system_prompt=None, model_name="claude-3-5-sonnet-20241022"):
        return LLMResponse(
            text="Based on the diagram provided, this system consists of a multi-agent supervisor graph.",
            model_used="mock-llm",
            token_count=12,
            latency_ms=5.0,
        )

# ---------------------------------------------------------------------------
# 1. Multimodal Model Unit Tests
# ---------------------------------------------------------------------------

def test_multimodal_input_models():
    input_item = MultimodalInput(
        input_type="image",
        content_bytes=b"fake_image_bytes",
        filename="architecture_diagram.png",
        mime_type="image/png",
    )
    assert input_item.input_type == "image"
    assert input_item.filename == "architecture_diagram.png"
    assert input_item.mime_type == "image/png"

    with pytest.raises(ValueError, match="Invalid input_type"):
        MultimodalInput(input_type="audio_video", content_bytes=b"data")

# ---------------------------------------------------------------------------
# 2. ImageProcessor Unit Tests
# ---------------------------------------------------------------------------

def test_image_processor_valid_and_invalid():
    processor = ImageProcessor(vision_provider=MockVisionProvider())

    item_valid = MultimodalInput(input_type="image", content_bytes=b"png_bytes", mime_type="image/png")
    desc = processor.process(item_valid, prompt="Explain diagram")
    assert "Visual Analysis" in desc

    item_invalid_mime = MultimodalInput(input_type="image", content_bytes=b"gif_bytes", mime_type="image/gif")
    with pytest.raises(ValueError, match="Unsupported image format"):
        processor.process(item_invalid_mime)

    item_oversized = MultimodalInput(input_type="image", content_bytes=b"x" * (11 * 1024 * 1024), mime_type="image/png")
    with pytest.raises(ValueError, match="exceeds max limit"):
        processor.process(item_oversized)

# ---------------------------------------------------------------------------
# 3. DocumentProcessor Unit Tests
# ---------------------------------------------------------------------------

def test_document_processor_txt_and_md():
    doc_proc = DocumentProcessor()

    item_md = MultimodalInput(
        input_type="document",
        content_bytes=b"# Architecture\nJARVIS scales using multi-agent supervision.",
        filename="design.md",
        mime_type="text/markdown",
    )
    summary, chunks = doc_proc.process(item_md)
    assert "Uploaded Document 'design.md'" in summary
    assert len(chunks) == 1
    assert chunks[0].source == "design.md"

    item_pdf = MultimodalInput(input_type="document", content_bytes=b"pdf", filename="file.pdf")
    with pytest.raises(ValueError, match="Unsupported document extension"):
        doc_proc.process(item_pdf)

# ---------------------------------------------------------------------------
# 4. MultimodalProcessor Coordination Tests
# ---------------------------------------------------------------------------

def test_multimodal_processor_combination():
    mm_proc = MultimodalProcessor()
    img_item = MultimodalInput(input_type="image", content_bytes=b"png_bytes", mime_type="image/png")
    doc_item = MultimodalInput(input_type="document", content_bytes=b"Documentation notes", filename="notes.txt")

    context = mm_proc.process_inputs([img_item, doc_item], user_query="Explain this")
    assert len(context.visual_context) > 0
    assert "Uploaded Document 'notes.txt'" in context.document_context

# ---------------------------------------------------------------------------
# 5. Graph Integration Test (Visual Context Injection)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_graph_multimodal_visual_context():
    mock_llm = MockLLM()
    graph = build_orchestrator_graph(mock_llm)
    config = {"configurable": {"thread_id": "session-mm-1"}}

    inputs = {
        "messages": [{"role": "user", "content": "Explain this diagram"}],
        "session_id": "session-mm-1",
        "user_id": "mm_user_1",
        "active_memory": [],
        "pending_action": None,
        "tool_round_count": 0,
        "visual_context": "Visual Analysis: Architecture diagram showing supervisor node and worker agents.",
        "document_context": None,
    }

    final_state = await graph.ainvoke(inputs, config=config)
    messages = final_state.get("messages", [])
    last_content = messages[-1].content if hasattr(messages[-1], "content") else messages[-1]["content"]
    assert "multi-agent supervisor graph" in last_content

# ---------------------------------------------------------------------------
# 6. REST API Test (POST /chat with multimodal file payloads)
# ---------------------------------------------------------------------------

def test_api_chat_multimodal_payload():
    client = TestClient(app)
    reg_res = client.post("/auth/register", json={"username": "mm_user", "password": "mmpassword"}).json()
    token = reg_res["token"]

    img_b64 = base64.b64encode(b"architecture_diagram_png").decode("ascii")

    res = client.post(
        "/chat",
        json={
            "text": "What is shown in this diagram?",
            "files": [
                {
                    "input_type": "image",
                    "filename": "diagram.png",
                    "mime_type": "image/png",
                    "content_base64": img_b64,
                }
            ]
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "session_id" in data
    assert len(data["response"]) > 0
