
import streamlit as st

from src.retrieval.rag_pipeline import RAGPipeline


st.set_page_config(
    page_title="InsightLens",
    page_icon="📊",
    layout="centered"
)


@st.cache_resource
def load_pipeline():
    return RAGPipeline()


pipeline = load_pipeline()

st.title("📊 InsightLens")
st.subheader("Multimodal RAG Assistant")

st.write(
    "Ask questions about business reports, revenue charts "
    "and video transcripts."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

        if message.get("sources"):
            st.caption("Sources:")
            for source in message["sources"]:
                st.write(source)


if prompt := st.chat_input("Ask a question about the business data..."):

    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Finding your answer..."):
            try:
                result = pipeline.ask(prompt)
                answer = result["answer"]
                sources = result["sources"]

            except ValueError:
                answer = (
                    "Document retrieval is not connected yet. "
                    "Please try a question about the available sales data."
                )
                sources = []

            st.write(answer)

            if sources:
                st.caption("Sources:")
                for source in sources:
                    st.write(source)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources
        }
    )
