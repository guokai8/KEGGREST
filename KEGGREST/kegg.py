import requests
import re
import numpy as np
import pandas as pd
from collections import defaultdict

# Utility functions for KEGG URL handling and fetching data
def get_root_url():
    return "https://rest.kegg.jp"

def get_genome_url():
    return "http://rest.genome.jp"

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
        print(f"Fetching URL: {url}")
    
    response = requests.get(url)
    response.raise_for_status()
    
    content = response.text.strip()
    return parser(content) if parser else content

# Function to get KEGG information about a database
def kegg_info(database):
    url = f"{get_root_url()}/info/{database}"
    return fetch_url(url, lambda x: x)

# Function to get list of pathways or organisms
def kegg_list(database, organism=None):
    if isinstance(database, list):
        database = "+".join(database)
    if organism:
        url = f"{get_root_url()}/list/{database}/{organism}"
    else:
        url = f"{get_root_url()}/list/{database}"
    return fetch_url(url, parse_list)

# Function to find KEGG entries based on a query
def kegg_find(database, query, option=None):
    query = re.sub(r"\s", "+", query)
    url = f"{get_root_url()}/find/{database}/{query}"
    if option:
        url = f"{url}/{option}"
    return fetch_url(url, parse_list)

# Function to get detailed KEGG entries
def kegg_get(dbentries, option=None):
    if isinstance(dbentries, list):
        dbentries = "+".join(dbentries[:10])  # KEGG limits to 10 entries per request
    url = f"{get_root_url()}/get/{dbentries}"
    if option:
        url = f"{url}/{option}"
    return fetch_url(url, parse_flat_file)

# Function to retrieve compounds in a specific pathway
def kegg_compounds(pathway_id):
    url = f"{get_root_url()}/link/cpd/{pathway_id}"
    return fetch_url(url, parse_compound)

# Conversion function to get mappings between KEGG IDs
def kegg_conv(target, source, query_size=100):
    groups = split_into_groups(source, query_size)
    results = []
    for group in groups:
        query = "+".join(group)
        url = f"{get_root_url()}/conv/{target}/{query}"
        results.append(fetch_url(url, parse_list))
    return results

# Link function to retrieve relationships between pathways, genes, etc.
from collections import defaultdict

def parse_kegg_list(data):
    """Parse KEGG link data to ensure each line has exactly two elements."""
    parsed_data = []
    for line in data.splitlines():
        parts = line.split('\t')
        if len(parts) == 2:  # Only accept lines with exactly two tab-separated values
            parsed_data.append(tuple(parts))
    return parsed_data

def kegg_link(target, source=None):
    if source:
        url = f"{get_root_url()}/link/{target}/{source}"
    else:
        url = f"{get_genome_url()}/link/{target}"

    # Fetch the data from the URL
    data = fetch_url(url, parse_kegg_list)  # Use the updated parse function

    # Process the data to create direct and inverse dictionaries
    rel_dir = defaultdict(list)
    rel_inv = defaultdict(list)
    
    for element_1, element_2 in data:
        rel_inv[element_1].append(element_2)
        rel_dir[element_2].append(element_1)

    return rel_dir, rel_inv

# Function to split list into smaller groups
def split_into_groups(lst, n):
    """Split list into groups of size n."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# Parsers
def parse_list(txt):
    """Parse KEGG list format."""
    return {line.split("\t")[0]: line.split("\t")[1] for line in txt.splitlines() if "\t" in line}

def parse_matrix(txt):
    """Parse KEGG matrix format."""
    return [line.split("\t") for line in txt.splitlines() if "\t" in line]

def parse_flat_file(txt):
    """Parse KEGG flat file format."""
    result = {}
    current_key = None
    for line in txt.splitlines():
        if line.startswith(" "):
            if current_key and current_key in result:
                result[current_key].append(line.strip())
        else:
            key, _, value = line.partition(" ")
            current_key = key
            result[current_key] = [value.strip()]
    return result

def parse_compound(txt):
    """Parse KEGG compound format."""
    return [line.split(":")[1] for line in txt.splitlines() if "cpd:" in line]

# Custom visualization functions
def mark_pathway_by_objects(pathway_id, object_id_list):
    pathway_id = pathway_id.replace("path:", "")
    object_id_list = "+".join(object_id_list)
    url = f"https://www.kegg.jp/pathway/{pathway_id}+{object_id_list}"
    response = requests.get(url)
    response.raise_for_status()
    return response.url

def color_pathway_by_objects(pathway_id, object_id_list, fg_color_list, bg_color_list):
    if len(object_id_list) != len(fg_color_list) or len(fg_color_list) != len(bg_color_list):
        raise ValueError("Object, foreground color, and background color lists must be of the same length.")
    
    # Format payload for KEGG coloring
    payload = "\n".join([f"{obj}\t{bg},{fg}" for obj, fg, bg in zip(object_id_list, fg_color_list, bg_color_list)])
    url = f"https://www.kegg.jp/kegg-bin/show_pathway?map={pathway_id}&multi_query={payload}"
    response = requests.post(url)
    response.raise_for_status()

    # Extract image URL
    img_url = re.search(r'<img src="([^"]+)"', response.text)
    if img_url:
        return "https://www.kegg.jp" + img_url.group(1)
    raise ValueError("Image URL not found in response.")

# Example database list
def list_databases():
    return ["pathway", "brite", "module", "ko", "genome", "vg", "ag", "compound", "glycan", "reaction",
            "rclass", "enzyme", "disease", "drug", "dgroup", "environ", "genes", "ligand", "kegg"]

# Example usage
if __name__ == "__main__":
    # List human pathways
    pathways = kegg_list("pathway", "hsa")
    print("Pathways:", list(pathways.items())[:5])

    # Find specific compounds
    compounds = kegg_find("compound", "C00031")
    print("Compounds:", compounds)

    # Get details for a pathway
    pathway_details = kegg_get("hsa00010")
    print("Pathway Details:", pathway_details)

    # Get related compounds for a pathway
    pathway_compounds = kegg_compounds("hsa00010")
    print("Pathway Compounds:", pathway_compounds)

    # Conversion example
    conv_results = kegg_conv("ncbi-geneid", ["hsa:10458", "hsa:10563"])
    print("Conversion Results:", conv_results)

    # Link example
    link_results = kegg_link("pathway", "hsa:10458")
    print("Link Results:", link_results)
    
# Example usage
if __name__ == "__main__":
    data_lph, data_lhp = kegg_link('pathway', 'hsa')
    print("Direct relationships:", data_lph)
    print("Inverse relationships:", data_lhp)