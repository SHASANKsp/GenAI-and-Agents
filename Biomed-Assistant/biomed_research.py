import os
import time
from Bio import Entrez
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
# Set your contact email for NCBI
Entrez.email = "shasankashekharpadhi@gmail.com"

CHROMA_DIR = "chroma_db"
MODEL_NAME = "llama3"



def fetch_pubmed_papers(query, max_results=100):
    print(f"🔍 Searching PubMed for: '{query}' ...")
    search = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    result = Entrez.read(search)
    ids = result["IdList"]
    print(f"✅ Found {len(ids)} papers.")

    papers = []
    for idx, pmid in enumerate(ids):
        print(f"📥 Fetching paper {idx + 1}/{len(ids)} (PMID: {pmid}) ...")
        try:
            handle = Entrez.efetch(db="pubmed", id=pmid, rettype="xml")
            record = Entrez.read(handle)
            article = record["PubmedArticle"][0]
            title = article["MedlineCitation"]["Article"]["ArticleTitle"]
            abstract = article["MedlineCitation"]["Article"].get("Abstract", {}).get("AbstractText", [""])[0]

            papers.append({
                "pmid": pmid,
                "title": title,
                "abstract": abstract
            })
        except Exception as e:
            print(f"❌ Error processing PMID {pmid}: {e}")
        time.sleep(0.34)  # Respect NCBI rate limit

    print(f"📚 Total papers fetched: {len(papers)}")
    return papers

def create_vector_store(papers):
    print("📦 Creating vector store in ChromaDB ...")
    texts = [f"Title: {p['title']}\nAbstract: {p['abstract']}" for p in papers]
    metadatas = [{"pmid": p["pmid"], "title": p["title"], "abstract": p["abstract"]} for p in papers]

    embeddings = OllamaEmbeddings(model=MODEL_NAME)
    vectordb = Chroma.from_texts(texts=texts, embedding=embeddings,
                                 metadatas=metadatas, persist_directory=CHROMA_DIR)
    vectordb.persist()
    print("✅ Vector store created and saved.")
    return vectordb

def get_existing_vector_store():
    print("📂 Loading existing vector store ...")
    embeddings = OllamaEmbeddings(model=MODEL_NAME)
    return Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)

def retrieve_relevant_papers(query, score_threshold=0.75, max_k=100):
    print(f"🔎 Retrieving papers with similarity score ≥ {score_threshold} ...")
    db = get_existing_vector_store()
    results_with_scores = db.similarity_search_with_score(query, k=max_k)

    filtered_docs = []
    print("📊 Similarity scores:")
    for idx, (doc, score) in enumerate(results_with_scores):
        print(f"🔹 [{idx + 1}] Score: {score:.4f} | Title: {doc.metadata.get('title', 'No title')}")
        if score >= score_threshold:
            filtered_docs.append(doc)

    print(f"✅ {len(filtered_docs)} papers passed similarity threshold.")
    return filtered_docs

def summarize_documents(docs):
    print("🧠 Generating consolidated summary with LLaMA 3 ...")

    llm = Ollama(model=MODEL_NAME, temperature=0.3, num_predict=4096)

    # Custom biomedical summarization prompt
    summary_prompt = PromptTemplate.from_template("""
You are a biomedical research assistant. Based on the collection of abstracts below, write a **detailed consolidated summary** that includes:
- Main biological concepts discussed
- Techniques used (e.g., CRISPR, sequencing)
- Key findings across the papers
- Similarities or differences in findings
- Implications for biomedical research or therapy

TEXT:
{text}

SUMMARY:
""")

    chain = load_summarize_chain(
        llm=llm,
        chain_type="map_reduce",
        map_prompt=summary_prompt,
        combine_prompt=summary_prompt
    )

    summary = chain.run(docs)
    print("✅ Summary complete.")
    return summary
