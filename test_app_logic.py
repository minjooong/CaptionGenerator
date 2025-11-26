from hanspell_custom import hanspell

def test_app_logic():
    print("--- Test App Logic ---")
    
    # Test Hanspell
    text = "맞춤법틀리면외않되?"
    res = hanspell.check(text)
    print(f"Hanspell Check: {res.checked}")
    
    # Test Session State Simulation
    segments = [
        {'start': 0, 'end': 1, 'text': "맞춤법틀리면"},
        {'start': 1, 'end': 2, 'text': "외않되?"}
    ]
    
    corrected_segments = []
    for seg in segments:
        r = hanspell.check(seg['text'])
        corrected_segments.append({
            'start': seg['start'],
            'end': seg['end'],
            'text': r.checked if r.result else seg['text']
        })
        
    print("Corrected Segments:")
    for seg in corrected_segments:
        print(f"{seg['text']}")

if __name__ == "__main__":
    test_app_logic()
