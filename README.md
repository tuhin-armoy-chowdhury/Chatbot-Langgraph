# 💬 LangGraph + Gemini Chatbot

hey! so this is my little chatbot project — i wanted to learn **LangGraph** and also ditch OpenAI for a bit, so i wired it up with **Google Gemini** instead.

it’s a stateful chat bot (yep, it remembers what you said earlier 🧠). nothing crazy fancy, just a clean tiny graph that actually works.

you can play with it two ways:

1. 📓 **Jupyter notebook** — best if you’re learning step by step → `langgraph_chatbot.ipynb`
2. 🌐 **Streamlit UI** — nice little chat in the browser → `streamlit_app.py` + `langgraph_backend.py`

---

## ✨ what’s going on here?

every message basically does this:

```text
START → chat_node (Gemini) → END
```

super simple, right? but the cool part is the **checkpointer** — it keeps conversation history per `thread_id`, so follow-ups don’t feel dumb. you don’t have to resend the whole chat every time. love that.

oh and in the Streamlit app you can **pick a Gemini model** from a dropdown. if that one is out of quota (looking at you, 429 😤), it automatically tries the next models. lifesaver on the free tier.

| file | what it does |
| --- | --- |
| `langgraph_chatbot.ipynb` | walkthrough notebook — build the graph, poke at memory, chat loop |
| `langgraph_backend.py` | the actual LangGraph brain (models + fallbacks live here) |
| `streamlit_app.py` | browser UI with model picker |
| `.env.example` | copy this → make your `.env` |
| `requirements.txt` | all the python stuff |

---

## 🧰 what you need

- Python **3.10+** (on linux you might need `python3`, not `python` — yeah that got me once 😅)
- a free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

---

## 🚀 setup (do this once)

```bash
cd langgraph-gemini-chatbot

# make a venv (please do this, future you will thank you)
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt

# drop your key in
cp .env.example .env
# open .env and put: GOOGLE_API_KEY=your_real_key
```

⚠️ don’t commit `.env`. it’s already in `.gitignore`. keep your secrets secret.

---

## 📓 run the notebook

```bash
jupyter notebook langgraph_chatbot.ipynb
# or jupyter lab if that’s your vibe
```

run the cells top → bottom. there’s a smoke test, memory check, and an interactive loop. type `quit` when you’re done chatting.

i left comments on basically every important line because past me always forgets *why* something exists.

---

## 🌐 run the Streamlit app

one liner after setup:

```bash
streamlit run streamlit_app.py
```

then open whatever url it prints (usually `http://localhost:8501`).

pick a model from the dropdown, type something, and you’re good. if your first pick is quota-blocked, the app hops to another model and tells you which one answered. pretty neat ✨

---

## 🧠 how memory works (quick mental model)

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

- `thread_id` = which chat bucket you’re in
- same id → remembers previous turns
- new id → fresh conversation, clean slate
- `InMemorySaver` = stored in RAM only, so restarting the app = bye bye history (expected!)

---

## 🔁 models + fallback

right now the app knows about:

- `gemini-2.5-flash` ← default, usually my go-to
- `gemini-2.5-flash-lite`
- `gemini-2.5-pro`
- `gemini-2.0-flash` ← often dead on free tier (`limit: 0`), kept as last resort

you pick one in the UI. if that model screams quota, we try the others automatically. no more staring at a giant red traceback every time google gets spicy.

---

## 🆚 why gemini instead of openai?

| old openai vibe | this project |
| --- | --- |
| `ChatOpenAI` | `ChatGoogleGenerativeAI` |
| `OPENAI_API_KEY` | `GOOGLE_API_KEY` |
| gpt models | gemini models |

same LangGraph ideas (`StateGraph`, `add_messages`, checkpointer, streamlit history) — just swapped the LLM. that’s it.

---

## 📁 project layout

```text
langgraph-gemini-chatbot/
├── langgraph_chatbot.ipynb   # learn-by-doing path
├── langgraph_backend.py      # graph + multi-model fallback
├── streamlit_app.py          # chat UI
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md                 # you are here 🙂
```

---

## 🩹 troubleshooting (stuff that bit me)

| what went wrong | what fixed it |
| --- | --- |
| `python: command not found` | use `python3` |
| `streamlit: command not found` | activate the venv + install requirements first |
| auth / missing key errors | make sure `.env` exists and `GOOGLE_API_KEY` is real |
| `429 RESOURCE_EXHAUSTED` / quota = 0 | switch model in the dropdown — fallback should kick in |
| model 404 / not found | try another name from the list |
| notebook can’t import stuff | use the same venv kernel you installed into |
| bot “forgets” after restart | that’s `InMemorySaver` being honest — RAM only |

---

## 📜 license / vibes

educational / personal use. bring your own Gemini key and play nice with [Google’s AI terms](https://ai.google.dev/gemini-api/terms).

have fun hacking on it ✌️
