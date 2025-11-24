
# Installation of Opensearch Module
The link to install opensearch module is in:
[Opensearch Installation
](https://docs.opensearch.org/latest/install-and-configure/install-opensearch/index/)

## Installation of opensearch python client:

Read the instructions from this document to setup and connect to opensearch module using python client:
[Opensearch Python Client
](https://docs.opensearch.org/latest/clients/python-low-level/)

## Opensearch storing data into index
1. Download ICD-10-CM link(https://www.cdc.gov/nchs/icd/icd-10-cm/files.html) from or from your source containing a list of ICD-10-CM code and descriptions and load into a pandas dataframe
2. Download LOINC codes from (https://loinc.org/downloads/) or from your source containing a list of LOINC code and descriptions and load it into a pandas dataframe.

The code for writing the data to index is in : opensearch_upload_data_to_index.py



# RAG-Based Clinical Code Extraction

This repository contains Python modules for extracting diagnosis and lab test codes from clinical and lab text using a Retrieval-Augmented Generation (RAG) approach powered by an OpenSearch index and large language models (LLMs).

---

## Repository Structure

- `opensearch_query_response_extractor.py`  
  Core module to interact with OpenSearch, perform generic queries on medical code indices (e.g., ICD, LOINC), and return relevant concepts.

- `RAG_store_diagnosis_code_extraction.py`  
  Implements a pipeline to extract ICD diagnosis codes from clinical text by retrieving relevant ICD codes from the OpenSearch store and using an LLM to select the best matching codes.

- `RAG_LOINC_code_Extraction_template.py`  
  Similar pipeline for extracting LOINC lab test codes from test descriptions (with metadata) using retrieval from a LOINC OpenSearch index and LLM extraction.

---

## Setup Instructions

### Prerequisites

- Python 3.8 or newer
- OpenSearch cluster accessible with your credentials
- OpenAI API key (or another LLM API you wish to use)
- Required Python packages

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/rag-clinical-code-extraction.git
   cd rag-clinical-code-extraction
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   *(Create a `requirements.txt` with at least: `opensearch-py`, `openai`)*

4. Prepare your OpenSearch credentials JSON file (example: `/home/pargim/credentials.json`)
   ```
   {
       "username": "your_opensearch_username",
       "password": "your_opensearch_password"
   }
   ```
   Update the path in `opensearch_query_response_extractor.py` if necessary.

5. Store your OpenSearch host URL inside the `execute_search_query` function or configure as environment variable as preferred.

6. Set your OpenAI API key:
   ```
   export OPENAI_API_KEY="your-api-key"
   ```
   Or modify the code to directly set `openai.api_key`.

---

## Usage

### 1. Searching Codes from OpenSearch

You can directly use `opensearch_query_response_extractor.py` to query ICD or LOINC indexes.

Example:
```
python opensearch_query_response_extractor.py
```
This runs example queries for ICD ("diabetes type 2") and LOINC ("Hemoglobin blood g/dL") codes and prints counts.

---

### 2. Extract ICD Diagnosis Codes from Clinical Text Using RAG

Use the `RAG_store_diagnosis_code_extraction.py` module:

```
from RAG_store_diagnosis_code_extraction import extract_diagnosis_codes

clinical_text = """
Patient presents with acute chest pain and shortness of breath. ECG shows elevated ST segments consistent with myocardial infarction.
"""

codes = extract_diagnosis_codes(clinical_text, top_n_retrieval=50, icd_index="icd_index")
print("Extracted ICD Codes:", codes)
```

This function:
- Queries the ICD OpenSearch index with the input clinical text
- Builds a prompt including retrieved ICD codes and descriptions
- Uses an LLM to extract the most relevant diagnosis codes

---

### 3. Extract LOINC Codes from LOINC Descriptions Using RAG

Use the `RAG_LOINC_code_Extraction_template.py` module:

```
from RAG_LOINC_code_Extraction_template import extract_loinc_codes

loinc_description = "Hemoglobin blood g/dL"

codes = extract_loinc_codes(loinc_description, top_n_retrieval=50, loinc_index="loincdb_without_component")
print("Extracted LOINC Codes:", codes)
```

This function:
- Retrieves potential LOINC codes from OpenSearch based on the test description
- Sends a prompt combining descriptions and codes to an LLM to extract the best matching codes

---

## Notes

- Modify the `execute_search_query` parameters like index names and field names as per your OpenSearch schema.
- Replace OpenAI API calls with your preferred LLM API if needed.
- Update credential file paths and OpenSearch host URLs before running.
- The RAG approach enhances medical code extraction by grounding large language models in structured clinical knowledge bases.

---

## License

MIT License

---

## Contact

For questions or issues, please open an issue on this repository or contact the maintainer.

---
```
This README provides detailed instructions for setting up, running, and customizing all three key code files in your repo following best practices for Python projects on GitHub.

[1](https://realpython.com/python-project-documentation-with-mkdocs/)
[2](https://python-markdown.github.io/install/)
[3](https://github.com/Python-Markdown/markdown)
[4](https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/adding-a-dev-container-configuration/setting-up-your-python-project-for-codespaces)
[5](https://packaging.python.org/guides/making-a-pypi-friendly-readme/)
[6](https://docs.github.com/github/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
[7](https://github.com/darsaveli/Readme-Markdown-Syntax)
[8](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/quickstart-for-writing-on-github)
[9](https://python-markdown.github.io)
[10](https://github.com/mkdocs/mkdocs)
