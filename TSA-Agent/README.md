# TSA Agent (Work in progress)
Protein safety assessment based on knowledge accessed from different databases**  

## **Overview**  
This tool retrieves comprehensive information about a given protein, including its function, drug interactions, toxicity risks, and expression data. It integrates multiple bioinformatics databases and AI-powered analysis to provide an in-depth evaluation of therapeutic targets.  

## **Workflow**  
1. **User Input:** Enter a protein name (e.g., *EGFR*) or UniProt ID.  
2. **Data Retrieval:** Queries multiple APIs to fetch protein-related data.  
3. **AI Analysis:** Uses **Llama3 (via Ollama)** for multi-turn AI processing to generate detailed insights.  
4. **Final Report:** Presents structured information in multiple sections, including **alternative drug strategies**, **target vs. drug-mediated toxicity**, and **expression analysis**.  

---

## **Data Sources & APIs**  

| **Resource**       | **Purpose** |
|--------------------|-------------|
| **UniProt**        | General protein information (function, sequence, structure). |
| **NCBI Entrez**    | Gene details, orthologs, and genetic variations. |
| **STRING-DB**      | Protein-protein interactions. |
| **ClinVar**        | Genetic variants and clinical significance. |
| **OMIM**          | Genetic disorders linked to the protein. |
| **DisGeNET**      | Disease associations. |
| **AlphaFold DB**  | AI-predicted protein structures. |
| **PDB**           | Experimentally determined 3D structures. |
| **Open Targets**  | Drug interactions and therapeutic relevance. |
| **DrugBank**      | Drug mechanisms and interactions. |
| **ChEMBL**       | Bioactivity data on drugs. |
| **FAERS**        | FDA Adverse Event Reporting System (drug safety). |
| **SIDER**        | Side effects database. |
| **CTD**          | Chemical-gene interactions. |
| **MGI**          | Knockout and genetic modification data (mouse models). |
| **IMPC**         | Mouse phenotype data for gene knockouts. |
| **PubMed**       | Literature search for relevant studies. |
| **ClinicalTrials.gov** | Ongoing clinical trials involving the protein. |
| **GTEx**         | Protein expression data across human tissues. |
| **HPA**          | Protein localization in tissues and cells. |
| **FANTOM5**      | Expression profiling in different cell types. |
| **Ensembl**      | Gene and transcript annotations. |
| **ProteomicsDB** | Protein abundance in different tissues. |

---

## **Setup Instructions**  
### **1. Install Ollama**  
Download and install Ollama from the official website: [https://ollama.com/download](https://ollama.com/download)  
Verify the installation: `ollama version`

### **2. Start Ollama Server**  
Run the following command in CMD: `ollama serve`

### **3. Download Llama3 Model**  
Install it using:  `ollama pull llama3`

### **4. Test Ollama**  
Run: `ollama run llama3 "Hello, how are you?"`



---
## **AI-Driven Analysis**  
The tool uses **Llama3 (via Ollama)** for AI-generated insights. It processes each section separately to ensure **multi-turn response generation**.  

### **AI-Generated Sections**  
1. **Function & Disease Role** – Protein function, signaling pathways, and disease links.  
2. **Drug & Therapy Considerations** – Approved drugs, resistance mechanisms, and treatment strategies.  
3. **Pitfalls & Safety Risks** – Drug resistance, adverse effects, and therapy limitations.  
4. **Target-Mediated vs. Drug-Mediated Toxicity** – Differentiating on-target from off-target effects.  
5. **Alternative Drug Strategies** – AI-suggested backup therapies based on mechanistic insights.  
6. **In Vitro & In Vivo Studies** – Experimental validation in cell and animal models.  
7. **Knockout & Knock-In Studies** – Functional insights from gene editing.  
8. **Protein Expression & Alternative Transcripts** – Expression levels, tissue specificity, and transcript variants.  
9. **Final Conclusion** – Summarizes therapeutic potential and future strategies.  

---

## **Future Improvements**  
- **Support for additional databases**  
- **Enhanced AI-driven insights**
- **Support for more models except Llama**
- **Streamlit for an UI**

---

