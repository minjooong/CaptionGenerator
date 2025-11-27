class MockWord:
    def __init__(self, word, start, end):
        self.word = word
        self.start = start
        self.end = end

def format_text(text):
    import re
    text = re.sub(r'[^\w\s]', '', text)
    return text

def split_into_segments(words, max_chars=16):
    """Splits a list of words into segments based on character limit and punctuation."""
    segments = []
    current_words = []
    
    for word in words:
        # Check if adding this word exceeds max_chars
        current_len = sum(len(w.word) for w in current_words)
        new_len = current_len + len(word.word)
        
        # Check if previous word ended with sentence-ending punctuation
        force_break = False
        if current_words:
            last_word_text = current_words[-1].word.strip()
            if last_word_text.endswith('.') or last_word_text.endswith('?'):
                force_break = True
        
        if (new_len > max_chars and current_words) or force_break:
            # Finalize current segment
            start = current_words[0].start
            end = current_words[-1].end
            text = "".join([w.word for w in current_words])
            formatted_text = format_text(text).strip()
            
            segments.append({
                'start': start,
                'end': end,
                'text': formatted_text
            })
            
            # Start new segment
            current_words = [word]
        else:
            current_words.append(word)
                
    # Append last segment
    if current_words:
        start = current_words[0].start
        end = current_words[-1].end
        text = "".join([w.word for w in current_words])
        formatted_text = format_text(text).strip()
        segments.append({
            'start': start,
            'end': end,
            'text': formatted_text
        })
        
    return segments

def test_split():
    print("--- Test Punctuation Split ---")
    
    # "안녕하세요." (short) "반갑습니다." (short)
    words = [
        MockWord("안녕하세요.", 0, 1),
        MockWord(" ", 1, 1.1),
        MockWord("반갑습니다.", 1.1, 2)
    ]
    
    # Even though "안녕하세요. 반갑습니다." is < 16 chars, it should split because of '.'
    segments = split_into_segments(words, max_chars=50)
    
    print(f"Segments found: {len(segments)}")
    for i, seg in enumerate(segments):
        print(f"Seg {i+1}: {seg['text']}")
        
    if len(segments) == 2:
        print("SUCCESS: Split on punctuation.")
    else:
        print("FAIL: Did not split.")

if __name__ == "__main__":
    test_split()
