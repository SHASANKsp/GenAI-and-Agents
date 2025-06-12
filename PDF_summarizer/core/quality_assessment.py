from typing import Dict
from langchain_core.prompts import ChatPromptTemplate

DEFAULT_CRITERIA = {
    "study_design": {
        "description": "Appropriateness of methodology",
        "weight": 0.3,
        "scale": {
            "1": "Case report/no controls",
            "5": "Randomized controlled trial"
        }
    },
    "statistical_rigor": {
        "description": "Proper use of statistics",
        "weight": 0.25,
        "scale": {
            "1": "No power calculation, inappropriate tests",
            "5": "Pre-registered, corrected for multiple comparisons" 
        }
    }
}

def assess_paper(paper: Dict, custom_criteria: Dict = None) -> Dict:
    """Evaluate paper against quality criteria"""
    criteria = {**DEFAULT_CRITERIA, **(custom_criteria or {})}
    
    assessment_prompt = """
    Evaluate this paper against biomedical research standards:
    
    {text}
    
    Assessment Criteria:
    {criteria}
    
    Provide scores in JSON format with brief rationale for each.
    """
    
    formatted_criteria = "\n".join(
        f"{name}: {desc['description']} (Weight: {desc['weight']})"
        for name, desc in criteria.items()
    )
    
    llm = Ollama(model="llama3")
    response = llm(assessment_prompt.format(
        text=paper["text"][:10000],  # First ~10k chars
        criteria=formatted_criteria
    ))
    
    return parse_assessment(response, criteria)

def parse_assessment(response: str, criteria: Dict) -> Dict:
    """Extract structured scores from LLM output"""
    try:
        import json
        data = json.loads(response)
        return {
            "scores": data,
            "weighted_score": sum(
                data.get(c, {}).get("score", 1) * criteria[c]["weight"]
                for c in criteria
            )
        }
    except:
        return {"error": "Failed to parse assessment"}