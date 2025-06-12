import streamlit as st
from core import (
    pdf_processor,
    numerical_processor,
    summarizer,
    session_manager,
    quality_assessment
)
from utils import (
    chat_utils,
    viz_utils
)

# Initialize session
if "session" not in st.session_state:
    st.session_state.session = session_manager.SessionManager("default_user")

def main():
    st.set_page_config(
        page_title="Biomedical PDF Assistant",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("Biomedical Literature Analysis Suite")
    
    # Navigation
    page = st.sidebar.selectbox(
        "Select Mode",
        ["Upload Papers", "Summarize", "Quality Check", "Chat"]
    )
    
    if page == "Upload Papers":
        render_upload()
    elif page == "Summarize":
        render_summarization()
    elif page == "Quality Check":
        render_quality()
    elif page == "Chat":
        render_chat()

def render_upload():
    st.header("Upload Research Papers")
    
    # Project selection
    project_name = st.text_input("Project Name", "My_Research")
    
    # File upload
    uploaded_files = st.file_uploader(
        "Select PDFs",
        type="pdf",
        accept_multiple_files=True
    )
    
    if uploaded_files and project_name:
        if st.button("Process Papers"):
            session_id = st.session_state.session.create_session(project_name)
            
            with st.status("Processing...") as status:
                for i, file in enumerate(uploaded_files):
                    try:
                        # Process pipeline
                        raw = pdf_processor.extract_pdf_content(file)
                        processed = numerical_processor.preprocess_content(raw)
                        
                        # Store results
                        st.session_state.session.add_paper(session_id, {
                            "title": file.name,
                            "processed_text": processed["text"],
                            "tables": processed["tables"],
                            "storage_path": f"papers/{session_id}_{i}.json"
                        })
                        
                        status.write(f"Processed {file.name}")
                    except Exception as e:
                        st.error(f"Failed to process {file.name}: {str(e)}")
            
            st.success(f"Processed {len(uploaded_files)} papers")

def render_summarization():
    st.header("Literature Synthesis")
    
    # Session selection
    sessions = st.session_state.session.get_user_sessions()
    selected = st.selectbox("Select Project", sessions)
    
    if selected:
        papers = st.session_state.session.get_session(selected)["papers"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Individual Summaries")
            summary_type = st.radio(
                "Summary Style",
                ["Technical", "Clinical"],
                horizontal=True
            )
            
            for paper in papers:
                with st.expander(paper["title"]):
                    st.write(summarizer.summarize_paper(paper, summary_type))
        
        with col2:
            st.subheader("Consolidated Analysis")
            research_question = st.text_input(
                "Research Focus",
                "What is the relationship between X and Y?"
            )
            
            if st.button("Synthesize"):
                summaries = [
                    summarizer.summarize_paper(p, summary_type)
                    for p in papers
                ]
                synthesis = summarizer.synthesize_papers(
                    summaries,
                    research_question
                )
                st.write(synthesis)

def render_quality():
    st.header("Quality Assessment")
    
    # Session selection
    sessions = st.session_state.session.get_user_sessions()
    selected = st.selectbox("Select Project", sessions, key="qa_select")
    
    if selected:
        papers = st.session_state.session.get_session(selected)["papers"]
        
        # Custom criteria
        with st.expander("⚙️ Assessment Criteria"):
            st.write("Configure quality evaluation metrics")
            # Implementation omitted for brevity
        
        # Run assessment
        if st.button("Evaluate Papers"):
            assessments = []
            for paper in papers:
                assessments.append(
                    quality_assessment.assess_paper(paper)
                )
            
            # Visualize
            st.plotly_chart(viz_utils.plot_quality_scores(assessments))
            
            # Export
            st.download_button(
                "Download Report",
                pd.DataFrame(assessments).to_csv(),
                file_name="quality_assessment.csv"
            )

def render_chat():
    st.header("Document Q&A")
    
    # Initialize chat
    if "chat_chain" not in st.session_state:
        st.session_state.chat_chain = chat_utils.init_chat_session()
    
    # Chat interface
    if prompt := st.chat_input("Ask about your research papers"):
        response = st.session_state.chat_chain({"question": prompt})
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write(
            chat_utils.format_chat_response(
                response,
                sources=response.get("source_documents", [])
            )
        )

if __name__ == "__main__":
    main()