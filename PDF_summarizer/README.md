# Biomedical PDF Analysis Suite (Work in progress)

## **🔍 Overview**
An end-to-end solution for transforming biomedical PDFs into structured knowledge with:
- **Intelligent extraction** of text, tables, and statistical results
- **Cross-paper synthesis** with contradiction detection
- **Quality-controlled** summarization and analysis

## **✨ Key Features**
| Feature | Description |
|---------|-------------|
| **Hybrid PDF Parsing** | Text + tables + layout preservation |
| **Numerical Grounding** | p-values, effect sizes, and percentages standardization |
| **Hierarchical Summarization** | Paper-level → literature-wide insights |
| **Quality Assessment** | Custom criteria evaluation |
| **Document Q&A** | Source-grounded conversations |

## **🚀 Quick Start**
```bash
# Install with Ollama
git clone https://github.com/yourrepo/biomed_pdf_assistant
cd biomed_pdf_assistant
pip install -r requirements.txt
ollama pull llama3

# Launch
streamlit run app.py
```



