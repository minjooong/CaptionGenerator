import streamlit as st
import os
import tempfile
from faster_whisper import WhisperModel
import math

def format_timestamp(seconds):
    """Converts seconds to SRT timestamp format (HH:MM:SS,mmm)."""
    hours = math.floor(seconds / 3600)
    seconds %= 3600
    minutes = math.floor(seconds / 60)
    seconds %= 60
    milliseconds = round((seconds - math.floor(seconds)) * 1000)
    seconds = math.floor(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

import re
from collections import Counter

def format_text(text):
    """
    Removes punctuation except for " ' ,
    """
    # Remove punctuation but keep " 
    # We want to remove . ? ! ; : , ' etc.
    # Regex: replace [.?!\-;:,'] with empty string.
    text = re.sub(r"[.?!\-;:,']", '', text)
    return text

def split_into_segments(words, max_chars=14):
    """
    Splits a list of word objects into subtitle segments, 
    ensuring each segment is at most max_chars long.
    Returns a list of dicts: {'start': float, 'end': float, 'text': str}
    """
def split_into_segments(words, max_chars=16):
    """Splits a list of words into segments based on character limit and punctuation."""
    segments = []
    current_words = []
    
    for word in words:
        # Check if adding this word exceeds max_chars
        current_len = sum(len(w.word) for w in current_words)
        new_len = current_len + len(word.word)
        
        # Check if previous word ended with sentence-ending punctuation
        force_break = False
        if current_words:
            last_word_text = current_words[-1].word.strip()
            if last_word_text.endswith('.') or last_word_text.endswith('?'):
                force_break = True
        
        if (new_len > max_chars and current_words) or force_break:
            # Finalize current segment
            start = current_words[0].start
            end = current_words[-1].end
            text = "".join([w.word for w in current_words])
            formatted_text = format_text(text).strip()
            
            segments.append({
                'start': start,
                'end': end,
                'text': formatted_text
            })
            
            # Start new segment
            current_words = [word]
        else:
            current_words.append(word)
                
    # Append last segment
    if current_words:
        start = current_words[0].start
        end = current_words[-1].end
        text = "".join([w.word for w in current_words])
        formatted_text = format_text(text).strip()
        segments.append({
            'start': start,
            'end': end,
            'text': formatted_text
        })
        
    return segments

def generate_srt_content(segments):
    """Generates SRT content from processed segments."""
    srt_content = ""
    for i, segment in enumerate(segments, start=1):
        start_time = format_timestamp(segment['start'])
        end_time = format_timestamp(segment['end'])
        text = segment['text']
        srt_content += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"
    return srt_content

def extract_prompt_words(script_text, limit=50):
    """Extracts important words from script for Whisper prompt, stripping particles."""
    if not script_text:
        return None
        
    # Normalize and split
    words = re.findall(r'\w+', script_text)
    
    # Common Korean particles/endings to strip
    # Order matters: longer matches first
    suffixes = [
        '에게서', '에서는', '에서도', '이라는', '이라고', '으로는', '으로도', '까지는', '까지도', '부터는', '부터도',
        '에서는', '에게는', '에게도', '한테는', '한테도', '께서는', '께서는', '입니다', '습니다', '합니다', '하고는',
        '에게', '에서', '으로', '까지', '부터', '한테', '께서', '처럼', '하고', '이나', '이랑', '이라', '와는', '과는',
        '은', '는', '이', '가', '을', '를', '의', '에', '로', '와', '과', '도', '만', '나', '랑', '야', '여', '라', '고'
    ]
    
    processed_words = []
    for w in words:
        # Skip very short words initially
        if len(w) < 2:
            continue
            
        stripped = w
        # Try to strip suffix
        for suffix in suffixes:
            if stripped.endswith(suffix):
                # Ensure we don't strip the whole word or leave just 1 char if possible
                # But if the word IS the suffix (rare for nouns), keep it?
                # Heuristic: Only strip if remaining length >= 1
                if len(stripped) > len(suffix):
                    stripped = stripped[:-len(suffix)]
                    break # Stop after first match (greedy)
        
        # Only keep if remaining part is still meaningful (len >= 2)
        if len(stripped) >= 2:
            processed_words.append(stripped)
    
    # Count frequency
    counter = Counter(processed_words)
    
    # Get top N most common words
    top_tuples = counter.most_common(limit)
    
    # Extract just the words
    top_words = [word for word, count in top_tuples]
    
    # Optimization: Check total length to fit within Whisper's context (approx 224 tokens)
    # A safe heuristic is ~800 characters for Korean/mixed text.
    final_words = []
    current_len = 0
    max_len = 800
    
    for word in top_words:
        # +2 for ", "
        if current_len + len(word) + 2 > max_len:
            break
        final_words.append(word)
        current_len += len(word) + 2
    
    # Join with commas for a keyword list style prompt
    return ", ".join(final_words)

def transcribe_audio(audio_path, initial_prompt=None, max_chars=16, progress_bar=None):
    """Transcribes audio using Faster-Whisper."""
    model_size = "medium"
    
    try:
        model = WhisperModel(model_size, device="auto", compute_type="int8")
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

    # Enable word_timestamps to allow precise splitting
    segments, info = model.transcribe(
        audio_path, 
        beam_size=5, 
        initial_prompt=initial_prompt,
        language="ko",
        word_timestamps=True
    )
    
    total_duration = info.duration
    processed_segments = []
    
    for segment in segments:
        # Update progress
        if progress_bar and total_duration > 0:
            progress = min(segment.end / total_duration, 1.0)
            progress_bar.progress(progress, text=f"Transcribing... {int(progress*100)}%")
        
        # Check length of the full segment (formatted)
        formatted_text = format_text(segment.text).strip()
        
        if len(formatted_text) <= max_chars:
            # Keep original segment (but formatted)
            processed_segments.append({
                'start': segment.start,
                'end': segment.end,
                'text': formatted_text
            })
        else:
            # Split this long segment using its words
            if segment.words:
                sub_segments = split_into_segments(segment.words, max_chars=max_chars)
                processed_segments.extend(sub_segments)
            else:
                # Fallback
                processed_segments.append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': formatted_text
                })
            
    if progress_bar:
        progress_bar.progress(1.0, text="Processing Subtitles...")
        
    return processed_segments

