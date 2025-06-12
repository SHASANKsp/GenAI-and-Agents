import pdfplumber
import pdfformatter
import pandas as pd
from typing import Dict, List

def extract_pdf_content(pdf_path: str) -> Dict:
    """Hybrid PDF parser with layout preservation and table extraction"""
    try:
        content = {"text": "", "tables": []}
        
        # Primary extraction
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Text with layout awareness
                content["text"] += page.extract_text(layout=True) + "\n\n"
                
                # Tables
                for table in page.extract_tables():
                    if len(table) > 1:  # Skip empty tables
                        df = pd.DataFrame(table[1:], columns=table[0])
                        content["tables"].append({
                            "data": df.to_dict(orient="records"),
                            "metadata": {
                                "page": page.page_number,
                                "header": table[0]
                            }
                        })
        
        # Fallback for complex layouts
        if len(content["text"].split()) < 500:
            content["text"] = pdfformatter.extract(pdf_path, mode="academic")
            
        return content
    except Exception as e:
        raise RuntimeError(f"PDF processing failed: {str(e)}")

def extract_sections(text: str) -> Dict[str, str]:
    """Identify standard paper sections"""
    sections = {
        "abstract": r"ABSTRACT(.+?)(INTRODUCTION|$)",
        "methods": r"METHODS(.+?)RESULTS",
        "results": r"RESULTS(.+?)DISCUSSION",
        "conclusions": r"CONCLUSION(.+?)(REFERENCES|$)"
    }
    return {
        name: re.search(pattern, text, re.DOTALL | re.IGNORECASE).group(1).strip()
        for name, pattern in sections.items()
        if re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    }