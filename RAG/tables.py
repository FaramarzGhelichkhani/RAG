import json
from typing import List

with open("tables.json", "r") as file:
    tables = json.load(file)

class TableEnum:
    def __init__(self, name, schema, description, prefix, query_explanation=""):
        self.name = name
        self.schema = schema
        self.description = description
        self.prefix = prefix
        self.query_explanation = query_explanation

class Table:
    FACTTRADE = TableEnum(**tables["FACTTRADE"])
    DIMDATE = TableEnum(**tables["DIMDATE"])
    FACTPORTFOLIOLATEST = TableEnum(**tables["FACTPORTFOLIOLATEST"])
    FACTPORTFOLIOMUTUALFUND = TableEnum(**tables["FACTPORTFOLIOMUTUALFUND"])
    FACTDAILYISSUERINDEX = TableEnum(**tables["FACTDAILYISSUERINDEX"])
    FACTDAILYFUND = TableEnum(**tables["FACTDAILYFUND"])
    DIMCUSTOMERFUND = TableEnum(**tables["DIMCUSTOMERFUND"])
    FACTCUSTOMERINVESTFUND = TableEnum(**tables["FACTCUSTOMERINVESTFUND"])
    HUBCUSTOMER_VC = TableEnum(**tables["HUBCUSTOMER_VC"])
    DIMCUSTOMER_VC = TableEnum(**tables["DIMCUSTOMER_VC"])
    DIMISSUER = TableEnum(**tables["DIMISSUER"])
    
    @classmethod
    def get_tables_descriptions(cls):
        desc = ""
        for attr in dir(cls):
            if not callable(getattr(cls, attr)) and not attr.startswith("__"):
                desc += getattr(cls, attr).name + " "
                desc += getattr(cls, attr).description
                desc += "\n"
        return desc
    
    @classmethod
    def get_table_query_explanation(cls, tables_name:List[str]):
        exp = ""
        if len(tables_name)==0:
            attrs = [attr for attr in dir(cls) if not callable(getattr(cls, attr)) and not attr.startswith("__") ]
        else:    
            attrs = [attr.upper() for attr in tables_name]
        for attr in attrs:
            exp += "in " + getattr(cls, attr).prefix + "."  + getattr(cls, attr).name + " "
            exp += getattr(cls, attr).query_explanation 
            exp += "\n"
        return exp
    
    @classmethod
    def get_table_schema(cls, tables_name:List[str]):
        sch = ""
        if len(tables_name)==0:
            attrs = [attr for attr in dir(cls) if not callable(getattr(cls, attr)) and not attr.startswith("__") ]
        else:    
            attrs = [attr.upper() for attr in tables_name]
        for attr in attrs:
            sch +=  getattr(cls, attr).prefix + "." + getattr(cls, attr).name + " schema : \n"
            sch += str(getattr(cls, attr).schema) 
            sch += "\n"
        return sch
    