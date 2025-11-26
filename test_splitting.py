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

def split_into_segments(words, max_chars=14):
    segments = []
    current_words = []
    current_len = 0
    
    for word in words:
        cleaned_word_text = format_text(word.word).strip()
        word_len = len(cleaned_word_text)
        
        if current_words and (current_len + 1 + word_len > max_chars):
            start = current_words[0].start
            end = current_words[-1].end
            text = "".join([w.word for w in current_words]).strip()
            formatted_text = format_text(text).strip()
            
            segments.append({
                'start': start,
                'end': end,
                'text': formatted_text
            })
            
            current_words = [word]
            current_len = word_len
        else:
            current_words.append(word)
            if current_len == 0:
                current_len = word_len
            else:
                current_len += 1 + word_len
                
    if current_words:
        start = current_words[0].start
        end = current_words[-1].end
        text = "".join([w.word for w in current_words]).strip()
        formatted_text = format_text(text).strip()
        segments.append({
            'start': start,
            'end': end,
            'text': formatted_text
        })
        
    return segments

def test_splitting():
    # "안녕하세요. 저는 김민중입니다. 반갑습니다!"
    # Words: "안녕하세요.", "저는", "김민중입니다.", "반갑습니다!"
    words = [
        MockWord("안녕하세요.", 0.0, 1.0),
        MockWord("저는", 1.0, 1.5),
        MockWord("김민중입니다.", 1.5, 2.5),
        MockWord("반갑습니다!", 2.5, 3.5)
    ]
    
    # Expected:
    # "안녕하세요" (5 chars) -> OK
    # "저는" (2 chars) -> "안녕하세요 저는" (8 chars) -> OK
    # "김민중입니다" (6 chars) -> "안녕하세요 저는 김민중입니다" (15 chars) -> Too long!
    # So split:
    # Seg 1: "안녕하세요 저는"
    # Seg 2: "김민중입니다 반갑습니다" (6+1+5 = 12 chars) -> OK
    
    print("--- Test Splitting ---")
    segments = split_into_segments(words, max_chars=14)
    for i, seg in enumerate(segments):
        print(f"Seg {i+1}: '{seg['text']}' ({seg['start']} -> {seg['end']})")

if __name__ == "__main__":
    test_splitting()
