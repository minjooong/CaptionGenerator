from hanspell import spell_checker

def test_grammar():
    print("--- Test Grammar Correction ---")
    # Case 1: Spacing and spelling
    text = "맞춤법틀리면외않되?그리고띄어쓰기안하면어떻게돼"
    # Expected: "맞춤법 틀리면 왜 안 돼? 그리고 띄어쓰기 안 하면 어떻게 돼"
    
    try:
        result = spell_checker.check(text)
        print(f"Original: {text}")
        print(f"Corrected: {result.checked}")
        print(f"Success: {result.result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_grammar()
