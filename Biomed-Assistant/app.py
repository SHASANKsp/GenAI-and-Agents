import streamlit as st
import pandas as pd
from biomed_research import (
    fetch_pubmed_papers,
    store_new_papers,
    retrieve_relevant_papers,
    summarize_documents
)

st.set_page_config(page_title="🧬 Biomedical Research Assistant", layout="wide")
st.title("🧬 Biomedical Research Assistant")
st.markdown("**Search PubMed, store papers in vector DB, and summarize using LLaMA 3.**")

# SECTION 1: Query Input
st.header("🔍 Step 1: Enter Your Research Query")
query = st.text_input("Enter your biomedical research query:")
state_key = f"papers_fetched_{query}"

# Setup placeholders
docs = []
summary = ""

# SECTION 2 & 3 side by side
col1, col2 = st.columns(2)

# SECTION 2: Fetch or Use Existing DB
with col1:
    st.subheader("📥 Step 2: Fetch or Use Existing Papers")
    fetch_option = st.radio("Choose how to proceed:", options=["🔄 Fetch from PubMed", "📂 Use Existing Database"])

    if fetch_option == "🔄 Fetch from PubMed":
        if st.button("🔍 Fetch and Store Papers", key="fetch_store") and query:
            with st.spinner("Fetching and storing papers..."):
                papers = fetch_pubmed_papers(query, max_results=100)
                store_new_papers(papers)
                st.session_state[state_key] = True
            st.success("✅ Papers fetched and stored!")

    elif fetch_option == "📂 Use Existing Database":
        st.info("ℹ️ You chose to use the existing stored papers.")
        st.session_state[state_key] = True

# SECTION 3: Retrieve and Summarize
with col2:
    st.subheader("🧠 Step 3: Retrieve and Summarize")
    if not st.session_state.get(state_key, False):
        st.info("⚠️ Please complete Step 2 first.")
    else:
        top_k = st.slider("Select number of relevant papers to retrieve:", min_value=5, max_value=50, value=25)

        if st.button("🧠 Generate Consolidated Summary", key="summarize"):
            with st.spinner("Retrieving papers for summarization..."):
                docs = retrieve_relevant_papers(query, top_k=top_k)

            if docs:
                st.markdown("### 📄 Retrieved Papers with Distance Scores")

                df = pd.DataFrame([{
                    "Title": doc.metadata.get("title", "Untitled"),
                    "PMID": doc.metadata.get("pmid", ""),
                    "Distance": round(doc.metadata.get("similarity_score", 0), 4),
                    "PubMed Link": f"https://pubmed.ncbi.nlm.nih.gov/{doc.metadata.get('pmid', '')}"
                } for doc in docs])

                st.dataframe(df[["Title", "Distance", "PubMed Link"]], use_container_width=True)

                csv = df.to_csv(index=False)
                st.download_button("📄 Download Table as CSV", csv, file_name="retrieved_papers.csv")

            with st.spinner("Generating summary..."):
                summary = summarize_documents(docs, query)
                st.session_state["last_summary"] = summary  # Save to session

# OUTSIDE BOTH COLUMNS → Full width summary
if st.session_state.get("last_summary"):
    st.markdown("## 🧠 Consolidated Summary")
    st.markdown(st.session_state["last_summary"])
    st.download_button("📥 Download Summary", st.session_state["last_summary"], file_name="summary.txt")
