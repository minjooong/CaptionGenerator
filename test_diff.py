def test_diff_logic():
    print("--- Test Diff Logic ---")
    
    # Simulate segments
    segments = [
        {'text': "안녕하세요 반갑슴니다"}, # Error
        {'text': "이것은 테스트입니다"}   # Correct
    ]
    
    # Simulate Hanspell check
    diffs = []
    corrected_segments = []
    
    for i, seg in enumerate(segments):
        original = seg['text']
        # Mock correction
        if "반갑슴니다" in original:
            corrected = original.replace("반갑슴니다", "반갑습니다")
        else:
            corrected = original
            
        if corrected != original:
            diffs.append({'index': i + 1, 'original': original, 'corrected': corrected})
            
        corrected_segments.append({'text': corrected})
        
    print(f"Diffs Found: {len(diffs)}")
    for diff in diffs:
        print(f"Line {diff['index']}: {diff['original']} -> {diff['corrected']}")
        
    if len(diffs) == 1 and diffs[0]['corrected'] == "안녕하세요 반갑습니다":
        print("SUCCESS: Diff captured correctly.")
    else:
        print("FAIL: Diff logic incorrect.")

if __name__ == "__main__":
    test_diff_logic()
