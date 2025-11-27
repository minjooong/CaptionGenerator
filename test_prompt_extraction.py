import re

def extract_prompt_words(script_text):
    """Extracts important words from script for Whisper prompt."""
    if not script_text:
        return None
        
    # Normalize and split
    words = re.findall(r'\w+', script_text)
    # Filter: len >= 2
    long_words = [w for w in words if len(w) >= 2]
    # Unique preserving order
    unique_words = list(dict.fromkeys(long_words))
    # Take first 100
    top_100 = unique_words[:100]
    # Join with commas for a keyword list style prompt
    return ", ".join(top_100)

def test_extraction():
    print("--- Test Prompt Extraction ---")
    
    script = "안녕하세요. 저는 AI입니다. 테스트를 진행합니다."
    expected = "안녕하세요, 저는, AI입니다, 테스트를, 진행합니다"
    
    result = extract_prompt_words(script)
    print(f"Script: {script}")
    print(f"Result: {result}")
    
    if result == expected:
        print("SUCCESS: Extraction matches expected output.")
    else:
        print("FAIL: Extraction mismatch.")

if __name__ == "__main__":
    test_extraction()
