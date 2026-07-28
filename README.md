# LangGraph Gemini Chatbot

A stateful chatbot built with [LangGraph](https://langchain-ai.github.io/langgraph/) and Google Gemini. Conversation history is retained per thread, and the Streamlit UI supports selecting a model with automatic fallback when a quota limit is reached.

## Features

1. LangGraph chat graph with in-memory checkpointing
2. Streamlit web UI with model selection
3. Automatic fallback across Gemini models on `429` / resource exhaustion
4. Jupyter notebook walkthrough for learning the graph setup

## Project structure

| File | Description |
| --- | --- |
| `langgraph_chatbot.ipynb` | Step by step notebook for building and testing the graph |
| `langgraph_backend.py` | Compiled LangGraph app, model list, and quota fallback logic |
| `streamlit_app.py` | Browser chat interface |
| `.env.example` | Template for `GOOGLE_API_KEY` |
| `requirements.txt` | Python dependencies |

```text
langgraph-gemini-chatbot/
├── langgraph_chatbot.ipynb
├── langgraph_backend.py
├── streamlit_app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Prerequisites

1. Python 3.10 or newer (`python3` on Linux)
2. A Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

## Setup

```bash
cd langgraph-gemini-chatbot

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Set GOOGLE_API_KEY in .env
```

Do not commit `.env`. It is listed in `.gitignore`.

## Run the Streamlit app

```bash
streamlit run streamlit_app.py
```

Open the URL shown in the terminal (default: `http://localhost:8501`). Select a Gemini model from the dropdown, then send a message in the chat input.

## Run the notebook

```bash
jupyter notebook langgraph_chatbot.ipynb
```

Execute cells from top to bottom. The notebook includes a smoke test, a memory check, and an interactive chat loop. Type `quit` to exit the loop.

## Graph overview

```text
START → chat_node (Gemini) → END
```

The checkpointer stores state by `thread_id`, so follow-up messages keep prior context without resending the full history.

```python
CONFIG = {
    "configurable": {
        "thread_id": "thread-1",
        "model": "gemini-2.5-flash",
    }
}

chatbot.invoke(
    {"messages": [HumanMessage(content="Hello")]},
    config=CONFIG,
)
```

1. Same `thread_id` continues the conversation
2. A new `thread_id` starts a fresh conversation
3. `InMemorySaver` keeps state in RAM only; history is cleared when the process stops

## Supported models

The app tries the selected model first. On quota errors it continues through the remaining list:

1. `gemini-2.5-flash` (default)
2. `gemini-2.5-flash-lite`
3. `gemini-2.5-pro`
4. `gemini-2.0-flash`

If a fallback model is used, the UI shows which model produced the reply.

## Troubleshooting

| Issue | Resolution |
| --- | --- |
| `python: command not found` | Use `python3` |
| `streamlit: command not found` | Activate the virtual environment and install requirements |
| Authentication errors | Confirm `.env` exists and `GOOGLE_API_KEY` is valid |
| `429 RESOURCE_EXHAUSTED` | Select another model; fallback should try the remaining options |
| Model not found | Choose a model name available for your API key |
| Notebook import errors | Use the same virtual environment kernel used for `pip install` |
| History lost after restart | Expected with `InMemorySaver` |

## License

For educational and personal use. Use your own Gemini API key and follow the [Google AI terms](https://ai.google.dev/gemini-api/terms).
