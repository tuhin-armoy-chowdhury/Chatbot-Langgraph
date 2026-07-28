"""
LangGraph chatbot backend powered by Google Gemini.

This module builds a tiny stateful chat graph:
  START → chat_node → END

The InMemorySaver checkpointer stores conversation history per thread_id,
so follow-up messages keep context without you re-sending the full history.
"""

from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

# Reads GOOGLE_API_KEY from a .env file in the project root (if present).
load_dotenv()

# Preferred order for automatic fallback when a model hits quota (429).
AVAILABLE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
]


def _is_quota_error(exc: BaseException) -> bool:
    text = str(exc)
    return "RESOURCE_EXHAUSTED" in text or "429" in text


def _model_chain(preferred: str) -> list[str]:
    """Try the user's pick first, then the rest of AVAILABLE_MODELS."""
    rest = [m for m in AVAILABLE_MODELS if m != preferred]
    if preferred in AVAILABLE_MODELS:
        return [preferred, *rest]
    return [preferred, *AVAILABLE_MODELS]


class ChatState(TypedDict):
    """
    Shared state that flows through the graph.

    `messages` is an Annotated list: when a node returns new messages,
    `add_messages` *appends* them instead of overwriting the whole list.
    That is how LangGraph accumulates conversation turns.
    """

    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState, config: RunnableConfig) -> dict:
    """
    Call Gemini with the selected model; on quota errors, try the next model.
    """
    messages = state["messages"]
    preferred = config.get("configurable", {}).get("model", AVAILABLE_MODELS[0])
    errors: list[str] = []

    for model_name in _model_chain(preferred):
        try:
            llm = ChatGoogleGenerativeAI(model=model_name)
            response = llm.invoke(messages)
            # Record which model answered (UI can show fallback info).
            response.response_metadata = {
                **(response.response_metadata or {}),
                "model_name": model_name,
                "requested_model": preferred,
                "fallback_used": model_name != preferred,
            }
            return {"messages": [response]}
        except ChatGoogleGenerativeAIError as exc:
            if not _is_quota_error(exc):
                raise
            errors.append(f"{model_name}: quota exceeded")
            continue

    raise RuntimeError(
        "All Gemini models hit quota limits. Try again later or enable billing.\n"
        + "\n".join(errors)
    )


checkpointer = InMemorySaver()

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)
