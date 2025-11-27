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
    
    stop_words = {'거죠', '거예요', '그런데', '그리고', '그건', '하지만', '그래서'}
    
    processed_words = []
    for w in words:
        if len(w) < 2:
            continue
            
        if w in stop_words:
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
    
    return ", ".join(top_words)

def test_stop_words():
    print("--- Test Stop Words ---")
    
    # "중요" appears once. Stop words appear many times.
    script = "중요 그런데 그리고 하지만 그래서 그건 거죠 거예요"
    
    result = extract_prompt_words(script)
    print(f"Script: {script}")
    print(f"Result: {result}")
    
    if "중요" in result:
        print("SUCCESS: '중요' extracted.")
    else:
        print("FAIL: '중요' missing.")
        
    stop_words = ['거죠', '거예요', '그런데', '그리고', '그건', '하지만', '그래서']
    failed = False
    for sw in stop_words:
        if sw in result:
            print(f"FAIL: Stop word '{sw}' found in result.")
            failed = True
            
    # Check for stripped versions that shouldn't be there if logic is correct
    # "그리" (from 그리고), "하지" (from 하지만)
    if "그리" in result:
         print("FAIL: '그리' (stripped '그리고') found.")
         failed = True
    if "하지" in result:
         print("FAIL: '하지' (stripped '하지만') found.")
         failed = True
            
    if not failed:
        print("SUCCESS: All stop words excluded.")

if __name__ == "__main__":
    test_stop_words()