st.set_page_config(page_title="Local SRT Generator", page_icon="🎬")

st.title("🎬 Local SRT Generator")
st.markdown("""
Upload an MP3 file to generate SRT subtitles.
The script is used only to help the AI with context (names, etc.).
""")

with st.sidebar:
    st.header("Settings")
    max_chars = st.number_input("Max Characters per Line", min_value=10, max_value=50, value=16, step=1)
    st.info(f"Subtitles longer than {max_chars} characters will be split.")
    
    st.divider()
    prompt_limit = st.slider("Prompt Word Count", min_value=10, max_value=100, value=50, step=10)
    st.caption("Number of frequent words to extract from script.")

uploaded_file = st.file_uploader("Upload MP3 Audio", type=["mp3", "wav", "m4a"])
script_text = st.text_area("Script (Optional - helps with accuracy)", height=200, placeholder="Paste your script here...")

initial_prompt = None
if script_text:
    initial_prompt = extract_prompt_words(script_text, limit=prompt_limit)
    if initial_prompt:
        with st.expander("ℹ️ Extracted Context Words (Click to view)", expanded=False):
            st.info(initial_prompt)
            st.caption(f"Top {len(initial_prompt.split(', '))} frequent words (len >= 2) sent to AI.")

# Initialize session state
if 'segments' not in st.session_state:
    st.session_state.segments = None
if 'srt_output' not in st.session_state:
    st.session_state.srt_output = None

if uploaded_file is not None:
    st.audio(uploaded_file, format='audio/mp3')
    
    if st.button("Generate Subtitles"):
        # Save uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        try:
            progress_bar = st.progress(0, text="Starting transcription...")
            
            segments = transcribe_audio(tmp_path, initial_prompt, max_chars, progress_bar)
            
            if segments:
                srt_output = generate_srt_content(segments)
                
                # Save to session state
                st.session_state.segments = segments
                st.session_state.srt_output = srt_output
                
                st.success("Transcription Complete!")
            else:
                st.error("Transcription failed or returned no segments.")
        
        except Exception as e:
            st.error(f"An error occurred: {e}")
        
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

# Display results if available in session state
if st.session_state.segments:
    st.divider()
    st.subheader("Results")
    
    st.download_button(
        label="Download SRT",
        data=st.session_state.srt_output,
        file_name="subtitles.srt",
        mime="text/plain",
        key="download_original"
    )

    st.text_area("Preview Subtitles", st.session_state.srt_output, height=300)
