# KEGGREST

`KEGGREST` is a Python package providing a simple interface to access the KEGG (Kyoto Encyclopedia of Genes and Genomes) REST API. This package allows users to fetch and interact with data from KEGG databases, enabling bioinformatics research on genomic and pathway data.

> **Note:** This package was modified based on the `KEGGREST` package from Bioconductor.

## Installation

Clone the repository and install with:

```bash
git clone https://github.com/yourusername/KEGGREST.git
cd KEGGREST
pip install -e .
```
Overview
KEGGREST offers several key functions for querying the KEGG REST API:

kegg_info(): Retrieve information about KEGG databases.
kegg_list(): List entries in a KEGG database.
kegg_get(): Retrieve specific entries from KEGG databases.
kegg_find(): Search by keywords within KEGG databases.
kegg_conv(): Convert identifiers between KEGG and external databases.
kegg_link(): Link entries across KEGG databases.
Each of these functions interacts directly with the KEGG API, handling data parsing and returning structured results.

Usage
### 1. Exploring KEGG Resources with kegg_list()
To list all available databases:

```
from KEGGREST import list_databases

print(list_databases())
```
To list all organisms in KEGG:

```
from KEGGREST import kegg_list

pathway = kegg_list("pathway")
print(pathway.head())
```
### 2. Retrieving Specific Entries with kegg_get()
To retrieve detailed information about specific entries in KEGG, such as genes:

```
from KEGGREST import kegg_get

data = kegg_get(["hsa:10458", "ece:Z5100"])
print(data)
```
You can also retrieve amino acid or nucleotide sequences:

```
sequences = kegg_get(["hsa:10458", "ece:Z5100"], option="aaseq")
print(sequences)
```
### 3. Searching by Keywords with kegg_find()
To search for entries related to a keyword:

```
from KEGGREST import kegg_find

results = kegg_find("genes", "shiga toxin")
print(results)
```
### 4. Converting Identifiers with kegg_conv()
To convert identifiers between KEGG and other databases:
```
from KEGGREST import kegg_conv

conversion = kegg_conv("ncbi-proteinid", ["hsa:10458", "ece:Z5100"])
print(conversion)
```
### 5. Linking Across Databases with kegg_link()
To find relationships between different entities in KEGG:

```
from KEGGREST import kegg_link

pathways = kegg_link("pathway", "hsa")
print(pathways)
```
### Contributing

Contributions to KEGGREST are welcome! Please submit pull requests or open issues to discuss features, bugs, or improvements.

### License
This project is licensed under the MIT License - see the LICENSE file for details.

### Citation and Restrictions
The KEGG API is provided for academic use by researchers affiliated with academic institutions. Please refer to the official KEGG REST API documentation for more information.


