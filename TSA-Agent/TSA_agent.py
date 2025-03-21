import requests
import json
import concurrent.futures
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
    """Fetch data from an API endpoint with error handling."""
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"⚠️ API request failed: {url}\nError: {e}")
        return None

def fetch_all_data(protein_name):
    """Fetch data from multiple APIs in parallel."""
    endpoints = {
        "uniprot": (API_ENDPOINTS["uniprot"], {"query": protein_name, "format": "json"}),
        "omim": (API_ENDPOINTS["omim"], {"search": protein_name, "format": "json"}),
        "disgenet": (f"{API_ENDPOINTS['disgenet']}/gda/gene/{protein_name}?format=json", None),
        "chembl": (f"{API_ENDPOINTS['chembl']}/target/search/{protein_name}.json", None),
        "faers": (API_ENDPOINTS["faers"], {"search": f"patient.drug.openfda.substance_name:{protein_name}", "limit": 5}),
        "clinical_trials": (API_ENDPOINTS["clinical_trials"], {"expr": protein_name, "fmt": "json"}),
        "gtex": (f"{API_ENDPOINTS['gtex']}?geneId={protein_name}&datasetId=gtex_v8", None),
        "hpa": (f"{API_ENDPOINTS['hpa']}{protein_name}", None),
        "proteomicsdb": (f"{API_ENDPOINTS['proteomicsdb']}?name={protein_name}", None)
    }
    
    data = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_key = {executor.submit(fetch_api_data, url, params): key for key, (url, params) in endpoints.items()}
        for future in concurrent.futures.as_completed(future_to_key):
            key = future_to_key[future]
            try:
                data[key] = future.result()
            except Exception as e:
                print(f"⚠️ Error fetching {key}: {e}")
                data[key] = None
    return data

def format_protein_data(protein_name, protein_data):
    """Format API results into structured content for Llama3."""

    def safe_get(data, keys, default="N/A"):
        """Safely extract nested values from JSON response."""
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return default
        return data

    formatted_text = f"### Protein: {protein_name}\n"

    formatted_text += f"\n**UniProt Summary:** {safe_get(protein_data['uniprot'], ['results', 0, 'comment'], 'No data available')}"
    formatted_text += f"\n**OMIM Disease Associations:** {safe_get(protein_data['omim'], ['omim', 'entryList', 0, 'entry', 'titles', 'preferredTitle'], 'No data available')}"
    formatted_text += f"\n**DisGeNET Disease Links:** " + ", ".join(
        [d.get("disease_name", "N/A") for d in (protein_data.get("disgenet") or [])[:5]]
    )
    formatted_text += f"\n**ChEMBL Drugs:** " + ", ".join(
        [d.get("molecule_chembl_id", "N/A") for d in (protein_data.get("chembl", {}).get("molecules") or [])[:5]]
    )
    formatted_text += f"\n**FAERS Adverse Events:** " + ", ".join(
        [d["term"] for d in (protein_data.get("faers", {}).get("results") or [])[:5]]
    )
    formatted_text += f"\n**Clinical Trials:** " + ", ".join(
        [d.get("title", "N/A") for d in (protein_data.get("clinical_trials", {}).get("FullStudiesResponse", {}).get("FullStudies") or [])[:3]]
    )
    formatted_text += f"\n**Expression Data (GTEx, HPA, ProteomicsDB):** {safe_get(protein_data['gtex'], ['data'], 'No expression data available')}"

    return formatted_text

def chat_with_ollama(prompt):
    """Generate AI response using Ollama (Llama3)."""
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "max_tokens": 1000,
        "temperature": 0.75,
        "top_p": 0.95,
        "stream": True
    }
    try:
        response = requests.post(API_ENDPOINTS["ollama"], json=payload, stream=True, timeout=15)
        response.raise_for_status()

        full_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode("utf-8"))
                    full_response += chunk.get("response", "")
                    if chunk.get("done", False):
                        break
                except Exception as ex:
                    print(f"⚠️ Error parsing response chunk: {ex}")
        return full_response
    except requests.RequestException as e:
        print(f"⚠️ Ollama API request failed: {e}")
        return "⚠️ AI response unavailable due to API error."

if __name__ == "__main__":
    protein_name = input("Enter a protein name or UniProt ID: ")
    protein_data = fetch_all_data(protein_name)
    formatted_data = format_protein_data(protein_name, protein_data)

    print("\n🔬 **Final Conclusion** 🔬")
    print(chat_with_ollama(f"{formatted_data}\n\nProvide a deep analysis on the therapeutic significance, potential risks, and future research directions for {protein_name}."))
