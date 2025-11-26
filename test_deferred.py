import re

def format_text(text):
    text = re.sub(r"[.?!\-;:,']", '', text)
    return text

def generate_srt_content(segments):
    srt_content = ""
    for i, segment in enumerate(segments, start=1):
        # Simulate format_text call
        text = format_text(segment['text']).strip()
        srt_content += f"{i}\n00:00:00,000 --> 00:00:01,000\n{text}\n\n"
    return srt_content

def test_deferred_formatting():
    print("--- Test Deferred Formatting ---")
    
    # Simulate segments with punctuation (as they would be after transcription/correction)
    segments = [
        {'text': "안녕하세요, 반갑습니다!"},
        {'text': "이것은 '테스트'입니다."}
    ]
    
    print("Original Segments:")
    for seg in segments:
        print(f"- {seg['text']}")
        
    srt_output = generate_srt_content(segments)
    
    print("\nGenerated SRT Content:")
    print(srt_output)
    
    if "," in srt_output or "'" in srt_output or "!" in srt_output:
        print("FAIL: Punctuation still present.")
    else:
        print("SUCCESS: Punctuation removed in SRT.")

if __name__ == "__main__":
    test_deferred_formatting()
