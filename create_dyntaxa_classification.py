#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import pathlib
import dyntaxa_db_cache


# Load from db.
db_cache = dyntaxa_db_cache.DyntaxaDbCache()
taxa_dict = db_cache.get_dyntaxa_dict()
taxon_id_list = taxa_dict.keys()
print("Taxa length: ", len(taxa_dict.keys()))
taxa_name_list = db_cache.get_dyntaxa_name_list()
print("Taxa name length: ", len(taxa_name_list))
taxa_parent_list = db_cache.get_dyntaxa_parent_list()
print("Taxa parent length: ", len(taxa_parent_list))

# Create a dictionary with all children for each taxon.
parent_children_dict = {}
for row_dict in taxa_parent_list:
    parent_id = row_dict["ParentTaxonId"]
    child_id = row_dict["ChildTaxonId"]
    if parent_id not in parent_children_dict:
        parent_children_dict[parent_id] = {}
        parent_children_dict[parent_id]["child_ids"] = []
    parent_children_dict[parent_id]["child_ids"].append(child_id)
print("Length TaxonParentRelation: ", len(parent_children_dict))

# Define a recursive function.
def add_children(taxon_id, classification):
    """ Recursive function. """
    if taxon_id in parent_children_dict:
        children = parent_children_dict[taxon_id]["child_ids"]
        parent_classification = classification[taxon_id]

        for child_id in children:
            # classification[child_id] = parent_classification + [taxon_id]
            classification[child_id] = parent_classification + [child_id]
            # print(child, ": ", classification[child])
            add_children(child_id, classification)


# Set up top node.
classification = {}
classification["0"] = ["0"]
taxon_id = "0"
# Run the recursive function.
add_children(taxon_id, classification)

# Print file with classification, id version.
out_file = "data_out/classification_id.txt"
out_path = pathlib.Path(out_file)
with out_path.open("w") as f:
    for key in classification.keys():
        row = key + "\t" + "\t".join(classification.get(key, []))
        f.write(row + "\n")

# Print file with classification, id version.
name_check = {}
name_check_log = []
out_file = "data_out/classification_name.txt"
out_path = pathlib.Path(out_file)
with out_path.open("w") as f:
    f.write("taxon_id\tscientific_name\tclassification\n")
    for key_id in classification.keys():
        try:
            name = taxa_dict[key_id].get("ScientificName", "")
            category = taxa_dict[key_id].get("TaxonCategory", "")
            guid = taxa_dict[key_id].get("RecommendedGUID", "")

            # Check for duplicates.
            name_check_str = name + "\t" + key_id + "\t" + category + "\t" + guid
            if name not in name_check:
                name_check[name] = name_check_str
            else:
                # name_check[name] += 1
                print(
                    "ERROR: Duplicate name: \t", name_check[name], "\t", name_check_str
                )
                name_check_log.append(
                    "ERROR: Duplicate name: \t"
                    + name_check[name]
                    + "\t"
                    + name_check_str
                )

            # name_row.append(name)
            name_list = []
            for row_id in classification.get(key_id, []):

                name = taxa_dict[row_id].get("ScientificName", "")
                category = taxa_dict[row_id].get("TaxonCategory", "")

                name_list.append(name + " [" + category + "]")

            classification_str = " - ".join(name_list)
            row = (
                key_id
                + "\t"
                + name
                + "\t"
                + classification_str
                + "\t"
                + "\t".join(name_list)
            )
            f.write(row + "\n")
        except Exception as e:
            print("ERROR: classification_name.txt: ", e)

# Print warnings.
out_file = "data_out/warning_classification_check_log.txt"
out_path = pathlib.Path(out_file)
with out_path.open("w") as f:
    for row in name_check_log:
        f.write(row + "\n")