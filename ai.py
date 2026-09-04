import logging

import requests

logger = logging.getLogger(__name__)


class AIEngine:
    def __init__(self, claude_api_key, hf_api_key):
        self.claude_api_key = claude_api_key
        self.hf_api_key = hf_api_key
        self.local_generator = None

    def query_claude(self, prompt, model_name='claude-3-5-sonnet-20241022'):
        if not self.claude_api_key or self.claude_api_key.startswith('YOUR_'):
            return None

        try:
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': self.claude_api_key,
                    'anthropic-version': '2023-06-01',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': model_name,
                    'messages': [{'role': 'user', 'content': prompt}],
                    'max_tokens': 1024,
                },
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, dict):
                content = payload.get('content')
                if isinstance(content, list) and len(content) > 0:
                    return content[0].get('text')
            return None
        except requests.RequestException as exc:
            logger.warning('Claude request failed: %s', exc)
            if exc.response is not None:
                logger.warning('Response body: %s', exc.response.text)
            return None
        except (ValueError, KeyError, TypeError) as exc:
            logger.warning('Claude response JSON parse/access failed: %s', exc)
            return None

    def query_huggingface(self, prompt, model='gpt2'):
        if not self.hf_api_key or self.hf_api_key.startswith('YOUR_'):
            return None

        try:
            response = requests.post(
                f'https://api-inference.huggingface.co/models/{model}',
                headers={'Authorization': f'Bearer {self.hf_api_key}'},
                json={'inputs': prompt},
                timeout=30,
            )
            payload = response.json()
            if isinstance(payload, dict) and payload.get('error'):
                logger.warning('Hugging Face inference error: %s', payload.get('error'))
                return None
            if isinstance(payload, list) and payload and isinstance(payload[0], dict):
                return payload[0].get('generated_text')
            if isinstance(payload, dict):
                return payload.get('generated_text')
            return None
        except Exception as exc:
            logger.warning('Hugging Face inference failed: %s', exc)
            return None

    def query_local(self, prompt, model='gpt2', max_new_tokens=50, num_return_sequences=1):
        if self.local_generator is None:
            try:
                from transformers import pipeline
                self.local_generator = pipeline(
                    'text-generation',
                    model=model,
                    device=0 if self._has_cuda() else -1,
                )
            except Exception as exc:
                logger.warning('Local model initialization failed: %s', exc)
                return None

        try:
            results = self.local_generator(
                prompt,
                max_new_tokens=max_new_tokens,
                num_return_sequences=num_return_sequences,
            )
            if isinstance(results, list) and results:
                return results[0].get('generated_text')
            return None
        except Exception as exc:
            logger.warning('Local generation failed: %s', exc)
            return None

    def _has_cuda(self):
        try:
            import torch
            return torch.cuda.is_available()
        except Exception:
            return False

    def get_response(self, prompt, model='claude'):
        fallback = 'Sorry, Jarvis is temporarily unable to access the AI service.'

        if model == 'claude':
            return (
                self.query_claude(prompt)
                or self.query_huggingface(prompt, model='gpt2')
                or self.query_local(prompt)
                or fallback
            )

        if model in ['huggingFace', 'hf', 'gpt2']:
            return (
                self.query_huggingface(prompt, model='gpt2')
                or self.query_claude(prompt)
                or self.query_local(prompt)
                or fallback
            )

        return (
            self.query_claude(prompt)
            or self.query_huggingface(prompt, model='gpt2')
            or self.query_local(prompt)
            or fallback
        )
