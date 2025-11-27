from unittest.mock import MagicMock
import sys

# Mock ollama
sys.modules['ollama'] = MagicMock()
import ollama

def extract_keywords_with_ollama(script_text, model_name="llama3", limit=50):
    """Extracts keywords using Local LLM (Ollama) - Mocked."""
    try:
        # Mock response
        mock_response = {
            'message': {
                'content': "Keyword1, Keyword2, Keyword3"
            }
        }
        ollama.chat.return_value = mock_response
        
        prompt = f"Extract {limit} keywords..."
        response = ollama.chat(model=model_name, messages=[{'role': 'user', 'content': prompt}])
        
        return response['message']['content'].strip()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_ollama_flow():
    print("--- Test Ollama Integration (Mock) ---")
    
    script = "This is a test script about AI and Python."
    result = extract_keywords_with_ollama(script)
    
    print(f"Script: {script}")
    print(f"Result: {result}")
    
    if "Keyword1" in result:
        print("SUCCESS: Mock Ollama called and returned result.")
    else:
        print("FAIL: Result mismatch.")

if __name__ == "__main__":
    test_ollama_flow()
