import re

def get_prompt(script_text):
    words = re.findall(r'\w+', script_text)
    long_words = [w for w in words if len(w) >= 2]
    unique_words = list(dict.fromkeys(long_words))
    top_100 = unique_words[:100]
    return ", ".join(top_100)

def test_prompt_logic():
    print("--- Test Prompt Logic ---")
    
    # Case 1: Simple script
    script = "안녕하세요. 저는 김민중입니다. 만나서 반갑습니다. 김민중입니다."
    # Expected: 안녕하세요, 저는, 김민중입니다, 만나서, 반갑습니다 (Unique, len>=2)
    
    prompt = get_prompt(script)
    print(f"Script: {script}")
    print(f"Prompt: {prompt}")
    
    expected_words = ["안녕하세요", "저는", "김민중입니다", "만나서", "반갑습니다"]
    for w in expected_words:
        if w not in prompt:
            print(f"FAIL: Missing {w}")
            return
            
    if "김민중입니다" in prompt and prompt.count("김민중입니다") == 1:
        print("SUCCESS: Duplicates removed.")
    else:
        print("FAIL: Duplicates issue.")

    # Case 2: Long script
    long_script = "단어 " * 200
    # Should only have one "단어"
    prompt_long = get_prompt(long_script)
    print(f"Long Script Prompt: {prompt_long}")
    if prompt_long == "단어":
        print("SUCCESS: Long script handled.")
        
    # Case 3: Many unique words
    many_words = " ".join([f"word{i}" for i in range(150)])
    prompt_many = get_prompt(many_words)
    count = len(prompt_many.split(", "))
    print(f"Many Words Count: {count}")
    if count == 100:
        print("SUCCESS: Limited to 100 words.")
    else:
        print(f"FAIL: Count is {count}")

if __name__ == "__main__":
    test_prompt_logic()
