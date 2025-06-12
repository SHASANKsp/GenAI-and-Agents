from typing import Dict, List, Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms import Ollama

SUMMARY_PROMPTS = {
    "technical": """
    Analyze this biomedical paper:
    
    {text}
    
    TABLES:
    {tables}
    
    Focus on:
    - Study design rigor
    - Key statistical results (p-values, effect sizes)
    - Limitations and biases
    """,
    "clinical": """
    Extract clinically relevant information:
    
    {content}
    
    Highlight:
    - Patient-relevant outcomes
    - Effect sizes with clinical interpretation
    - Safety concerns
    """
}

def summarize_paper(paper: Dict, mode: str = "technical") -> str:
    """Generate comprehensive paper summary"""
    llm = Ollama(model="llama3", temperature=0.2)
    
    # Prepare tables
    tables_str = "\n".join([
        f"Table {i+1}:\n{pd.DataFrame(t['data']).to_markdown()}"
        for i, t in enumerate(paper["tables"])
    ])
    
    # Generate summary
    prompt = ChatPromptTemplate.from_template(SUMMARY_PROMPTS[mode.lower()])
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run({
        "text": paper["text"],
        "tables": tables_str
    })

def synthesize_papers(summaries: List[str], query: str) -> Dict:
    """Create unified literature review"""
    llm = Ollama(model="llama3", temperature=0.3)
    
    synthesis_prompt = """
    Synthesize findings from {count} papers about '{query}':
    
    {summaries}
    
    Structure your response with:
    1. Consensus Findings (with paper count)
    2. Contradictory Evidence
    3. Research Gaps
    4. Clinical/Research Implications
    """
    
    return llm(synthesis_prompt.format(
        count=len(summaries),
        query=query,
        summaries="\n\n---\n\n".join(summaries)
    ))