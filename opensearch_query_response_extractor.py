import os
from typing import List, Dict, Any, Tuple
import json
import sys
from opensearchpy import OpenSearch, exceptions
from opensearchpy.connection import RequestsHttpConnection

def _load_json_credentials(json_file_read: str) -> Dict[str, str]:
    """
    Loads credentials from a JSON file.

    :param json_file_read: Path to the JSON credentials file.
    :return: Dictionary containing the loaded credentials.
    """
    print(f"Loading credentials from: {json_file_read}")
    with open(json_file_read, 'r') as f:
        data_json = json.load(f)
    return data_json

def create_opensearch_client(host: str, auth: Tuple[str, str]) -> OpenSearch:
    """
    Creates and returns an OpenSearch client.

    :param host: The OpenSearch host URL (e.g., "https://your-host:9200").
    :param auth: A tuple containing (username, password) for basic authentication.
    :return: An initialized OpenSearch client object.
    """
    client = OpenSearch(
        hosts=[host],
        verify_certs=False,         # Set to True in production with proper CA certs
        http_auth=auth,
        ssl_assert_hostname=False,  # Set to True in production
        ssl_show_warn=False,        # Suppress SSL warnings in development/testing
        connection_class=RequestsHttpConnection
    )
    try:
        if not client.ping():
            raise exceptions.ConnectionError("Failed to connect to OpenSearch. Please check host and credentials.")
        print("Successfully connected to OpenSearch.")
    except Exception as e:
        print(f"ERROR: OpenSearch connection failed: {e}", file=sys.stderr)
        raise
    return client

def execute_search_query(description: str,
                         size: int,
                         index_name: str,
                         field_name: str = "concept_name",
                         code_field: str = "concept_code") -> Tuple[List[Dict[str, Any]], Dict[str, str], List[str]]:
    """
    Executes a search query on OpenSearch to retrieve relevant documents based on a match in a specified field.

    :param description: The concept description to search for.
    :param size: Number of top documents to retrieve.
    :param index_name: The OpenSearch index to query.
    :param field_name: The field name to match against (default: 'concept_name').
    :param code_field: The field name for the concept code (default: 'concept_code').
    :return: Tuple containing list of hits, dict mapping codes to names, and list of concept names.
    """
    dict_rag = {}
    top_hits = []
    concept_names = []

    # Load credentials
    try:
        json_file_read = "/home/pargim/credentials.json"  # Update path as per environment
        data = _load_json_credentials(json_file_read)
    except Exception as e:
        print(f"ERROR: Could not load credentials: {e}", file=sys.stderr)
        return [], {}, []

    OPENSEARCH_HOST = "Opensearch Host"  # Set your host here
    OPENSEARCH_USERNAME = data.get("username")
    OPENSEARCH_PASSWORD = data.get("password")

    if not OPENSEARCH_USERNAME or not OPENSEARCH_PASSWORD:
        print("ERROR: OpenSearch username or password not found in credentials.json.", file=sys.stderr)
        return [], {}, []

    try:
        client = create_opensearch_client(OPENSEARCH_HOST, (OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD))
    except Exception:
        return [], {}, []

    # Optional setting for large queries
    client.cluster.put_settings({
        "persistent": {
            "indices.query.bool.max_clause_count": 8192
        }
    })

    search_body = {
        "size": size,
        "query": {
            "match": {
                field_name: description
            }
        },
        "sort": [
            {"_score": {"order": "desc"}}
        ]
    }

    print(f"\nInitiating search for index: {index_name}")
    print(f"Querying for {field_name}: '{description}'")
    print(f"Search Body:\n{json.dumps(search_body, indent=2)}")

    try:
        response = client.search(index=index_name, body=search_body)
        if response and "hits" in response and "hits" in response["hits"]:
            total_hits_found = response["hits"]["total"]["value"]
            print(f"Total matching documents found: {total_hits_found}")
            print(f"Retrieving top {len(response['hits']['hits'])} hits (up to requested size).")

            for hit in response["hits"]["hits"]:
                if "_source" in hit:
                    concept_name = hit["_source"].get(field_name, "N/A")
                    concept_code = hit["_source"].get(code_field, "N/A")
                    top_hits.append(hit)
                    dict_rag[concept_code] = concept_name
                    concept_names.append(concept_name)
        else:
            print("No hits found or unexpected response structure.")

    except exceptions.TransportError as e:
        print(f"ERROR: OpenSearch TransportError during search: {e.status_code} - {e.info['error']['reason']}", file=sys.stderr)
    except Exception as e:
        print(f"ERROR: Unexpected error during search: {e}", file=sys.stderr)

    print(f"\nFinished search. Total documents collected: {len(top_hits)}")
    return top_hits, dict_rag, concept_names

# Example Usage:
if __name__ == "__main__":
    # Search ICD codes
    icd_results, icd_dict_rag, _ = execute_search_query(
        description="diabetes type 2",
        size=20,
        index_name="icd_index",
        field_name="concept_name",
        code_field="concept_code"
    )

    # Search LOINC codes
    loinc_results, loinc_dict_rag, _ = execute_search_query(
        description="Hemoglobin blood g/dL",
        size=100,
        index_name="loincdb_without_component",
        field_name="concept_name",
        code_field="concept_code"
    )

    print(f"ICD results count: {len(icd_results)}")
    print(f"LOINC results count: {len(loinc_results)}")
