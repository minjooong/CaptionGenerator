import re
from collections import Counter

def extract_prompt_words(script_text):
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
    top_100_tuples = counter.most_common(100)
    top_100_words = [word for word, count in top_100_tuples]
    return ", ".join(top_100_words)

def test_stripping():
    print("--- Test Particle Stripping ---")
    
    # "학교에서", "학교는", "학교가" -> Should all map to "학교" (count 3)
    # "선생님은", "선생님이" -> "선생님" (count 2)
    script = "학교에서 학교는 학교가 선생님은 선생님이 학생"
    
    result = extract_prompt_words(script)
    print(f"Script: {script}")
    print(f"Result: {result}")
    
    if result.startswith("학교"):
        print("SUCCESS: '학교' is most frequent.")
    else:
        print("FAIL: Stripping failed.")
        
    if "선생님" in result:
        print("SUCCESS: '선생님' extracted.")
        
    # Test verb ending
    script_verb = "합니다 갑니다 놉니다" # -> 하, 갑, 놉 (len 1, filtered out?)
    # "합니다" -> "하" (len 1) -> Filtered out
    # "공부합니다" -> "공부" (len 2) -> Kept
    script_verb2 = "공부합니다 운동합니다"
    result_verb = extract_prompt_words(script_verb2)
    print(f"Verbs: {result_verb}")
    if "공부" in result_verb and "운동" in result_verb:
        print("SUCCESS: Verb endings stripped.")

if __name__ == "__main__":
    test_stripping()
