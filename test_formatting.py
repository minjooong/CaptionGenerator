import re

def format_text(text):
    # Remove punctuation
    text = re.sub(r'[.,?!]', '', text)
    
    # Split lines if too long (simple greedy split)
    if len(text) > 14:
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= 14:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
            
        return "\n".join(lines)
        
    return text

def test_formatting():
    # Case 1: Punctuation removal
    print("--- Case 1: Punctuation ---")
    res = format_text("안녕하세요. 반갑습니다!")
    print(f"Original: '안녕하세요. 반갑습니다!' -> Result: '{res}'")
    
    # Case 2: Line splitting (Short)
    print("\n--- Case 2: Short Line ---")
    res = format_text("짧은 문장입니다")
    print(f"Result: '{res}'")
    
    # Case 3: Line splitting (Long)
    print("\n--- Case 3: Long Line ---")
    # "이것은 아주 긴 문장이라서 줄바꿈이 필요합니다" (22 chars)
    long_text = "이것은 아주 긴 문장이라서 줄바꿈이 필요합니다"
    res = format_text(long_text)
    print(f"Original: '{long_text}'")
    print(f"Result:\n{res}")

if __name__ == "__main__":
    test_formatting()
