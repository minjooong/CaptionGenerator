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
    segments = []
    current_words = []
    
    for word in words:
        # Check what the text would look like if we added this word
        candidate_words = current_words + [word]
        candidate_text = "".join([w.word for w in candidate_words])
        formatted_candidate = format_text(candidate_text).strip()
        
        # If adding this word exceeds max_chars (and we already have words)
        if current_words and len(formatted_candidate) > max_chars:
            # Finalize current segment
            start = current_words[0].start
            end = current_words[-1].end
            text = "".join([w.word for w in current_words])
            # Keep original text with punctuation for grammar correction context
            
            segments.append({
                'start': start,
                'end': end,
                'text': text.strip()
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
        # Keep original text
        segments.append({
            'start': start,
            'end': end,
            'text': text.strip()
        })
        
    return segments

def generate_srt_content(segments):
    """Generates SRT content from processed segments."""
    srt_content = ""
    for i, segment in enumerate(segments, start=1):
        start_time = format_timestamp(segment['start'])
        end_time = format_timestamp(segment['end'])
        # Apply formatting (punctuation removal) HERE, at the final stage
        text = format_text(segment['text']).strip()
        srt_content += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"
    return srt_content

def transcribe_audio(audio_path, script_text=None, max_chars=16, progress_bar=None):
    """Transcribes audio using Faster-Whisper."""
    model_size = "medium"
    
    try:
        model = WhisperModel(model_size, device="auto", compute_type="int8")
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

    # Summarize script for prompt
    # User requested: Summarize to < 1000 chars including important words.
    # Strategy: Extract unique words to preserve vocabulary while reducing length.
    initial_prompt = None
    if script_text:
        # Normalize and split
        # Use simple regex to find words
        words = re.findall(r'\w+', script_text)
        # Unique preserving order
        unique_words = list(dict.fromkeys(words))
        # Join
        summary = " ".join(unique_words)
        # Truncate to 1000 chars
        if len(summary) > 1000:
            summary = summary[:1000]
        initial_prompt = summary
    
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
            # Keep original segment (with punctuation)
            processed_segments.append({
                'start': segment.start,
                'end': segment.end,
                'text': segment.text.strip()
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
                    'text': segment.text.strip()
                })
            
    if progress_bar:
        progress_bar.progress(1.0, text="Processing Subtitles...")
        
    return processed_segments

# Import custom hanspell
try:
    from hanspell_custom import hanspell
except ImportError:
    hanspell = None

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

uploaded_file = st.file_uploader("Upload MP3 Audio", type=["mp3", "wav", "m4a"])
script_text = st.text_area("Script (Optional - helps with accuracy)", height=200, placeholder="Paste your script here...")

if script_text:
    st.caption("ℹ️ Note: The script will be automatically summarized (vocabulary extracted) to fit the AI's context limit.")

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
            
            segments = transcribe_audio(tmp_path, script_text, max_chars, progress_bar)
            
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="Download SRT",
            data=st.session_state.srt_output,
            file_name="subtitles.srt",
            mime="text/plain",
            key="download_original"
        )
        
    with col2:
        if st.button("✨ Correct Grammar"):
            if hanspell:
                with st.spinner("Correcting grammar... This may take a while."):
                    corrected_segments = []
                    correction_count = 0
                    
                    progress_bar = st.progress(0, text="Correcting...")
                    total = len(st.session_state.segments)
                    
                    for i, seg in enumerate(st.session_state.segments):
                        original = seg['text']
                        try:
                            result = hanspell.check(original)
                            if result.result: # Success
                                corrected = result.checked
                                if corrected != original:
                                    correction_count += 1
                            else:
                                corrected = original
                        except Exception:
                            corrected = original
                            
                        # Preserve structure
                        corrected_segments.append({
                            'start': seg['start'],
                            'end': seg['end'],
                            'text': corrected
                        })
                        progress_bar.progress((i + 1) / total)
                    
                    # Update session state with corrected version
                    st.session_state.segments = corrected_segments
                    st.session_state.srt_output = generate_srt_content(corrected_segments)
                    st.rerun()
            else:
                st.error("Grammar correction module not loaded.")

    st.text_area("Preview Subtitles", st.session_state.srt_output, height=300)
    
    # If we just corrected, show a success message (logic: maybe store a flag?)
    # But for now, the updated preview is enough.
