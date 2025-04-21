# ConvoFlow

**ConvoFlow** is a modular, AI-powered framework for building intelligent, conversational phone trees (IVR systems). It uses a graph-based design and integrates offline-friendly voice recognition, speech synthesis, and local language models like [Gemma](https://ollama.com/library/gemma) via [Ollama](https://ollama.com/). It is fully testable, supports logging of user journeys, and is great for rapid prototyping or production-ready flows.

---

## Features

- **Graph-based flow system**: Model your IVR routes using nodes and transitions.
- **Local LLM integration**: Route conversations using models like `gemma:7b` via LangChain + Ollama.
- **Voice input + speech output**: Leverages Hugging Face for speech-to-text and Coqui TTS for responses.
- **Back navigation**: Users can say "go back" at any point to return to the previous node.
- **CLI dev mode**: Rapidly test your flows without audio using a terminal interface.
- **Analytics logging**: Logs the user’s journey through the call graph into an SQLite database.

---

## Installation

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/convoflow.git
cd convoflow
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Install Ollama & Download a Model

ConvoFlow uses **Ollama** to run LLMs locally. Install it:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma:7b
```

---

## Quick Start

Run the sample CLI IVR flow (text-only mode):

```bash
python examples/dev_cli.py
```

This will simulate an IVR interaction in your terminal using LangChain + a local Gemma model.

You’ll see prompts like:
```
[START]: Welcome. Say billing, support, or hours.
You: billing
[BILLING]: Would you like your balance or to make a payment?
```

Say "go back" at any point to return to the previous prompt.

---

## Running Voice-Enabled IVR (Coming Soon)

Voice input and TTS runner will use:
- `sounddevice` for microphone input
- Hugging Face Wav2Vec2 for transcription
- Coqui TTS for responses

You can begin integrating this with the `convoflow/core/runner.py` class.

---

## Logging & Analytics

Each session is logged into a local **SQLite database (`convoflow.db`)**. Tracked data includes:

- Session start and end times
- Node IDs visited
- User input at each step
- Full traversal path

You can inspect it via:

```bash
sqlite3 convoflow.db
```

or using `sqlite-utils`:

```bash
sqlite-utils tables convoflow.db
sqlite-utils rows convoflow.db routes
```

---

## Testing

ConvoFlow includes a test suite under `/tests`.

To run all tests:

```bash
pytest
```

You can test:

- Graph building
- LangChain routing logic
- Voice transcription (mocked)
- Session logging to DB

---

## Directory Overview

```
convoflow/
│
├── convoflow/
│   ├── core/             # Graph + runner logic
│   ├── ai/               # LLM via LangChain
│   ├── io/               # STT and TTS handling
│   └── db/               # Logging to SQLite
│
├── examples/             # CLI demo flow
├── tests/                # Unit tests
├── requirements.txt
├── README.md
└── pyproject.toml
```

---

## Requirements

See [`requirements.txt`](./requirements.txt) for all dependencies. Key ones include:

- `langchain`, `langchain-community` – for LLM abstraction
- `ollama` – run local LLMs like Gemma
- `transformers`, `torchaudio`, `TTS` – for speech processing
- `pytest` – for testing

---

## License

MIT License

---

## Author

Developed by Bijan Ardalan — a modular, AI-first IVR framework for modern voice interfaces.