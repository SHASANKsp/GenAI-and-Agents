import pandas as pd
import numpy as np
import re
from typing import Dict, List

NUMERICAL_PATTERNS = {
    'p_value': r'p\s*[<>≤≥=]\s*[\d\.]+',
    'percentage': r'\d+\.?\d*\s*%',
    'correlation': r'r\s*=\s*[\d\.]+'
}

def preprocess_content(content: Dict) -> Dict:
    """Standardize all numerical data in document"""
    processed = content.copy()
    
    # Process tables
    processed["tables"] = [standardize_table(t) for t in content.get("tables", [])]
    
    # Annotate text
    processed["text"] = annotate_numerics(content["text"])
    
    # Extract stats
    processed["statistics"] = extract_statistics(processed["text"])
    
    return processed

def standardize_table(table: Dict) -> Dict:
    """Convert table data to analyzable formats"""
    df = pd.DataFrame(table["data"])
    
    # Numeric conversion
    for col in df.columns:
        # Handle percentages
        if df[col].astype(str).str.contains('%').any():
            df[col] = (
                df[col].astype(str)
                .str.replace('%','')
                .astype(float) / 100
            )
        # General numeric
        elif df[col].astype(str).str.match(r'^[\d\.,]+$').any():
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(',',''), 
                errors='ignore'
            )
    
    # Add metadata
    table["metadata"]["numerics"] = {
        col: {
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "mean": float(df[col].mean())
        }
        for col in df.select_dtypes(include=np.number).columns
    }
    
    table["data"] = df.to_dict(orient="records")
    return table

def annotate_numerics(text: str) -> str:
    """Tag statistical findings in text"""
    for stat_type, pattern in NUMERICAL_PATTERNS.items():
        text = re.sub(
            pattern, 
            f'[STAT:{stat_type.upper()}]\g<0>[/STAT]', 
            text, 
            flags=re.IGNORECASE
        )
    return text