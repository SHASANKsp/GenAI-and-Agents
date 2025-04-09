import streamlit as st
from biomed_research import (
    fetch_pubmed_papers,
    create_vector_store,
    retrieve_relevant_papers,
    summarize_documents
)


st.set_page_config(page_title="Biomedical Research Assistant", layout="wide")
st.title("🧬 Biomedical Research Assistant")
st.markdown("Search and summarize research papers using your local **LLaMA 3** model and **ChromaDB**.")

query = st.text_input("🔍 Enter your biomedical search query:", "CRISPR in cancer")
score_threshold = st.slider("📊 Minimum similarity score to include a paper", 0.0, 1.0, 0.75, 0.01)
max_k = st.number_input("📌 Max number of papers to search (for filtering):", min_value=10, max_value=200, value=100, step=10)

if st.button("📥 Search and Summarize"):
    if query.strip():
        with st.spinner("🔄 Fetching papers from PubMed..."):
            papers = fetch_pubmed_papers(query, max_results=max_k)
            if not papers:
                st.warning("⚠️ No papers found.")
                st.stop()

        with st.spinner("📦 Creating vector store and storing papers..."):
            create_vector_store(papers)

        with st.spinner("🔍 Retrieving relevant papers..."):
            relevant_docs = retrieve_relevant_papers(query, score_threshold=score_threshold, max_k=max_k)
            if not relevant_docs:
                st.warning("⚠️ No papers matched the similarity threshold.")
                st.stop()

        with st.spinner("🧠 Generating summary using LLaMA 3..."):
            summary = summarize_documents(relevant_docs)

        st.success("✅ Summary Ready!")
        st.markdown("### 🧠 Consolidated Summary")
        st.markdown(summary)

        st.download_button("📥 Download Summary (.md)", summary, file_name="biomedical_summary.md")

        st.markdown("### 📚 Papers Used in Summary")
        titles_used = [doc.metadata.get("title", "Unknown title") for doc in relevant_docs]
        st.markdown("\n".join([f"- {t}" for t in titles_used]))
        st.download_button("📥 Download Paper Titles", "\n".join(titles_used), file_name="used_titles.txt")
    else:
        st.warning("❗ Please enter a query to proceed.")
