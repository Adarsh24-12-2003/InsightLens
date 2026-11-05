
import re

import streamlit as st

from src.retrieval.rag_pipeline import RAGPipeline


def rewrite_follow_up(original_question, follow_up):
    """Build a monthly question from the original metric and follow-up month."""
    month = re.search(
        r"\b(january|jan|february|feb|march|mar|april|apr|may|"
        r"june|jun|july|jul|august|aug|september|sep|october|oct|"
        r"november|nov|december|dec)\b",
        follow_up,
        re.IGNORECASE,
    )
    question_lower = original_question.lower()

    if "margin" in question_lower:
        metric = "profit margin"
    else:
        metrics = [
            name for name in ("revenue", "profit")
            if re.search(rf"\b{name}\b", question_lower)
        ]
        metric = " and ".join(metrics)

    if month and metric:
        return f"What was the {metric} in {month.group(0)}?"

    # Keep both messages available when either the metric or month is unclear.
    return f"{original_question}. Follow-up: {follow_up}"


st.set_page_config(
    page_title="InsightLens",
    page_icon="📊",
    layout="centered"
)


@st.cache_resource
def load_pipeline():
    # Reuse the pipeline across Streamlit reruns instead of rebuilding it.
    return RAGPipeline()


pipeline = load_pipeline()

st.title("📊 InsightLens")
st.subheader("Multimodal RAG Assistant")

st.write(
    "Ask questions about business reports, revenue charts "
    "and video transcripts."
)

if "messages" not in st.session_state:
    # Keep chat history between Streamlit reruns.
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

        if message.get("sources"):
            st.caption("Sources:")
            for source in message["sources"]:
                source_name = source.get("source", "Unknown source")
                st.write(f"📄 {source_name}")


# Streamlit reruns the app after each chat input; handle only a new prompt.
if prompt := st.chat_input("Ask a question about the business data..."):

    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Finding your answer..."):
            try:
                # Greetings need no document search, so answer them directly.
                if prompt.lower().strip() in ["hi", "hello", "hey"]:
                    answer = (
                        "Hello! Welcome to InsightLens. Ask me anything about "
                        "the business reports, revenue charts, or video transcripts."
                    )
                    sources = []
                else:
                    follow_up_starters = ("in ", "what about ", "and ")
                    if prompt.lower().strip().startswith(follow_up_starters):
                        # Skip earlier follow-ups to keep using the original question.
                        original_question = next(
                            (
                                message["content"]
                                for message in reversed(
                                    st.session_state.messages[:-1]
                                )
                                if message["role"] == "user"
                                and not message["content"].lower().strip().startswith(
                                    follow_up_starters
                                )
                            ),
                            None,
                        )
                        combined_query = (
                            rewrite_follow_up(original_question, prompt)
                            if original_question else prompt
                        )
                    else:
                        combined_query = prompt

                    result = pipeline.ask(combined_query)
                    answer = result["answer"]
                    sources = result["sources"]

            except ValueError:
                # Give a helpful response if retrieval is not configured.
                answer = (
                    "I'm designed to answer questions about the provided "
                    "business reports, revenue charts, sales data, and video transcripts. "
                    "Please ask me something related to these topics."
                )
                sources = []

            st.write(answer)

            if sources:
                st.caption("Sources:")
                for source in sources:
                    source_name = source.get("source", "Unknown source")
                    st.write(f"📄 {source_name}")

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources
        }
    )
