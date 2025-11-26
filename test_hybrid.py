import re

def format_text(text):
    # Remove punctuation except " ' ,
    text = re.sub(r'[.?!\-;:]', '', text)
    return text

class MockWord:
    def __init__(self, word, start, end):
        self.word = word
        self.start = start
        self.end = end

class MockSegment:
    def __init__(self, text, start, end, words):
        self.text = text
        self.start = start
        self.end = end
        self.words = words

def split_into_segments(words, max_chars=14):
    segments = []
    current_words = []
    
    for word in words:
        candidate_words = current_words + [word]
        candidate_text = "".join([w.word for w in candidate_words])
        formatted_candidate = format_text(candidate_text).strip()
        
        if current_words and len(formatted_candidate) > max_chars:
            start = current_words[0].start
            end = current_words[-1].end
            text = "".join([w.word for w in current_words])
            formatted_text = format_text(text).strip()
            
            segments.append({
                'start': start,
                'end': end,
                'text': formatted_text
            })
            current_words = [word]
        else:
            current_words.append(word)
                
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

def test_hybrid_segmentation():
    # Case 1: Short segment (should keep as is)
    seg1 = MockSegment("안녕하세요", 0.0, 1.0, [MockWord("안녕하세요", 0.0, 1.0)])
    
    # Case 2: Long segment (should split)
    # "저는 김민중입니다 반갑습니다" (13 chars? No. "저는"(2) "김민중입니다"(6) "반갑습니다"(5) = 13 + spaces? 
    # Let's make it definitely long.
    # "이것은 아주 긴 문장이라서 반드시 잘라야 합니다" (25 chars)
    words2 = [
        MockWord("이것은", 2.0, 2.5),
        MockWord("아주", 2.5, 3.0),
        MockWord("긴", 3.0, 3.5),
        MockWord("문장이라서", 3.5, 4.5),
        MockWord("반드시", 4.5, 5.0),
        MockWord("잘라야", 5.0, 5.5),
        MockWord("합니다", 5.5, 6.0)
    ]
    seg2 = MockSegment("이것은 아주 긴 문장이라서 반드시 잘라야 합니다", 2.0, 6.0, words2)
    
    segments = [seg1, seg2]
    processed_segments = []
    
    print("--- Test Hybrid Segmentation ---")
    for segment in segments:
        formatted_text = format_text(segment.text).strip()
        if len(formatted_text) <= 14:
            print(f"Keeping short segment: '{formatted_text}'")
            processed_segments.append({'text': formatted_text})
        else:
            print(f"Splitting long segment: '{formatted_text}'")
            sub_segments = split_into_segments(segment.words, max_chars=14)
            for sub in sub_segments:
                print(f"  -> Sub-segment: '{sub['text']}'")
            processed_segments.extend(sub_segments)

if __name__ == "__main__":
    test_hybrid_segmentation()
