#imports
import os
import time
from Bio import Entrez
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate


Entrez.email = "shasankashekharpadhi@gmail.com"
CHROMA_DIR = "chroma_db"
MODEL_NAME = "llama3"

def fetch_pubmed_papers(query, max_results=100):
    print(f"Searching PubMed for: '{query}' ...")
    search = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    result = Entrez.read(search)
    ids = result["IdList"]
    print(f"ound {len(ids)} papers.")

    papers = []
    for idx, pmid in enumerate(ids):
        print(f"Fetching paper {idx + 1}/{len(ids)} (PMID: {pmid}) ...")
        handle = Entrez.efetch(db="pubmed", id=pmid, rettype="xml")
        record = Entrez.read(handle)
        try:
            article = record["PubmedArticle"][0]
            title = article["MedlineCitation"]["Article"]["ArticleTitle"]
            abstract = article["MedlineCitation"]["Article"].get("Abstract", {}).get("AbstractText", [""])[0]
            print(f"Title: {title}")
            papers.append({
                "pmid": pmid,
                "title": title,
                "abstract": abstract
            })
        except Exception as e:
            print(f"Skipping paper due to error: {e}")
            continue
        time.sleep(0.34)

    print(f"Total papers fetched: {len(papers)}")
    return papers

def get_existing_vector_store():
    print("Loading existing vector store ...")
    embeddings = OllamaEmbeddings(model=MODEL_NAME)
    return Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)

def store_new_papers(papers):
    print("Storing new papers in ChromaDB with deduplication ...")
    vectordb = get_existing_vector_store()
    existing = vectordb.get(include=["metadatas"])
    existing_pmids = {m["pmid"] for m in existing["metadatas"]}

    new_papers = [p for p in papers if p["pmid"] not in existing_pmids]
    print(f"New unique papers to add: {len(new_papers)}")

    if not new_papers:
        print("No new papers to store.")
        return

    texts = [f"Title: {p['title']}\nAbstract: {p['abstract']}" for p in new_papers]
    metadatas = [{"pmid": p["pmid"], "title": p["title"], "abstract": p["abstract"]} for p in new_papers]
    vectordb.add_texts(texts=texts, metadatas=metadatas)
    vectordb.persist()
    print("New papers added and persisted.")

def retrieve_relevant_papers(query, top_k=25):
    print(f"Retrieving top {top_k} most relevant papers based on distance ...")
    db = get_existing_vector_store()
    results_with_scores = db.similarity_search_with_score(query, k=top_k)

    docs = []
    for doc, distance in results_with_scores:
        doc.metadata["distance_score"] = round(distance, 4)
        docs.append(doc)

    print("Titles of retrieved papers:")
    for idx, doc in enumerate(docs):
        title = doc.metadata.get("title", "Unknown title")
        score = doc.metadata.get("distance_score", 0)
        print(f"[{idx + 1}] Title: {title} | Distance Score: {score:.4f}")

    return docs

def summarize_documents(docs, query):
    print("Generating consolidated summary with LLaMA 3 ...")

    llm = Ollama(model=MODEL_NAME, temperature=0.3, num_predict=5000)

    summary_prompt = PromptTemplate.from_template("""
You are a biomedical research assistant.

A biomedical researcher is investigating the topic: **"{query}"**.

Based on the collection of abstracts provided below, write a **detailed and focused consolidated summary** that:
- Addresses the research question or topic directly.
- Highlights key findings, biological mechanisms, methods, and conclusions relevant to the query.
- Avoids including information not directly related to the topic.
- Uses scientific language suitable for a researcher or clinician.

TEXT:
{text}

CONSOLIDATED SUMMARY (focused on the query: "{query}"):
""")

    chain = load_summarize_chain(
        llm=llm,
        chain_type="stuff",
        prompt=summary_prompt
    )

    summary = chain.run({"input_documents": docs, "query": query})
    print("Summary complete.")
    return summary
