import plotly.express as px
import pandas as pd

def plot_timeline(papers: List[Dict]):
    """Create publication year histogram"""
    years = [p.get("year") for p in papers if p.get("year")]
    if not years:
        return None
    
    df = pd.DataFrame({"year": years})
    fig = px.histogram(
        df, x="year",
        title="Publication Timeline",
        labels={"year": "Publication Year", "count": "Paper Count"}
    )
    return fig

def plot_quality_scores(assessments: List[Dict]):
    """Visualize quality assessment results"""
    df = pd.DataFrame([
        {
            "paper": f"Paper {i+1}",
            "score": a.get("weighted_score", 0),
            "criteria": ", ".join(a.get("scores", {}).keys())
        }
        for i, a in enumerate(assessments)
    ])
    
    return px.bar(
        df,
        x="paper",
        y="score",
        color="criteria",
        title="Paper Quality Scores"
    )