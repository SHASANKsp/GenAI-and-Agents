# Biomedical Research Assistant  
#### Retrieve and summarize biomedical research papers using Llama 3 (via Ollama) and ChromaDB for intelligent search.  

# Features  
Search PubMed for recent research papers  
Retrieve contextually relevant papers using ChromaDB  
Summarize papers locally using Llama 3 (via Ollama)  
Fast, lightweight, and works offline (except PubMed API)  
Interactive Streamlit UI for seamless exploration  

# Running the Application  
#### Start the Streamlit app with:  
`streamlit run app.py `
 
 Then, open the localhost URL in your browser.  

# 🖥️ Usage  
#### Enter a biomedical query (e.g., "CRISPR in cancer")  
#### Click "Search & Summarize"  
#### The app retrieves relevant papers, stores embeddings, and summarizes them  

# 🔍 How It Works  
#### 1. Fetches PubMed papers related to the query  
#### 2. Encodes papers using BAAI/bge-base-en embeddings  
#### 3. Stores embeddings in ChromaDB  
#### 4. Finds the most relevant papers  
#### 5. Summarizes each paper using Llama 3 locally  