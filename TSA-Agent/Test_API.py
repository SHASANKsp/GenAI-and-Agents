#import
import os
import time
import requests
import json

os.makedirs("api_responses", exist_ok=True)

#List of APIs and their test query endpoints
APIS = {
    "uniprot": "https://rest.uniprot.org/uniprotkb/search?query=TP53",
    "ncbi_entrez": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&id=7157&retmode=json",
    "string_db": "https://string-db.org/api/json/network?identifiers=TP53",
    "clinvar": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term=TP53&retmode=json",
    "faers": "https://api.fda.gov/drug/event.json?search=patient.drug.medicinalproduct:TP53&limit=10",

    "ctd": "http://ctdbase.org/tools/batchQuery.go?inputType=gene&inputTerms=TP53&format=json",
    "mgi": "http://www.informatics.jax.org/api/marker/MGI:98834",
    "impc": "https://www.mousephenotype.org/data/genes/MGI:98834",
    "pubmed": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=TP53&retmode=json",
    "clinical_trials": "https://clinicaltrials.gov/api/query/full_studies?expr=TP53&fmt=json",
    "gtex": "https://gtexportal.org/rest/v1/expression/geneExpression?gencodeId=ENSG00000141510",
    "hpa": "https://www.proteinatlas.org/api/search/protein/TP53",
    "ensembl": "https://rest.ensembl.org/lookup/symbol/homo_sapiens/TP53?content-type=application/json",
}

def fetch_api(name, url, retries=3, delay=3):
    for attempt in range(1, retries + 1):
        try:
            print(f"Fetching data from {name} (Attempt {attempt})...")
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                file_path = os.path.join("api_responses", f"{name}.json")
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                print(f"Saved {name} data to {file_path}")
                return
            else:
                print(f"Attempt {attempt} failed for {name}: {response.status_code} - {response.reason}")
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt} failed for {name}: {e}")
        time.sleep(delay)  # Wait before retrying
    print(f"Failed to fetch {name} after {retries} attempts.")

for api_name, api_url in APIS.items():
    fetch_api(api_name, api_url)
print("\n API testing complete! Check 'api_responses' folder for results.")
