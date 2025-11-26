# 🎬 Local SRT Generator

A powerful, local-first application to generate SRT subtitles from audio files using OpenAI's Whisper model (via `faster-whisper`). Designed for accuracy and privacy, it runs entirely on your machine.

## ✨ Features

- **🔒 Local Processing**: No data leaves your computer. Powered by `faster-whisper` for efficient local transcription.
- **📝 Script-Aided Accuracy**: Upload a script to guide the AI, ensuring correct spelling of names and technical terms.
- **🧠 Smart Summarization**: Automatically extracts key vocabulary from long scripts to fit within the AI's context window.
- **✨ Grammar Correction**: Built-in Korean grammar and spelling correction using a custom Naver Speller integration.
- **⚡ Adjustable Formatting**:
    - **Smart Splitting**: Automatically splits lines based on a configurable character limit (default 16).
    - **Clean Output**: Removes all punctuation (commas, quotes, etc.) for a professional subtitle look.
- **🛠️ User-Friendly UI**: Simple web interface built with Streamlit.

## 🚀 Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install dependencies**:
    Ensure you have Python installed (3.8+ recommended).
    ```bash
    pip install -r requirements.txt
    ```

## 💻 Usage

1.  **Run the application**:
    ```bash
    streamlit run app.py
    ```

2.  **Generate Subtitles**:
    -   Upload your MP3, WAV, or M4A file.
    -   (Optional) Paste your script to improve accuracy.
    -   Adjust the "Max Characters per Line" setting if needed.
    -   Click **Generate Subtitles**.

3.  **Review & Correct**:
    -   Preview the generated subtitles.
    -   Click **✨ Correct Grammar** to automatically fix spacing and spelling errors.

4.  **Download**:
    -   Click **Download SRT** to save your file.

## 📂 Project Structure

-   `app.py`: Main application logic and UI.
-   `hanspell_custom.py`: Custom client for Naver Speller grammar correction.
-   `requirements.txt`: List of Python dependencies.

## ⚠️ Note

-   The first run may take a few moments to download the Whisper model.
-   Grammar correction requires an internet connection to access the Naver Speller API.

## 📄 License

[MIT License](LICENSE)
