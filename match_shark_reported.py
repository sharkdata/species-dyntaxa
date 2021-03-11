#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import pathlib
import dyntaxa_db_cache


print("Starting...")

# dyntaxa_columns = [
#     "TaxonId",
#     "ScientificName",
#     "Author",
#     "TaxonCategoryId",
#     "TaxonCategory",
#     "IsValid",  # Use True
#     "ValidFromDate",
#     "ValidToDate",
#     "RecommendedGUID",
# ]

# dyntaxa_name_columns = [
#     "TaxonId",
#     "Name",
#     "IsRecommended",
#     "NameCategoryId",  # 0=scientific name
#     "NameUsageId",  # 1=synonym
#     "NameStatusId",  # 0=valid
#     "ValidFromDate",
#     "ValidToDate",
# ]

# dyntaxa_parent_columns = [
#     "ChildTaxonId",
#     "ParentTaxonId",
# ]


# Load from db.
db_cache = dyntaxa_db_cache.DyntaxaDbCache()
dyntaxa_dict = db_cache.get_dyntaxa_dict()
print("Taxa length: ", len(dyntaxa_dict.keys()))
dyntaxa_name_list = db_cache.get_dyntaxa_name_list()
print("Taxa name length: ", len(dyntaxa_name_list))
dyntaxa_parent_list = db_cache.get_dyntaxa_parent_list()
print("Taxa parent length: ", len(dyntaxa_parent_list))

taxon_id_list = dyntaxa_dict.keys()
lookup_name_dyntaxa_dict = {}
lookup_name_dyntaxa_synonyms_dict = {}
lookup_shark_translate_dict = {}

# # Marine only.
# marine_taxon_id_list = []
# for taxon_id in taxon_id_list:
#     taxon_dict = taxa_dict[taxon_id]
#     if "marinespecies.org" in taxon_dict["RecommendedGUID"]:
#         marine_taxon_id_list.append(taxon_id)
# print("Marine taxa length: ", len(marine_taxon_id_list))

# From dyntaxa taxa.
for row_dict in dyntaxa_dict.values():
    taxon_id = row_dict["TaxonId"]
    scientific_name = row_dict["ScientificName"]
    # Add ID.
    if taxon_id not in lookup_name_dyntaxa_dict:
        lookup_name_dyntaxa_dict[taxon_id] = []
    if taxon_id not in lookup_name_dyntaxa_dict[taxon_id]:
        lookup_name_dyntaxa_dict[taxon_id].append(taxon_id)
    # Add name.
    if scientific_name not in lookup_name_dyntaxa_dict:
        lookup_name_dyntaxa_dict[scientific_name] = []
    if taxon_id not in lookup_name_dyntaxa_dict[scientific_name]:
        lookup_name_dyntaxa_dict[scientific_name].append(taxon_id)

# From dyntaxa names.
for row_dict in dyntaxa_name_list:
    taxon_id = row_dict["TaxonId"]
    scientific_name = row_dict["Name"]
    # recommended = row_dict["IsRecommended"]
    # if recommended == "True":
    if scientific_name not in lookup_name_dyntaxa_synonyms_dict:
        lookup_name_dyntaxa_synonyms_dict[scientific_name] = []
    if taxon_id not in lookup_name_dyntaxa_synonyms_dict[scientific_name]:
        lookup_name_dyntaxa_synonyms_dict[scientific_name].append(taxon_id)

# # Log when multiple dyntaxa-id.
# for scientific_name in lookup_name_dict.keys():
#     if len(lookup_name_dict[scientific_name]) > 1:
#         print(
#             "Multiple id for name: ",
#             scientific_name,
#             " Id list: ",
#             lookup_name_dict[scientific_name],
#         )

# Save to file.
lookup_file_path = pathlib.Path("data_out/lookup_name.txt")
with lookup_file_path.open("w", encoding="cp1252", errors="replace") as file:
    file.write("scientific_name\tdyntaxa_id\n")
    for key, value in sorted(lookup_name_dyntaxa_dict.items()):
        file.write(key + "\tTAXA\t" + "\t".join(value) + "\n")
    for key, value in sorted(lookup_name_dyntaxa_synonyms_dict.items()):
        file.write(key + "\tSYNONYM\t" + "\t".join(value) + "\n")


