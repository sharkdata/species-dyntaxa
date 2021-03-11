#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import openpyxl
import datetime
import dyntaxa_db_cache


print("\n\n=== Dyntaxa to DB started. ===")

excel_file = "data_in/Dyntaxa database export 2021-01-18.xlsx"
print("Loaded Excel.")
wb = openpyxl.load_workbook(excel_file, read_only=True)
print("Excel loaded")
# print(wb.sheetnames)
# 'Taxon'
# 'TaxonName'
# 'TaxonParentRelation'
# 'TaxonSplitRelation'
# 'TaxonLumpRelation'
# 'TaxonNameReferences'
# 'TaxonCategories'
# 'TaxonNameCategories'
# 'TaxonNameStatus'
# 'TaxonNameUsage'
# 'TaxonChangeStatus'
# 'TaxonAlertStatus'
# 'ReferenceList'


def sheet_to_dict(excel_sheet, columns):
    """ """
    result_list = []
    dyntaxa_sheet = excel_sheet
    header = None
    for row in dyntaxa_sheet:
        row_list = []
        for cell in row:
            row_list.append(str(cell.value).strip())
        if header is None:
            header = row_list
        else:
            row_dict = dict(zip(header, row_list))
            short_dict = {}
            for key in columns:
                short_dict[key] = row_dict.get(key, "")
            result_list.append(short_dict)
    #
    return result_list


dyntaxa_columns = [
    "TaxonId",
    "ScientificName",
    "Author",
    "TaxonCategoryId",
    "TaxonCategory",
    "IsValid",  # Use True
    "ValidFromDate",
    "ValidToDate",
    "RecommendedGUID",
]

dyntaxa_name_columns = [
    "TaxonId",
    "Name",
    "IsRecommended",
    "NameCategoryId",  # 0=scientific name
    "NameUsageId",  # 1=synonym
    "NameStatusId",  # 0=valid
    "ValidFromDate",
    "ValidToDate",
]

dyntaxa_parent_columns = [
    "ChildTaxonId",
    "ParentTaxonId",
]

print("Reading dyntaxa sheet.")
dyntaxa_list = sheet_to_dict(wb["Taxon"], dyntaxa_columns)
print("- dyntaxa length: ", len(dyntaxa_list))

print("Reading dyntaxaName sheet.")
dyntaxa_name_list = sheet_to_dict(wb["TaxonName"], dyntaxa_name_columns)
print("- dyntaxaName length: ", len(dyntaxa_name_list))

print("Reading dyntaxaParentRelation sheet.")
dyntaxa_parent_list = sheet_to_dict(wb["TaxonParentRelation"], dyntaxa_parent_columns)
print("- dyntaxaParent length: ", len(dyntaxa_parent_list))

# Select valid rows.
dyntaxa_list_db = []
for taxon in dyntaxa_list:
    taxon_id = taxon["TaxonId"]
    if taxon["IsValid"] != "True":
        continue
    today_datetime = datetime.datetime.now()
    valid_from_datetime = datetime.datetime.fromisoformat(taxon["ValidFromDate"])
    valid_to_datetime = datetime.datetime.fromisoformat(taxon["ValidToDate"])
    if (today_datetime < valid_from_datetime) or (today_datetime > valid_to_datetime):
        continue
    # Add to db.
    dyntaxa_list_db.append(taxon)

dyntaxa_name_list_db = []
for taxon in dyntaxa_name_list:
    taxon_id = taxon["TaxonId"]
    # Only use scientific name (0=scientific name).
    if taxon["NameCategoryId"] != "0":
        continue
    # # Only use Synonyms (1=synonym).
    # if taxon["NameUsageId"] != "1":
    #     continue
    # Add to db.
    dyntaxa_name_list_db.append(taxon)

dyntaxa_parent_list_db = []
for taxon in dyntaxa_parent_list:
    parent_id = taxon["ParentTaxonId"]
    taxon_id = taxon["ChildTaxonId"]
    # Skip organism group "Algae"
    if parent_id == "6001047":
        continue
    # Add to db.
    dyntaxa_parent_list_db.append(taxon)


print("Write to database.")
db = dyntaxa_db_cache.DyntaxaDbCache()
db.add_dyntaxa_list(dyntaxa_list_db)
db.add_dyntaxa_name_list(dyntaxa_name_list_db)
db.add_dyntaxa_parent_list(dyntaxa_parent_list_db)

print("Done...")
