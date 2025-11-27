import re
from collections import Counter

def extract_prompt_words(script_text):
    if not script_text:
        return None
    words = re.findall(r'\w+', script_text)
    long_words = [w for w in words if len(w) >= 2]
    counter = Counter(long_words)
    top_100_tuples = counter.most_common(100)
    top_100_words = [word for word, count in top_100_tuples]
    return ", ".join(top_100_words)

def test_frequency():
    print("--- Test Frequency Extraction ---")
    
    # "중요" appears 3 times, "보통" 2 times, "가끔" 1 time
    script = "중요 중요 중요 보통 보통 가끔"
    expected_order = ["중요", "보통", "가끔"]
    
    result = extract_prompt_words(script)
    print(f"Script: {script}")
    print(f"Result: {result}")
    
    result_list = result.split(", ")
    
    if result_list == expected_order:
        print("SUCCESS: Correct frequency order.")
    else:
        print("FAIL: Order mismatch.")

if __name__ == "__main__":
    test_frequency()
