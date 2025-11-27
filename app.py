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

import os
from dotenv import load_dotenv

load_dotenv()

import re
from collections import Counter

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

def format_text(text):
    """
    Removes punctuation except for " ' ,
    """
    # Remove punctuation but keep " 
    # We want to remove . ? ! ; : , ' etc.
    # Regex: replace [.?!\-;:,'] with empty string.
    text = re.sub(r"[.?!\-;:,']", '', text)
    return text

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

def extract_keywords_with_gemini(script_text, limit=50):
    """Extracts keywords using Google Gemini API."""
    if not HAS_GEMINI:
        st.error("Google Generative AI library not found.")
        return None
        
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.warning("GEMINI_API_KEY not found in .env file. Please add it.")
        return None
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        Analyze the following text and extract exactly {limit} keywords.
        
        Prioritize:
        1. People's names (Crucial)
        2. Proper nouns (Places, Organizations)
        3. Technical terms
        4. Important nouns that appear frequently
        
        Rules:
        - Extract as many relevant words as possible to reach the target of {limit}.
        - Exclude common verbs and simple adjectives.
        - Output ONLY the comma-separated list.
        
        Text:
        {script_text[:10000]}
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Gemini Error: {e}")
        return None

def correct_with_gemini(srt_content):
    """Corrects SRT content using Gemini API."""
    if not HAS_GEMINI:
        st.error("Google Generative AI library not found.")
        return None
        
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY not found in .env file.")
        return None
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        You are a professional subtitle editor. 
        Please correct any typos, spelling mistakes, and grammatical errors in the following Korean SRT subtitles.
        
        IMPORTANT RULES:
        1. Keep the exact SRT format (numbers, timestamps, blank lines).
        2. Do NOT change the timing.
        3. Only correct the text content.
        4. Remove any punctuation (commas, periods, question marks) from the corrected text if they were added, to maintain the clean style.
        5. Output ONLY the corrected SRT content, no other text.
        
        SRT Content:
        {srt_content}
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini API Error: {e}")
        return None

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
    st.caption("Number of keywords to extract from script.")

uploaded_file = st.file_uploader("Upload MP3 Audio", type=["mp3", "wav", "m4a"])
script_text = st.text_area("Script (Optional - helps with accuracy)", height=200, placeholder="Paste your script here...")

# Initialize session state
if 'segments' not in st.session_state:
    st.session_state.segments = None
if 'srt_output' not in st.session_state:
    st.session_state.srt_output = None
if 'corrected_srt' not in st.session_state:
    st.session_state.corrected_srt = None
if 'extracted_keywords' not in st.session_state:
    st.session_state.extracted_keywords = None

initial_prompt = None

if uploaded_file is not None:
    st.audio(uploaded_file, format='audio/mp3')
    
    if st.button("Generate Subtitles", type="primary"):
        # Reset corrected SRT on new generation
        st.session_state.corrected_srt = None
        
        # 1. Extract Keywords (if script provided)
        if script_text:
            with st.spinner("Step 1/2: Extracting keywords from script with Gemini..."):
                initial_prompt = extract_keywords_with_gemini(script_text, limit=prompt_limit)
                if initial_prompt:
                    st.session_state.extracted_keywords = initial_prompt
                    st.info(f"Context: {initial_prompt}")
        
        # Save uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        try:
            with st.spinner("Step 2/2: Generating subtitles... (This may take a moment)"):
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="Download Original SRT",
            data=st.session_state.srt_output,
            file_name="subtitles.srt",
            mime="text/plain",
            key="download_original"
        )
        
    with col2:
        if st.button("✨ Auto-Correct with Gemini"):
            with st.spinner("Correcting typos and grammar with Gemini..."):
                corrected_srt = correct_with_gemini(st.session_state.srt_output)
                if corrected_srt:
                    st.session_state.corrected_srt = corrected_srt
                    st.success("Correction Complete!")
        # The `correct_with_gemini` function internally checks for API key and handles errors.
        # So, the disabled button logic is now handled within the function or by its return value.

    st.text_area("Preview Subtitles (Original)", st.session_state.srt_output, height=300)
    
    if st.session_state.corrected_srt:
        st.divider()
        st.subheader("✨ Corrected Subtitles")
        st.download_button(
            label="Download Corrected SRT",
            data=st.session_state.corrected_srt,
            file_name="subtitles_corrected.srt",
            mime="text/plain",
            key="download_corrected"
        )
        st.text_area("Preview Corrected", st.session_state.corrected_srt, height=300)
