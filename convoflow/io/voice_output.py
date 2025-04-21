import torch
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import sounddevice as sd

# Load the models and processor
print("Loading SpeechT5 TTS model...")
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
print("SpeechT5 TTS model loaded.")

# Load speaker embeddings (using a default voice)
print("Loading speaker embeddings...")
voice_id = 5400
embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
speaker_embeddings = torch.tensor(embeddings_dataset[voice_id]["xvector"]).unsqueeze(0)
print("Speaker embeddings loaded.")

def speak_text(text, sample_rate=16000):
    """Synthesizes speech from text using SpeechT5 and plays it.

    Args:
        text (str): The text to speak.
        sample_rate (int): The desired sample rate for the audio.
                           Note: SpeechT5 HiFi-GAN vocoder outputs at 16kHz.
    """
    if not text:
        print("TTS: No text provided to speak.")
        return

    try:
        print(f"TTS: {text}")
        inputs = processor(text=text, return_tensors="pt")

        with torch.no_grad():
            spectrogram = model.generate_speech(inputs["input_ids"], speaker_embeddings)

            speech_waveform = vocoder(spectrogram)

        # Play the audio
        speech_np = speech_waveform.cpu().numpy()
        output_sample_rate = 16000 
        sd.play(speech_np, samplerate=output_sample_rate)
        sd.wait() # Wait until playback is finished
        print("\n")

    except Exception as e:
        print(f"Error during TTS synthesis or playback: {e}")
        raise
