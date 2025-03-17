import requests
import json
import streamlit as st

# API Base URLs
API_ENDPOINTS = {
    "uniprot": "https://rest.uniprot.org/uniprotkb/search",
    "ncbi_entrez": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
    "string_db": "https://string-db.org/api/json/network",
    "clinvar": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
    "omim": "https://api.omim.org/api/entry",
    "disgenet": "https://www.disgenet.org/api",
    "alphafold": "https://www.alphafold.ebi.ac.uk/api/prediction",
    "pdb": "https://data.rcsb.org/rest/v1/core/entry",
    "open_targets": "https://api.platform.opentargets.org/api/v4/graphql",
    "drugbank": "https://go.drugbank.com/structures/small_molecule_drugs/",
    "chembl": "https://www.ebi.ac.uk/chembl/api/data",
    "faers": "https://api.fda.gov/drug/event.json",
    "sider": "http://sideeffects.embl.de/api/drug/",
    "ctd": "http://ctdbase.org/detail.go?",
    "mgi": "http://www.informatics.jax.org/api/marker/",
    "impc": "https://www.mousephenotype.org/data/genes/",
    "pubmed": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
    "clinical_trials": "https://clinicaltrials.gov/api/query/full_studies",
    "gtex": "https://gtexportal.org/rest/v1/expression/geneExpression",
    "hpa": "https://www.proteinatlas.org/search/",
    "fantom5": "https://fantom.gsc.riken.jp/5/datahub/",
    "ensembl": "https://rest.ensembl.org/lookup/symbol/homo_sapiens/",
    "proteomicsdb": "https://www.proteomicsdb.org/proteomicsdb/logic/api/proteinexpression",
    "ollama": "http://localhost:11434/api/generate"
}

def fetch_api_data(url, params=None):
    """Fetch data from an API endpoint."""
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def search_protein_databases(protein_name):
    """Fetch protein details from multiple sources."""
    return {
        "uniprot": fetch_api_data(API_ENDPOINTS["uniprot"], {"query": protein_name, "format": "json"}),
        "ncbi_entrez": fetch_api_data(API_ENDPOINTS["ncbi_entrez"], {"db": "gene", "term": protein_name, "retmode": "json"}),
        "string_db": fetch_api_data(API_ENDPOINTS["string_db"], {"identifiers": protein_name, "species": 9606}),
        "clinvar": fetch_api_data(API_ENDPOINTS["clinvar"], {"db": "clinvar", "term": protein_name, "retmode": "json"}),
        "omim": fetch_api_data(API_ENDPOINTS["omim"], {"search": protein_name, "format": "json"}),
        "disgenet": fetch_api_data(f"{API_ENDPOINTS['disgenet']}/gda/gene/{protein_name}?format=json"),
        "alphafold": fetch_api_data(f"{API_ENDPOINTS['alphafold']}/{protein_name}"),
        "pdb": fetch_api_data(f"{API_ENDPOINTS['pdb']}/{protein_name}")
    }

def search_expression_databases(protein_name):
    """Fetch protein expression details from multiple sources."""
    return {
        "gtex": fetch_api_data(f"{API_ENDPOINTS['gtex']}/{protein_name}"),
        "hpa": fetch_api_data(f"{API_ENDPOINTS['hpa']}{protein_name}"),
        "fantom5": fetch_api_data(f"{API_ENDPOINTS['fantom5']}{protein_name}"),
        "ensembl": fetch_api_data(f"{API_ENDPOINTS['ensembl']}{protein_name}", {"expand": "1"}),
        "proteomicsdb": fetch_api_data(f"{API_ENDPOINTS['proteomicsdb']}?protein_name={protein_name}")
    }

def chat_with_ollama(prompt):
    """Generate AI response using Ollama (Llama3) with streaming output."""
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "max_tokens": 1000,
        "temperature": 0.75,
        "top_p": 0.95,
        "stream": True
    }
    response = requests.post(API_ENDPOINTS["ollama"], json=payload, stream=True)

    full_response = ""
    for line in response.iter_lines():
        if line:
            try:
                chunk = json.loads(line.decode("utf-8"))
                full_response += chunk.get("response", "")
                if chunk.get("done", False):
                    break
            except Exception as ex:
                st.error("Error parsing streaming chunk: " + str(ex))
    return full_response

def get_protein_details(protein_name):
    """Fetch protein details and assess therapeutic target risks using multi-turn AI processing."""
    print(f"🔍 Searching for protein: {protein_name}...\n")

    # Fetch all data sources
    protein_data = search_protein_databases(protein_name)
    expression_data = search_expression_databases(protein_name)

    sections = {
        "Function & Disease Role": f"Describe the biological function, signaling pathways, and disease involvement of {protein_name}. Include known oncogenic mutations and associated cancers.",
        "Drug & Therapy Considerations": f"Summarize approved drugs, inhibitors, and therapeutic strategies for targeting {protein_name}. Discuss resistance mechanisms and alternative drug strategies, including combination therapies, repurposed drugs, and next-generation inhibitors.",
        "Pitfalls & Safety Risks": f"Identify potential safety risks, resistance mechanisms, and treatment failures associated with targeting {protein_name}. Highlight FDA warnings and reported adverse effects.",
        "Target-Mediated vs. Drug-Mediated Toxicity": f"Analyze toxicity profiles from FAERS, SIDER, CTD, and knockout studies. Distinguish between target-mediated toxicity (due to {protein_name}'s biological function) and drug-mediated toxicity (off-target effects).",
        "In Vitro & In Vivo Studies": f"Summarize experimental data from ChEMBL, Open Targets, and CTD. Highlight in vitro functional assays and in vivo tumor models related to {protein_name}.",
        "Knockout & Knock-In Studies": f"Summarize findings from knockout and knock-in models from MGI, IMPC, and PubMed. Explain the role of {protein_name} in normal physiology and disease models.",
        "Protein Expression & Alternative Transcripts": f"Summarize expression data from GTEx, HPA, FANTOM5, and ProteomicsDB. Indicate whether {protein_name} is ubiquitously expressed or tissue-specific, and analyze alternative transcript variants.",
        "Final Conclusion": f"Summarize the overall therapeutic potential, risks, and challenges of targeting {protein_name}. Discuss next-generation approaches, such as PROTACs, bispecific antibodies, or alternative pathway inhibition."
    }

    for section, prompt in sections.items():
        print(f"\n🔍 Generating AI response for: {section}")
        print(chat_with_ollama(prompt))

# Example Usage
protein_name = input("Enter a protein name or UniProt ID: ")
get_protein_details(protein_name)
