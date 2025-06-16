from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_ollama import Ollama
from core.vector_db import VectorStore
from typing import Dict, List

def init_chat_session():
    """Prepare conversation chain with document context"""
    vector_db = VectorStore()
    llm = Ollama(model="llama3", temperature=0.3)
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_db.collection.as_retriever(),
        memory=memory,
        chain_type="stuff",
        verbose=True
    )

def format_chat_response(response: Dict, sources: List[Dict]) -> str:
    """Create source-grounded response"""
    answer = response["answer"]
    source_texts = "\n\n".join(
        f"Source {i+1} ({s['metadata']['title']}):\n{s['text'][:500]}..."
        for i, s in enumerate(sources))
    return f"{answer}\n\n---\nREFERENCES:\n{source_texts}"