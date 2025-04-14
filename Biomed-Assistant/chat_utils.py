#import
import streamlit as st
from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.memory import ConversationBufferMemory

CHROMA_DIR = "chroma_db"
MODEL_NAME = "llama3"

def load_vector_db():
    embeddings = OllamaEmbeddings(model=MODEL_NAME)
    vectordb = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
    return vectordb

def run_chatbox():
    st.title("Biomedical Chatbot")
    vectordb = load_vector_db()
    num_docs = len(vectordb.get()["documents"])
    st.markdown(f"📊 **ChromaDB Status**: {num_docs} documents loaded.")

    llm = ChatOllama(model=MODEL_NAME, temperature=0.3)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    qa_chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=vectordb.as_retriever(), memory=memory)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_query = st.text_input("Ask something about the research papers:", key="chat_input")

    if user_query:
        response = qa_chain({"question": user_query})
        answer = response["answer"]
        st.session_state.chat_history.append((user_query, answer))

    for i, (q, a) in enumerate(st.session_state.chat_history):
        st.markdown(f"**You:** {q}")
        st.markdown(f"**Assistant:** {a}")
