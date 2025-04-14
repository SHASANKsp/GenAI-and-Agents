#imports
import streamlit as st
import pandas as pd
from biomed_research import (
    fetch_pubmed_papers,
    store_new_papers,
    retrieve_relevant_papers,
    summarize_documents
)
from chat_utils import run_chatbox


st.set_page_config(page_title="Biomedical Research Assistant", layout="wide")
st.title("Biomedical Research Assistant")

#toggle between Assistant and Chatbot
tab_option = st.radio("Choose View Mode:", ["Assistant", "Chatbot"], horizontal=True)

if tab_option == "Chatbot":
    run_chatbox()
    st.stop()


st.markdown("### Step 1: Enter your research query")
query = st.text_input("Enter your biomedical research query:")

col1, col2 = st.columns(2)
state_key = f"papers_fetched_{query}"

with col1:
    st.markdown("### Step 2: Fetch and Store Papers")
    fetch_option = st.radio(
        "Select source for summarization:",
        ["🔄 Fetch from PubMed", "📁 Use existing database"]
    )

    if st.button("Proceed", key="fetch_button") and query:
        with st.spinner("Processing..."):
            if fetch_option == "🔄 Fetch from PubMed":
                papers = fetch_pubmed_papers(query, max_results=100)
                store_new_papers(papers)
            st.session_state[state_key] = True
        st.success("✅ Papers ready!")

with col2:
    st.markdown("### Step 3: Retrieve and Summarize Papers")
    if not st.session_state.get(state_key, False):
        st.info("⚠️ Please complete Step 2 first.")
    else:
        top_k = st.slider("Number of papers to retrieve for summarization:", 5, 50, 25)
        if st.button("Consolidated Summary", key="summarize_button"):
            with st.spinner("Retrieving documents..."):
                docs = retrieve_relevant_papers(query, top_k=top_k)

            if docs:
                st.markdown("### 📄 Retrieved Papers")
                df = pd.DataFrame([{
                    "Title": doc.metadata.get("title", "Untitled"),
                    "PMID": doc.metadata.get("pmid", ""),
                    "Similarity Score": round(doc.metadata.get("similarity_score", 0), 4),
                    "PubMed Link": f"https://pubmed.ncbi.nlm.nih.gov/{doc.metadata.get('pmid', '')}"
                } for doc in docs])

                st.dataframe(df[["Title", "Similarity Score", "PubMed Link"]], use_container_width=True)
                st.download_button("📄 Download Table as CSV", df.to_csv(index=False), file_name="retrieved_papers.csv")

            with st.spinner("Generating summary..."):
                summary = summarize_documents(docs, query)

            st.markdown("## Consolidated Summary")
            st.markdown(summary)

            st.download_button("📥 Download Summary", summary, file_name="summary.txt")
