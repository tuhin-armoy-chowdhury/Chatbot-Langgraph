"""
Streamlit frontend for the LangGraph + Gemini chatbot.

Run with:
  streamlit run streamlit_app.py
"""

import streamlit as st
from langchain_core.messages import HumanMessage

from langgraph_backend import AVAILABLE_MODELS, chatbot

st.set_page_config(page_title="LangGraph Gemini Chatbot", page_icon="💬")
st.title("LangGraph Chatbot (Gemini)")

# Model picker — preferred model is tried first; others are fallbacks on 429.
selected_model = st.selectbox(
    "Gemini model",
    options=AVAILABLE_MODELS,
    index=0,
    help="If this model is out of quota, the app automatically tries the others.",
)

# thread_id tells the checkpointer which conversation memory bucket to use.
CONFIG = {
    "configurable": {
        "thread_id": "thread-1",
        "model": selected_model,
    }
}

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])
        if message.get("model"):
            st.caption(f"via {message['model']}")

user_input = st.chat_input("Type here")

if user_input:
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    response = chatbot.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=CONFIG,
    )

    last = response["messages"][-1]
    ai_message = last.content
    meta = getattr(last, "response_metadata", {}) or {}
    used_model = meta.get("model_name", selected_model)
    fallback = meta.get("fallback_used", False)

    note = used_model
    if fallback:
        note = f"{used_model} (fallback — {selected_model} was out of quota)"

    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message, "model": note}
    )
    with st.chat_message("assistant"):
        st.text(ai_message)
        st.caption(f"via {note}")