# Match SHARK reported scientific names.
shark_reported_file_path = pathlib.Path(
    "data_in/sharkweb_data_HELA_DYNTAXA_EJ_TRANSLATE.txt"
)
reported_list = []
with shark_reported_file_path.open("r") as f:
    for index, line in enumerate(f.readlines()):
        if index > 0:  # Not header.
            reported_name = line.strip().split("\t")[0]
            reported_list.append(reported_name.strip())
print("SHARK reported taxa - length: ", len(reported_list))

# Match SHARK reported scientific names.
shark_translate_file_path = pathlib.Path(
    "data_in/translate_to_dyntaxa_FROM_SHARK_CONFIG.txt"
)
lookup_shark_translate_dict = {}
header = []
with shark_translate_file_path.open("r") as f:
    for index, line in enumerate(f.readlines()):
        row_parts = [x.strip() for x in line.split("\t")]
        if index == 0:
            header = row_parts
        else:
            row_dict = dict(zip(header, row_parts))
            taxon_name_from = row_dict.get("taxon_name_from", "")
            taxon_name_to = row_dict.get("taxon_name_to", "")
            taxon_id_to = row_dict.get("taxon_id (if not in DynTaxa)", "")
            if taxon_name_from:
                if taxon_id_to:
                    lookup_shark_translate_dict[taxon_name_from] = taxon_id_to
                elif taxon_name_to:
                    lookup_shark_translate_dict[taxon_name_from] = taxon_name_to
print("SHARK translate - length: ", len(lookup_shark_translate_dict))


# FINAL MATCH.
match_result = []
header = [
    "reported_scientific_name",
    "shark_translate",
    "dyntaxa_id",
    "dyntaxa_scientific_name",
    "rank",
    "match_result",
    "multiple_ids",
    "GUID",
]
match_result.append(header)
for shark_name in reported_list:
    result_row = {}
    result_row["reported_scientific_name"] = shark_name
    shark_translate = lookup_shark_translate_dict.get(shark_name, "")
    result_row["shark_translate"] = shark_translate
    # Check.
    taxon_id_list = []
    # Check dyntaxa.
    if shark_name in lookup_name_dyntaxa_dict:
        taxon_id_list = lookup_name_dyntaxa_dict[shark_name]
        result_row["match_result"] = "OK-DYNTAXA"
    # Check shark translate.
    elif shark_translate in lookup_name_dyntaxa_dict:
        taxon_id_list = lookup_name_dyntaxa_dict[shark_translate]
        result_row["match_result"] = "OK-TRANSLATE"
    # Check dyntaxa synonyms.
    elif shark_name in lookup_name_dyntaxa_synonyms_dict:
        taxon_id_list = lookup_name_dyntaxa_synonyms_dict[shark_name]
        result_row["match_result"] = "OK-SYNONYM"
    #
    if len(taxon_id_list) == 0:
        result_row["match_result"] = "NOT FOUND"
    if len(taxon_id_list) == 1:
        pass
        # result_row["match_result"] = "OK"
    if len(taxon_id_list) > 1:
        result_row["match_result"] = "MULTIPLE-FIRST USED"
        result_row["multiple_ids"] = str(taxon_id_list)

    taxon_id = ""
    if len(taxon_id_list) >= 1:
        taxon_id = taxon_id_list[0]
        if taxon_id in dyntaxa_dict:
            taxon_dict = dyntaxa_dict[taxon_id]
            result_row["dyntaxa_id"] = taxon_dict.get("TaxonId", "")
            result_row["dyntaxa_scientific_name"] = taxon_dict.get("ScientificName", "")
            result_row["rank"] = taxon_dict.get("TaxonCategory", "")
            result_row["GUID"] = taxon_dict.get("RecommendedGUID", "")
        else:
            print("ERROR: ", taxon_id)
            result_row["dyntaxa_id"] = taxon_id
            result_row["match_result"] = "ERROR-ID-MISSING"

    row = []
    for item in header:
        row.append(result_row.get(item, ""))
    match_result.append(row)

# Save to file.
lookup_file_path = pathlib.Path("data_out/match_result.txt")
with lookup_file_path.open("w", errors="replace") as file:
    for row in match_result:
        file.write("\t".join(row) + "\n")

print("Done...")
