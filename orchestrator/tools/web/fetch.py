import re
import logging
from typing import Any, Dict, Optional
from urllib.parse import urlparse
import httpx

from orchestrator.tools.interface import BaseTool
from orchestrator.security import SSRFProtector, InputSanitizer

logger = logging.getLogger(__name__)

MAX_FETCH_BYTES = 50000  # 50 KB max content limit
MAX_FETCH_CHARS = 10000  # 10,000 max characters

def clean_html_to_text(html_content: str) -> str:
    """
    Cleans raw HTML markup into plain text content.
    """
    if not html_content:
        return ""

    # Remove script and style elements
    text = InputSanitizer.strip_html_scripts(html_content)
    # Remove remaining HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

class WebFetchTool(BaseTool):
    """
    Web Fetch Tool for fetching textual content from a specified HTTP/HTTPS URL safely.
    Protected against SSRF, private network scanning, and prompt injection attacks.
    """
    def __init__(self, timeout: float = 10.0, max_chars: int = MAX_FETCH_CHARS):
        super().__init__(
            name="web_fetch",
            description="Fetches text content from a given HTTP/HTTPS URL safely.",
            metadata={"category": "research", "permission_tier": 1},
        )
        self.timeout = timeout
        self.max_chars = max_chars

    def execute(self, url: str = "", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Fetches text content from a specified URL with SSRF validation.
        """
        if not url or not isinstance(url, str) or not url.strip():
            raise ValueError("URL must be a non-empty string.")

        target_url = url.strip()

        # Enforce SSRF validation: block loopback, private IP ranges, cloud metadata endpoints
        SSRFProtector.validate_url(target_url)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(target_url, headers=headers)
                response.raise_for_status()

                # Re-validate final URL after redirects against SSRF
                SSRFProtector.validate_url(str(response.url))

                raw_bytes = response.content[:MAX_FETCH_BYTES]
                content_type = response.headers.get("content-type", "").lower()

                if "html" in content_type:
                    cleaned_text = clean_html_to_text(raw_bytes.decode("utf-8", errors="replace"))
                else:
                    cleaned_text = raw_bytes.decode("utf-8", errors="replace").strip()

                truncated_text = cleaned_text[:self.max_chars]
                wrapped_text = InputSanitizer.wrap_untrusted_context(truncated_text, source_label=target_url)

                return {
                    "url": target_url,
                    "content": wrapped_text,
                    "length": len(wrapped_text),
                    "status_code": response.status_code,
                }
        except ValueError as exc:
            raise exc
        except httpx.TimeoutException:
            raise TimeoutError(f"Request to '{target_url}' timed out after {self.timeout} seconds.")
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(f"HTTP Error {exc.response.status_code} while fetching '{target_url}'.")
        except httpx.RequestError as exc:
            raise ConnectionError(f"Failed to connect to '{target_url}': {str(exc)}")
        except Exception as exc:
            raise RuntimeError(f"Error fetching URL '{target_url}': {str(exc)}")
