import streamlit as st
from biomed_research import fetch_pubmed_papers, create_vector_store, retrieve_relevant_papers, summarize_paper

# Streamlit UI
st.title("Biomedical Research Assistant")
st.write("Retrieve and summarize research papers using Llama 3 locally!")

query = st.text_input("Enter your biomedical search query (e.g., CRISPR in cancer):")

if st.button("Search & Summarize"):
    if query:
        with st.spinner("Fetching and summarizing papers..."):
            papers = fetch_pubmed_papers(query)
            if not papers:
                st.warning("No relevant papers found.")
            else:
                texts = [p["title"] for p in papers]
                vector_store = create_vector_store(texts)
                relevant_papers = retrieve_relevant_papers(query, vector_store)

                for idx, paper in enumerate(relevant_papers):
                    summary = summarize_paper(paper)
                    st.subheader(f"🔹 Paper {idx+1}")
                    st.write(f"**Title:** {paper}")
                    st.write(f"**Summary:** {summary}")

    else:
        st.warning("Please enter a search query.")
