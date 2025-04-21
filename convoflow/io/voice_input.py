import torch
import speech_recognition as sr
import numpy as np
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import warnings

# Suppress specific Warnings
warnings.filterwarnings("ignore", category=UserWarning, module='numba')
warnings.filterwarnings("ignore", category=UserWarning, module='librosa')
warnings.filterwarnings("ignore", category=FutureWarning, module='transformers.models.whisper.generation_whisper')
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
print(f"Using device: {device} with dtype: {torch_dtype}")

model_id = "openai/whisper-large-v3"

processor = None
print(f"Loading processor for {model_id}...")
try:
    processor = AutoProcessor.from_pretrained(model_id)
    print("Processor loaded.")
except Exception as e:
    print(f"FATAL: Failed to load processor: {e}")
    raise

model = None
print(f"Loading model {model_id}...")
try:
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, 
        torch_dtype=torch_dtype, 
        low_cpu_mem_usage=True,
        use_safetensors=True
    )
    model.to(device)
    print("Model loaded and moved to device.")
except Exception as e:
    print(f"FATAL: Failed to load model: {e}")
    print("Ensure sufficient RAM/VRAM and correct torch installation.")
    raise

pipe = None
if model and processor:
    print("Creating ASR pipeline...")
    try:
        pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=torch_dtype,
            device=device,
            chunk_length_s=30
        )
        print("ASR pipeline created successfully.")
    except Exception as e:
        print(f"FATAL: Failed to create pipeline: {e}")
        raise
else:
    print("FATAL: Model or processor not loaded, cannot create pipeline.")
    raise RuntimeError("Model or Processor failed to load")

# Initialize speech_recognition Recognizer
r = sr.Recognizer()
r.pause_threshold = 0.8
r.dynamic_energy_threshold = True

def transcribe_from_mic(sample_rate=16000):
    """
    Listens to the microphone until silence, then transcribes using Whisper.
    Uses explicitly loaded model and processor via the ASR pipeline.
    Returns: transcribed text (str) or empty string if error/no speech.
    """
    if pipe is None:
        print("ERROR: ASR pipeline is not available. Cannot transcribe.")
        return ""
        
    with sr.Microphone(sample_rate=sample_rate) as source:
        print("(Listening... Speak clearly and pause when finished)")
        try:
            audio_data = r.listen(source)
        except sr.WaitTimeoutError:
            print("(No speech detected within timeout)")
            return "" 
        except Exception as e:
            print(f"Error during listening: {e}")
            return "" 

    raw_data = audio_data.get_raw_data()
    audio_np = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0

    if audio_np.size == 0:
        print("(No audio captured)")
        return ""

    # Run pipeline
    try:
        result = pipe(
            audio_np,
            generate_kwargs={
                "language": "english",
                "forced_decoder_ids": None
            }
        )
        transcription = result["text"]
        print("(Whisper transcription finished.)")
        return transcription.strip().lower()
    except Exception as e:
        print(f"Error during Whisper processing: {e}")
        return "" 