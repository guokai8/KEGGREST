import requests
import re
import numpy as np
import pandas as pd
from collections import defaultdict

def get_root_url():
    return "https://rest.kegg.jp"

def get_genome_url():
    return "http://rest.genome.jp"

def print_message(*args):
    """Print formatted message without quotes."""
    print(" ".join(map(str, args)))

def clean_url(url):
    """Clean the URL by encoding specific characters."""
    url = re.sub(r" ", "%20", url)
    url = re.sub(r"#", "%23", url)
    url = re.sub(r":", "%3a", url)
    return re.sub(r"http(s)*%3a//", r"http\1://", url)

def fetch_url(url, parser=None, debug=False):
    """Fetch content from a URL and optionally parse it."""
    url = clean_url(url)
    if debug:
        print_message("URL:", url)
    
    response = requests.get(url)
    response.raise_for_status()
    
    content = response.text.strip()
    return parser(content) if parser else content

# Parsers
def matrix_parser(txt, ncol):
    """Parse text into an n x ncol matrix."""
    lines = txt.strip().split("\n")
    split_data = [line.split("\t") for line in lines]
    flattened_data = sum(split_data, [])
    return np.array(flattened_data).reshape(-1, ncol)

def organism_list_parser(url):
    """Parse the KEGG organism list."""
    response = requests.get(url)
    response.raise_for_status()
    lines = response.text.strip().split("\n")
    split_data = [line.split("\t") for line in lines]
    df = pd.DataFrame(split_data, columns=["T.number", "organism", "species", "phylogeny"])
    return df

def get_parser_name(entry):
    """Clean and parse the NAME field."""
    return {k: v.strip(";") for k, v in entry.items()}

def get_parser_entry(entry):
    """Parse the ENTRY field."""
    segs = re.split(r"\s{3,}", entry[0])
    return {segs[1]: segs[0]}

def get_parser_reference(refs):
    """Parse the REFERENCE field."""
    parsed_references = []
    current_ref = {}
    for item in refs:
        if item['refField'] == "REFERENCE":
            if current_ref:
                parsed_references.append(current_ref)
            current_ref = {"id": item["value"]}
        else:
            current_ref.setdefault(item['refField'], []).append(item["value"])
    if current_ref:
        parsed_references.append(current_ref)
    return parsed_references

def get_parser_key_value(entry):
    """Parse key-value data structure."""
    content = {}
    lines = entry.strip().split("\n")
    for line in lines:
        parts = line.split("  ", 1)
        if len(parts) == 2:
            key, value = parts
            content[key.strip()] = value.strip()
    return content

def get_parser_list(entry):
    """Parse list-like structure from the entry."""
    return re.split(r" {2,}", entry.strip())

def get_parser_list_or_key_value(entry):
    """Parse as list or key-value based on content structure."""
    if re.search(r" {2,}", entry):
        return get_parser_key_value(entry)
    return get_parser_list(entry)

def flat_file_parser(txt):
    """Parse KEGG flat files."""
    lines = txt.strip().split("\n")
    entry_data = defaultdict(list)
    current_key = None
    current_subfield = None

    for line in lines:
        if line.startswith("///"):
            entry_data["///"] = "End of Entry"
            continue

        line = line.rstrip()
        if not line.startswith(" "):  # New field
            parts = line.split(maxsplit=1)
            current_key = parts[0]
            current_subfield = None
            entry_data[current_key] = []
            if len(parts) > 1:
                entry_data[current_key].append(parts[1])
        else:  # Continuation of previous field
            if current_key:
                entry_data[current_key].append(line.strip())

    return entry_data

def list_parser(txt, value_column, name_column=None):
    """Parse list data into a dictionary with specified columns as keys and values."""
    lines = txt.strip().split("\n")
    parsed_data = {}

    for line in lines:
        fields = line.split("\t")
        if len(fields) >= value_column:
            value = fields[value_column - 1]
            name = fields[name_column - 1] if name_column and len(fields) >= name_column else None
            if name:
                parsed_data[name] = value
            else:
                parsed_data[len(parsed_data)] = value

    return parsed_data

def text_parser(txt):
    """Simply return the text as is."""
    return txt

# Example function calls to test functionality
if __name__ == "__main__":
    # Testing matrix parser
    txt_data = "A\tB\nC\tD\nE\tF"
    matrix = matrix_parser(txt_data, 2)
    print("Matrix Parsed:\n", matrix)

    # Testing organism list parser
    organism_url = "https://rest.kegg.jp/list/organism"
    organism_df = organism_list_parser(organism_url)
    print("\nOrganism List Parsed:\n", organism_df.head())

    # Testing key-value parser
    key_value_data = "ENTRY       A00000            Enzyme\nNAME        Example enzyme\n"
    key_value_dict = get_parser_key_value(key_value_data)
    print("\nKey-Value Parsed:\n", key_value_dict)
