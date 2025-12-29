# test_llm.py
from llm_interface import LocalLLMInterface

# Initialize LLM interface
llm = LocalLLMInterface(
    backend="ollama",       # or "vllm" if using vLLM
    model="llama3:instruct",
    temperature=0.2,
    max_tokens=200
)

# Hardcoded prompt for testing
prompt = """
You are an expert assistant. Answer the following question:
What are the key factors driving revenue growth in a company?
Use logical reasoning.
"""

# Generate response
full_response = []
for text_chunk in llm.stream_response(prompt):
    print(text_chunk, end="", flush=True) # Print each piece with no newline
    full_response.append(text_chunk) 