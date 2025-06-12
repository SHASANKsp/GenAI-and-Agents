import chromadb
from chromadb.config import Settings
from typing import List, Dict

class VectorStore:
    def __init__(self):
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="vector_db",
            anonymized_telemetry=False,
            auto_compact=True
        ))
        self.collection = self.client.get_or_create_collection("biomed_papers")
    
    def add_papers(self, papers: List[Dict]):
        """Store paper embeddings with metadata"""
        documents = []
        metadatas = []
        ids = []
        
        for i, paper in enumerate(papers):
            documents.append(paper["processed_text"])
            metadatas.append({
                "title": paper["title"],
                "year": paper["year"],
                "pmid": paper["pmid"],
                "has_tables": len(paper["tables"]) > 0
            })
            ids.append(f"doc_{i}")
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def retrieve_similar(self, query: str, n_results: int = 5) -> List[Dict]:
        """Semantic search across papers"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return [
            {
                "text": doc,
                "metadata": meta
            }
            for doc, meta in zip(results["documents"][0], results["metadatas"][0])
        ]