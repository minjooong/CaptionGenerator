from rapidfuzz import process, fuzz
import re

def align_text_with_script(transcribed_text, script_text):
    if not script_text:
        return transcribed_text
    
    # Updated splitting logic
    script_sentences = [s.strip() for s in re.split(r'[.?!]+|\n', script_text) if s.strip()]
    
    print(f"DEBUG: Split sentences: {script_sentences}")
    
    best_match = process.extractOne(transcribed_text, script_sentences, scorer=fuzz.ratio)
    
    if best_match:
        match_text, score, index = best_match
        print(f"Transcribed: '{transcribed_text}'")
        print(f"Match: '{match_text}' (Score: {score})")
        if score > 80:
            return match_text
            
    return transcribed_text

def test_alignment():
    script = """안녕하세요! 저는 김민중입니다. 
    오늘은 날씨가 참 좋네요? 그렇죠!
    내일은 비가 올까요."""
    
    # Case 1: Split check
    print("--- Case 1: Splitting Check ---")
    # Should split into: "안녕하세요", "저는 김민중입니다", "오늘은 날씨가 참 좋네요", "그렇죠", "내일은 비가 올까요"
    align_text_with_script("dummy", script)
    
    # Case 2: Matching with punctuation in script
    print("\n--- Case 2: Matching ---")
    res = align_text_with_script("오늘은 날씨가 참 좋네요", script)
    print(f"Result: {res}")

if __name__ == "__main__":
    test_alignment()
