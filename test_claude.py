import os
from dotenv import load_dotenv
from ai import AIEngine

load_dotenv()
engine = AIEngine(os.getenv('CLAUDE_API_KEY'), os.getenv('HF_API_KEY'))
print('claude key present:', bool(engine.claude_api_key) and not engine.claude_api_key.startswith('YOUR_'))
print('hf key present:', bool(engine.hf_api_key) and not engine.hf_api_key.startswith('YOUR_'))
prompt = 'Hello Jarvis, test model response.'
print('sending prompt...')
result = engine.query_claude(prompt)
print('claude result:')
print(result)
