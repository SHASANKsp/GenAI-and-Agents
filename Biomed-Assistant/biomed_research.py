import requests
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_community.llms import Ollama
from langchain.chains.summarize import load_summarize_chain

# Load Local Llama 3 Model
llm = Ollama(model="llama3")

# Load Local Embedding Model
embedding_model = SentenceTransformer("BAAI/bge-base-en")

# Function to Fetch Papers from PubMed
def fetch_pubmed_papers(query, max_results=5):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": max_results}
    
    response = requests.get(base_url, params=params)
    paper_ids = response.json()["esearchresult"]["idlist"]
    
    papers = []
    for paper_id in paper_ids:
        details_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={paper_id}&retmode=json"
        details_response = requests.get(details_url).json()
        paper_info = details_response["result"][paper_id]
        
        title = paper_info["title"]
        pubdate = paper_info.get("pubdate", "Unknown")
        papers.append({"id": paper_id, "title": title, "pubdate": pubdate})

    return papers

# Function to Create and Store Embeddings in ChromaDB
def create_vector_store(texts):
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(name="research_papers")

    for idx, text in enumerate(texts):
        embedding = embedding_model.encode(text).tolist()
        collection.add(ids=[str(idx)], embeddings=[embedding], documents=[text])

    return collection

# Function to Retrieve Relevant Papers
def retrieve_relevant_papers(query, vector_store):
    query_embedding = embedding_model.encode(query).tolist()
    results = vector_store.query(
        query_embeddings=[query_embedding], 
        n_results=3
    )
    return results["documents"]

# Function to Summarize Papers Using Llama 3
def summarize_paper(text):
    summarize_chain = load_summarize_chain(llm)
    summary = summarize_chain.run(text)
    return summary

# End-to-End Biomedical Research Assistant
def biomedical_research_assistant(query):
    papers = fetch_pubmed_papers(query)
    if not papers:
        return "No relevant papers found."

    texts = [p["title"] for p in papers]
    vector_store = create_vector_store(texts)
    
    relevant_papers = retrieve_relevant_papers(query, vector_store)
    
    summaries = []
    for paper in relevant_papers:
        summary = summarize_paper(paper)
        summaries.append(summary)
    
    return summaries
