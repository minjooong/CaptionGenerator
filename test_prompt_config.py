import re
from collections import Counter

def extract_prompt_words(script_text, limit=50):
    if not script_text:
        return None
    words = re.findall(r'\w+', script_text)
    suffixes = [
        '에게서', '에서는', '에서도', '이라는', '이라고', '으로는', '으로도', '까지는', '까지도', '부터는', '부터도',
        '에서는', '에게는', '에게도', '한테는', '한테도', '께서는', '께서는', '입니다', '습니다', '합니다', '하고는',
        '에게', '에서', '으로', '까지', '부터', '한테', '께서', '처럼', '하고', '이나', '이랑', '이라', '와는', '과는',
        '은', '는', '이', '가', '을', '를', '의', '에', '로', '와', '과', '도', '만', '나', '랑', '야', '여', '라', '고'
    ]
    processed_words = []
    for w in words:
        if len(w) < 2:
            continue
        stripped = w
        for suffix in suffixes:
            if stripped.endswith(suffix):
                if len(stripped) > len(suffix):
                    stripped = stripped[:-len(suffix)]
                    break
        if len(stripped) >= 2:
            processed_words.append(stripped)
    
    counter = Counter(processed_words)
    top_tuples = counter.most_common(limit)
    top_words = [word for word, count in top_tuples]
    
    final_words = []
    current_len = 0
    max_len = 800
    for word in top_words:
        if current_len + len(word) + 2 > max_len:
            break
        final_words.append(word)
        current_len += len(word) + 2
    
    return ", ".join(final_words)

def test_config():
    print("--- Test Prompt Config ---")
    
    # Test Limit
    script = "단어 " * 100 # "단어" repeated
    # Actually need different words to test limit
    script_many = " ".join([f"word{i}" for i in range(100)])
    
    res_50 = extract_prompt_words(script_many, limit=50)
    count_50 = len(res_50.split(", "))
    print(f"Limit 50 count: {count_50}")
    if count_50 == 50:
        print("SUCCESS: Limit 50 respected.")
    else:
        print(f"FAIL: Limit 50 got {count_50}")
        
    res_10 = extract_prompt_words(script_many, limit=10)
    count_10 = len(res_10.split(", "))
    print(f"Limit 10 count: {count_10}")
    if count_10 == 10:
        print("SUCCESS: Limit 10 respected.")
        
    # Test Optimization (Length)
    # Create very long words
    long_word = "A" * 100
    script_long = " ".join([f"{long_word}{i}" for i in range(20)]) # 20 * 100 = 2000 chars
    
    res_long = extract_prompt_words(script_long, limit=20)
    print(f"Long script result length: {len(res_long)}")
    if len(res_long) <= 800:
        print("SUCCESS: Length optimization respected.")
    else:
        print(f"FAIL: Length {len(res_long)} > 800")

if __name__ == "__main__":
    test_config()
