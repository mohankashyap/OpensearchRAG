from typing import List, Dict, Tuple
import json
import openai  # Assume OpenAI API; replace with your LLM API client

# Reuse or import the generic execute_search_query function
# It should support specifying the index and relevant fields

def build_loinc_llm_prompt(loinc_description: str, retrieved_loinc: Dict[str, str]) -> str:
    """
    Build a prompt for the LLM combining the LOINC description with the retrieved LOINC codes and their descriptions.
    """
    intro_text = (
        "You are a clinical lab test coding assistant. Given the LOINC test description below,\n"
        "and a list of potential LOINC codes with descriptions retrieved from the knowledge store,\n"
        "identify and extract the most accurate LOINC codes that correspond to the test described.\n\n"
    )
    loinc_info = "\n".join([f"LOINC Code: {code} | Description: {desc}" for code, desc in retrieved_loinc.items()])
    prompt = (f"{intro_text}LOINC Test Description:\n{loinc_description}\n\nPotential LOINC Codes:\n{loinc_info}"
              "\n\nExtracted LOINC codes (provide only the codes):")
    return prompt

def extract_loinc_codes(loinc_description: str,
                        top_n_retrieval: int = 50,
                        loinc_index: str = "loincdb_without_component") -> List[str]:
    """
    Given a LOINC test description with metadata, retrieve potential codes from OpenSearch,
    then use an LLM to extract the most relevant LOINC codes.
    """
    # Step 1: Retrieve LOINC codes related to the description
    retrieved_hits, retrieved_codes_dict, _ = execute_search_query(
        description=loinc_description,
        size=top_n_retrieval,
        index_name=loinc_index,
        field_name="concept_name",  # Assuming 'concept_name' holds description/name
        code_field="concept_code"   # Assuming 'concept_code' holds LOINC codes
    )

    if not retrieved_codes_dict:
        print("No LOINC codes retrieved from knowledge base.")
        return []

    # Step 2: Build prompt for LLM
    prompt = build_loinc_llm_prompt(loinc_description, retrieved_codes_dict)

    # Step 3: Query the LLM (OpenAI GPT-4 example - adapt your API keys and call accordingly)
    openai.api_key = "your-api-key"
    llm_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful clinical lab coding assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0
    )

    output_text = llm_response['choices'][0]['message']['content'].strip()

    # Parse the output (expecting a list of LOINC codes separated by commas or new lines)
    extracted_codes = [code.strip() for code in output_text.replace("\n", ",").split(",") if code.strip()]

    return extracted_codes


# Example usage
if __name__ == "__main__":
    loinc_test_desc = """Hemoglobin blood g/dL"""
    extracted_codes = extract_loinc_codes(loinc_test_desc, top_n_retrieval=50, loinc_index="loincdb_without_component")
    print("Extracted LOINC Codes:", extracted_codes)
