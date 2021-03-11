#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import pathlib
import sqlite3
import json


class DyntaxaDbCache:
    """ """

    def __init__(self, db_file="data_in/dyntaxa_db_cache_2.db"):
        """ """
        self.db_file = db_file
        self.db_path = pathlib.Path(self.db_file)

    def create_db(self):
        """ """
        db_con = sqlite3.connect(self.db_path)
        with db_con:
            # From DynTaxa Excel sheets.
            db_con.execute(
                "CREATE TABLE dyntaxa(taxon_id varchar(20) PRIMARY KEY, data json)"
            )
            db_con.execute("CREATE TABLE dyntaxa_name(data json)")
            db_con.execute("CREATE TABLE dyntaxa_parent(data json)")
            # Calculated stuff.
            db_con.execute(
                "CREATE TABLE taxa(taxon_id varchar(20) PRIMARY KEY, data json)"
            )

    def connect(self):
        """ """
        if not self.db_path.exists():
            self.create_db()
        #
        return sqlite3.connect(self.db_path)

    def add_dyntaxa_list(self, dyntaxa_list, append=False):
        """ """
        with self.connect() as con:
            if append == False:
                con.execute("delete from dyntaxa")
            for dyntaxa_dict in dyntaxa_list:
                taxon_id = dyntaxa_dict.get("TaxonId", "")
                if taxon_id != "":
                    try:
                        con.execute(
                            "insert into dyntaxa values (?, ?)",
                            (
                                taxon_id,
                                json.dumps(
                                    dyntaxa_dict,
                                ),
                            ),
                        )
                    except Exception as e:
                        print("Exception in dyntaxa, id:  ", taxon_id, "   ", e)

    def get_dyntaxa_dict(self):
        """ """
        dyntaxa_dict = {}
        with self.connect() as con:
            cur = con.cursor()
            cur.execute("select data from dyntaxa")
            for row in cur:
                row_dict = json.loads(row[0])
                taxa_id = row_dict["TaxonId"]
                dyntaxa_dict[taxa_id] = row_dict
            cur.close()
        # print("Length dyntaxa: ", len(dyntaxa_dict))
        return dyntaxa_dict

    def add_dyntaxa_name_list(self, dyntaxa_name_list, append=False):
        """ """
        with self.connect() as con:
            if append == False:
                con.execute("delete from dyntaxa_name")
            for dyntaxa_dict in dyntaxa_name_list:
                taxon_id = dyntaxa_dict.get("TaxonId", "")
                if taxon_id != "":
                    try:
                        con.execute(
                            "insert into dyntaxa_name values (?)",
                            (json.dumps(dyntaxa_dict),),
                        )
                    except Exception as e:
                        print("Exception in dyntaxa_name, id:  ", taxon_id, "   ", e)

    def get_dyntaxa_name_list(self):
        """ """
        dyntaxa_name_list = []
        with self.connect() as con:
            cur = con.cursor()
            cur.execute("select data from dyntaxa_name")
            for row in cur:
                row_dict = json.loads(row[0])
                dyntaxa_name_list.append(row_dict)
            cur.close()
        # print("Length dyntaxa_name: ", len(dyntaxa_name_list))
        return dyntaxa_name_list

    def add_dyntaxa_parent_list(self, dyntaxa_parent_list, append=False):
        """ """
        with self.connect() as con:
            if append == False:
                con.execute("delete from dyntaxa_parent")
            for dyntaxa_dict in dyntaxa_parent_list:
                # taxon_id = taxon_dict.get("TaxonId", "")
                taxon_id = dyntaxa_dict.get("ChildTaxonId", "")
                if taxon_id != "":
                    try:
                        con.execute(
                            "insert into dyntaxa_parent values (?)",
                            (json.dumps(dyntaxa_dict),),
                        )
                    except Exception as e:
                        print("Exception in dyntaxa_parent, id:  ", taxon_id, "   ", e)

    def get_dyntaxa_parent_list(self):
        """ """
        dyntaxa_parent_list = []
        with self.connect() as con:
            cur = con.cursor()
            cur.execute("select data from dyntaxa_parent")
            for row in cur:
                row_dict = json.loads(row[0])
                dyntaxa_parent_list.append(row_dict)
            cur.close()
        # print("Length dyntaxa_parent: ", len(dyntaxa_parent_list))
        return dyntaxa_parent_list

    def add_taxa_list(self, taxa_list, append=False):
        """ """
        with self.connect() as con:
            if append == False:
                con.execute("delete from taxa")
            for taxa_dict in taxa_list:
                taxon_id = taxa_dict.get("TaxonId", "")
                if taxon_id != "":
                    try:
                        con.execute(
                            "insert into taxa values (?, ?)",
                            (
                                taxon_id,
                                json.dumps(
                                    taxa_dict,
                                ),
                            ),
                        )
                    except Exception as e:
                        print("Exception in taxa, id:  ", taxon_id, "   ", e)

    def get_taxa_dict(self):
        """ """
        taxa_dict = {}
        with self.connect() as con:
            cur = con.cursor()
            cur.execute("select data from taxa")
            for row in cur:
                row_dict = json.loads(row[0])
                taxa_id = row_dict["TaxonId"]
                taxa_dict[taxa_id] = row_dict
            cur.close()
        # print("Length taxa: ", len(taxa_dict))
        return taxa_dict
