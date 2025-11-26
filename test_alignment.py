from rapidfuzz import process, fuzz

def align_text_with_script(transcribed_text, script_text):
    if not script_text:
        return transcribed_text
    
    script_sentences = script_text.replace('\n', ' ').split('. ')
    
    best_match = process.extractOne(transcribed_text, script_sentences, scorer=fuzz.ratio)
    
    if best_match:
        match_text, score, index = best_match
        print(f"Transcribed: '{transcribed_text}'")
        print(f"Match: '{match_text}' (Score: {score})")
        if score > 80:
            return match_text
            
    return transcribed_text

def test_alignment():
    script = "안녕하세요. 저는 김민중입니다. 오늘은 날씨가 참 좋네요."
    
    # Case 1: Exact match
    print("--- Case 1 ---")
    res = align_text_with_script("안녕하세요", script)
    print(f"Result: {res}")
    
    # Case 2: Typo (Name)
    print("\n--- Case 2 ---")
    res = align_text_with_script("저는 김민종입니다", script) # '중' -> '종'
    print(f"Result: {res}")
    
    # Case 3: Low similarity (Improvised)
    print("\n--- Case 3 ---")
    res = align_text_with_script("갑자기 비가 오네요", script)
    print(f"Result: {res}")

if __name__ == "__main__":
    test_alignment()
