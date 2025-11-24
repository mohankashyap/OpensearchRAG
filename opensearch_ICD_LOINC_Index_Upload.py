import os
import pandas as pd
import requests
import zipfile
from io import BytesIO
import logging
import json
from opensearchpy import OpenSearch, RequestsHttpConnection, helpers

def get_opensearch_client_from_cred(json_path='credentials.json'):
    with open(json_path) as f:
        d = json.load(f)
    client = OpenSearch(
        hosts=[{'scheme': 'https', 'host': 'YOUR_OPENSEARCH_HOST', 'port': 8000}],
        verify_certs=False,
        http_auth=(d["username"], d["password"]),
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        connection_class=RequestsHttpConnection
    )
    return client

def write_to_elasticsearch(df, client, index_name):
    records = df.to_dict(orient='records')
    actions = [
        {
            "_index": index_name,
            "_source": record
        }
        for record in records
    ]
    helpers.bulk(client, actions)
    logging.info(f"Data written to Elasticsearch index: {index_name}")

def download_and_load_icd10cm(url, extract_folder='icd10cm_data'):
    """
    Downloads the latest ICD-10-CM code (2025) CSV or text file from CDC and parses to DataFrame.
    """
    files_page = requests.get(url)
    # Manually specify download link for 2025 release CSV if available
    ZIP_URL = 'https://www.cdc.gov/nchs/data/icd/ICD-10-CM-FY2026-Codes.zip'
    zip_response = requests.get(ZIP_URL)
    with zipfile.ZipFile(BytesIO(zip_response.content)) as z:
        z.extractall(extract_folder)
    
    # Look for code file (commonly named like 'icd10cm_codes_YYYY.txt' or similar)
    for file in os.listdir(extract_folder):
        if file.endswith('.txt') or file.endswith('.csv'):
            fp = os.path.join(extract_folder, file)
            # Standard columns: code, description
            df = pd.read_csv(fp, sep='\t', dtype=str, encoding="utf-8")
            # You may need to adjust delimiter based on file format (.csv vs .txt)
            # If not tab-delimited, try pd.read_csv(fp, sep=',', ...)
            return df
    raise FileNotFoundError("ICD-10-CM codes file not found after extraction.")

def download_and_load_loinc(url, extract_folder='loinc_data'):
    """
    Downloads LOINC complete set as CSV from official LOINC site and parses to DataFrame.
    """
    ZIP_URL = 'https://downloads.loinc.org/public/loinc/2.77/loinc.csv.zip'
    zip_response = requests.get(ZIP_URL)
    with zipfile.ZipFile(BytesIO(zip_response.content)) as z:
        z.extractall(extract_folder)
    for file in os.listdir(extract_folder):
        if file.lower() == 'loinc.csv':
            fp = os.path.join(extract_folder, file)
            df = pd.read_csv(fp, dtype=str, encoding='utf-8')
            return df
    raise FileNotFoundError("LOINC CSV file not found after extraction.")

def main():
    # Download and load ICD-10-CM
    icd_url = "https://www.cdc.gov/nchs/icd/icd-10-cm/files.html"
    icd_df = download_and_load_icd10cm(icd_url)
    
    # Download and load LOINC
    loinc_url = "https://loinc.org/downloads/"
    loinc_df = download_and_load_loinc(loinc_url)

    # Prepare OpenSearch client
    client = get_opensearch_client_from_cred('credentials.json')

    # Index ICD-10-CM codes
    write_to_elasticsearch(icd_df, client, index_name="icd10cmtest")
    # Index LOINC codes
    write_to_elasticsearch(loinc_df, client, index_name="loinctest")

if __name__ == "__main__":
    main()
