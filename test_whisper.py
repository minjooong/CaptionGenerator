from faster_whisper import WhisperModel
import os

def test_model_loading():
    print("Testing model loading...")
    try:
        # Use 'tiny' for a quick test
        model = WhisperModel("tiny", device="auto", compute_type="int8")
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Failed to load model: {e}")

if __name__ == "__main__":
    test_model_loading()
