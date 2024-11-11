import requests
import re
import numpy as np
import pandas as pd
from collections import defaultdict

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

class FlatFileRecordGen:
    def __init__(self):
        self.fields = defaultdict(list)
        self.references = []
        self.last_field = None
        self.last_subfield = None
        self.current_reference = {}

    def set_field(self, field):
        """Sets a new field, flushing previous data if necessary."""
        self.flush()  # Save any previous data before setting a new field
        self.last_field = field
        self.last_subfield = None

    def set_subfield(self, subfield):
        """Sets a subfield within the current field."""
        self.last_subfield = subfield

    def set_body(self, body):
        """Sets the body content for the current field or subfield."""
        if self.last_field == "REFERENCE":
            # Handling REFERENCE-specific data
            if self.last_subfield:
                self.current_reference.setdefault(self.last_subfield, []).append(body)
            else:
                self.current_reference.setdefault(self.last_field, []).append(body)
        else:
            # General handling for other fields
            if self.last_subfield:
                self.fields[self.last_field].setdefault(self.last_subfield, []).append(body)
            else:
                self.fields[self.last_field].append(body)

    def flush(self):
        """Flushes the current reference if it exists."""
        if self.current_reference:
            self.references.append(self.current_reference)
            self.current_reference = {}

    def get_fields(self):
        """Returns all fields, including references."""
        fields = dict(self.fields)
        if self.references:
            fields["REFERENCE"] = self.references
        return fields


# Parser functions to handle different field types
def get_parser_list(entry):
    return re.split(r" {2,}", entry.strip())

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
    content = {}
    lines = entry.strip().split("\n")
    for line in lines:
        parts = line.split("  ", 1)
        if len(parts) == 2:
            key, value = parts
            content[key.strip()] = value.strip()
    return content

def get_parser_list_or_key_value(entry):
    if re.search(r" {2,}", entry):
        return get_parser_key_value(entry)
    return get_parser_list(entry)

def get_parser_biostring(entry, type):
    """Parse a sequence entry, returning an amino acid or nucleotide string."""
    seq = "".join(entry[1:]).replace("\n", "")
    if type == "AAStringSet":
        return f"AAStringSet({seq})"
    elif type == "DNAStringSet":
        return f"DNAStringSet({seq})"
    return seq


# Main flat file parser function
def flat_file_parser(txt):
    lines = txt.strip().split("\n")
    all_entries = []
    ffrec = FlatFileRecordGen()

    for line in lines:
        if line == "///":
            # Flush entry when end marker is encountered
            ffrec.flush()
            for name, item in ffrec.get_fields().items():
                # Apply specific parsing functions based on field name
                if name == "ENTRY":
                    ffrec.set_field("ENTRY")
                    ffrec.set_body(get_parser_entry(item))
                elif name in {"ENZYME", "MARKER", "ALL_REAC", "RELATEDPAIR", "DBLINKS", "DRUG", "GENE"}:
                    ffrec.set_field(name)
                    ffrec.set_body(get_parser_list(item))
                elif name in {"PATHWAY", "ORTHOLOGY", "PATHWAY_MAP", "MODULE", "DISEASE", "REL_PATHWAY", "COMPOUND", "REACTION", "ORGANISM"}:
                    ffrec.set_field(name)
                    ffrec.set_body(get_parser_key_value(item))
                elif name == "REACTION":
                    ffrec.set_field(name)
                    ffrec.set_body(get_parser_list_or_key_value(item))
                
                # Handle single-item lists
                if isinstance(item, list) and len(item) == 1:
                    ffrec.set_field(name)
                    ffrec.set_body(item[0])

            # Process sequences
            if "NTSEQ" in ffrec.get_fields():
                ffrec.set_field("NTSEQ")
                ffrec.set_body(get_parser_biostring(ffrec.get_fields()["NTSEQ"], "DNAStringSet"))
            if "AASEQ" in ffrec.get_fields():
                ffrec.set_field("AASEQ")
                ffrec.set_body(get_parser_biostring(ffrec.get_fields()["AASEQ"], "AAStringSet"))

            # Append the fully parsed entry to the list of all entries
            all_entries.append(ffrec.get_fields())
            ffrec = FlatFileRecordGen()  # Start a new record
            continue

        # Remove trailing whitespace from line
        line = line.rstrip()
        if not line.startswith(" "):  # New field
            parts = line.split(maxsplit=1)
            field = parts[0]
            ffrec.set_field(field)
            if len(parts) > 1:
                ffrec.set_body(parts[1])
        else:  # Continuation or subfield
            content = line.strip()
            if content:
                ffrec.set_body(content)

    return all_entries

def get_parser_name(entry):
    """Clean and parse the NAME field."""
    return {k: v.strip(";") for k, v in entry.items()}


def get_parse_biostring(entry, seq_type):
    """
    Parse biostrings (DNA or amino acid sequences) from KEGG entries.
    """
    sequence = "".join(entry[1:]).replace("\n", "")
    if seq_type == "AAStringSet":
        return sequence  # Amino Acid Sequence as string
    elif seq_type == "DNAStringSet":
        return sequence  # DNA Sequence as string
    else:
        raise ValueError("Invalid sequence type. Use 'AAStringSet' or 'DNAStringSet'.")

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
