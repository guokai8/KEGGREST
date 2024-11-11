import requests
import re
import urllib.parse

# Default URLs
def get_root_url():
    """Get the root KEGG REST URL."""
    return "https://rest.kegg.jp"

def get_genome_url():
    """Get the KEGG Genome URL."""
    return "http://rest.genome.jp"

def print_message(*args):
    """Print formatted message without quotes."""
    print(" ".join(map(str, args)))

def clean_url(url):
    """Clean the URL by encoding specific characters."""
    url = urllib.parse.quote(url, safe="%/:=&?~#+!$,;'@()*[]")
    url = re.sub(r"http(s)*%3a//", r"http\1://", url)
    return url

def fetch_url(url, parser=None, debug=False):
    """Fetch content from a URL and optionally parse it."""
    url = clean_url(url)
    if debug:
        print_message("URL:", url)
    
    response = requests.get(url)
    response.raise_for_status()
    
    content = response.text.strip()
    if len(content) == 0:
        return [] if parser else ""

    return parser(content) if parser else content

def strip(string):
    """Strip leading and trailing whitespace from a string."""
    return string.strip()

def rstrip(string):
    """Strip trailing whitespace from a string."""
    return string.rstrip()

def lstrip(string):
    """Strip leading whitespace from a string."""
    return string.lstrip()

def get_kegg_pathway_image_url(pathway_id):
    """
    Get the KEGG pathway image URL by pathway ID.
    
    Args:
    - pathway_id (str): The KEGG pathway ID.
    
    Returns:
    - str: The full URL to the pathway image.
    """
    url = f"https://www.kegg.jp/kegg-bin/show_pathway?{pathway_id}"
    response = requests.get(url)
    response.raise_for_status()
    
    # Find image URL path
    lines = response.text.splitlines()
    for line in lines:
        if '<img src="/kegg' in line:
            path = line.split('"')[1]
            return f"https://www.kegg.jp{path}"
    
    return None

def split_in_groups(lst, n):
    """
    Split a list into groups of size n.
    
    Args:
    - lst (list): The list to split.
    - n (int): The size of each group.
    
    Returns:
    - list of lists: A list where each sublist is of size n or less.
    """
    return [lst[i:i + n] for i in range(0, len(lst), n)]

# Example usage:
if __name__ == "__main__":
    # Get root and genome URLs
    print("Root URL:", get_root_url())
    print("Genome URL:", get_genome_url())
    
    # Clean URL
    url = "http://example.com/test url with spaces and #hash"
    print("Cleaned URL:", clean_url(url))
    
    # Fetch a URL (example: get KEGG pathway image URL)
    pathway_id = "hsa00010"
    pathway_image_url = get_kegg_pathway_image_url(pathway_id)
    print("Pathway Image URL:", pathway_image_url)
    
    # Split a list into groups
    lst = list(range(10))
    print("Split in groups of 3:", split_in_groups(lst, 3))
