from unittest.mock import MagicMock
import sys
import os

# Mock google.generativeai
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
import google.generativeai as genai

# Mock dotenv
sys.modules['dotenv'] = MagicMock()
from dotenv import load_dotenv

def extract_keywords_with_gemini(script_text, limit=50):
    """Extracts keywords using Google Gemini API - Mocked."""
    # Simulate env var
    os.environ['GEMINI_API_KEY'] = 'fake_key'
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: API Key missing")
        return None
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Mock response
        mock_response = MagicMock()
        mock_response.text = "Keyword1, Keyword2, Keyword3"
        model.generate_content.return_value = mock_response
        
        prompt = f"Extract {limit} keywords..."
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_gemini_flow():
    print("--- Test Gemini Extraction (Mock) ---")
    
    script = "This is a test script about AI and Python."
    result = extract_keywords_with_gemini(script)
    
    print(f"Script: {script}")
    print(f"Result: {result}")
    
    if "Keyword1" in result:
        print("SUCCESS: Mock Gemini called and returned result.")
    else:
        print("FAIL: Result mismatch.")

if __name__ == "__main__":
    test_gemini_flow()
