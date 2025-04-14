# Biomedical Research Assistant

A Retrieval-Augmented Generation (RAG)-powered research assistant that streamlines biomedical literature discovery, summarization, and Q&A using open-source LLM.

This Streamlit-based application integrates PubMed search, vector similarity retrieval, and LLaMA 3-based summarization and conversational reasoning to support scientific exploration and literature review.

---

## Key Features

### Assistant Mode — Literature RAG Pipeline
- **PubMed Search**: Query biomedical literature via NCBI Entrez API.
- **Vector Store**: Store and deduplicate paper metadata using ChromaDB.
- **RAG-Based Summarization**: Retrieve the top-*k* relevant papers via vector similarity search and generate a unified summary using LLaMA 3 with a         stuff summarization chain.

### Chatbot Mode — AI-Powered Literature Q&A
- Ask free-form questions about your research topic.
- Get grounded, document-aware responses using context-relevant paper embeddings retrieved via vector similarity.
- Powered by **Retrieval-Augmented Generation (RAG)** + **LLaMA 3** for domain-specific chat capabilities.

---


## Tech Stack

- **LLMs**: LLaMA 3 (locally hosted via [Ollama](https://ollama.com/))
- **RAG Framework**: Vector retrieval + LLM-based generation
- **Embedding Store**: [ChromaDB](https://www.trychroma.com/) for local persistent vector storage
- **Paper Metadata**: PubMed data via [NCBI Entrez API](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
- **UI Framework**: [Streamlit](https://streamlit.io/) for an interactive and lightweight frontend

---

## Notes
LLaMA 3 must be installed via Ollama and accessible locally.  
ChromaDB is used to persistently store embeddings of paper titles and abstracts.  
PubMed queries are limited to 100 papers per query to avoid rate limiting.

---

## Future Plans
Add support for full-text summarization  
Add PDF parsing and ingestion  
Add feature to select between LLMs