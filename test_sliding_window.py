from rapidfuzz import process, fuzz
import re

def align_text_with_script(transcribed_text, script_sentences, start_index=0, window_size=20):
    if not script_sentences:
        return transcribed_text, start_index
    
    end_index = min(start_index + window_size, len(script_sentences))
    window_sentences = script_sentences[start_index:end_index]
    
    print(f"DEBUG: Searching in window [{start_index}:{end_index}] -> {window_sentences}")
    
    if not window_sentences:
        return transcribed_text, start_index
        
    best_match = process.extractOne(transcribed_text, window_sentences, scorer=fuzz.ratio)
    
    if best_match:
        match_text, score, relative_index = best_match
        if score > 80:
            absolute_index = start_index + relative_index
            return match_text, absolute_index + 1
            
    return transcribed_text, start_index

def test_sliding_window():
    script = """1. 안녕하세요.
    2. 저는 김민중입니다.
    3. 오늘은 날씨가 좋네요.
    4. 내일도 좋을까요?
    5. 아마 그럴겁니다."""
    
    script_sentences = [s.strip() for s in re.split(r'[.?!]+|\n', script) if s.strip()]
    
    current_index = 0
    
    # Step 1: Match first sentence
    print("--- Step 1 ---")
    res, new_index = align_text_with_script("안녕하세요", script_sentences, current_index, window_size=2)
    print(f"Result: {res}, New Index: {new_index}")
    current_index = new_index
    
    # Step 2: Match third sentence (skipping second)
    print("\n--- Step 2 ---")
    res, new_index = align_text_with_script("오늘은 날씨가 좋네요", script_sentences, current_index, window_size=2)
    print(f"Result: {res}, New Index: {new_index}")
    current_index = new_index
    
    # Step 3: Try to match something far ahead (outside window)
    print("\n--- Step 3 (Outside Window) ---")
    # Window size 2, current index should be 3 (after "오늘은..."). 
    # Sentences: [0:안녕, 1:김민중, 2:오늘, 3:내일, 4:아마]
    # Current index 3 -> Window [3:5] -> ["내일...", "아마..."]
    # If we try to match "김민중" (index 1), it should fail because it's behind.
    res, new_index = align_text_with_script("저는 김민중입니다", script_sentences, current_index, window_size=2)
    print(f"Result: {res}, New Index: {new_index}")

if __name__ == "__main__":
    test_sliding_window()
