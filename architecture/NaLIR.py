# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: NaLIR-SBBD
#     language: python
#     name: nalir-sbbd
# ---

# +
from rdbms.rdbms import RDBMS
from data_structure.query import Query
from components.stanford_parser import StanfordParser
from components.node_mapper import NodeMapper
from components.entity_resolution import entity_resolute
from components.tree_structure_adjustor import TreeStructureAdjustor
from components.explainer import explain
from components.sql_translator import translate

from config import ConfigHandler
# -

config_json_text = '''{
    "connection":{
        "host": "localhost",
        "password":"paulo",
        "user":"paulo",
        "database":"mas"
    },
    "defaultImplementation": true,
    "loggingMode": "ERROR",
    "zfiles_path":"/home/pr3martins/Desktop/zfiles",
}
'''
config = ConfigHandler(reset=True,config_json_text=config_json_text)

rdbms = RDBMS(config)

query_line='return me the authors who have papers in VLDB conference before 2002 after 1995.'
query = Query(query_line,rdbms.schema_graph)

# ## Stanford Dependency Parser

StanfordParser(query)
query.parse_tree

# **Important Note**: The graph vizualitation requires the program [Graphviz](https://graphviz.org/) (alongside with the graphviz python package) to be installed.

query.parse_tree.show()

# ## Node Mapper

NodeMapper.phrase_process(query,rdbms,config)

query.parse_tree.show()

# ##  Entity Resolution

# The entity pairs denote that two nodes represente the same entity.

entity_resolute(query)
query.entities

# ## Tree Structure Adjustor

TreeStructureAdjustor.tree_structure_adjust(query,rdbms)
query.query_tree.show()

# ## Explainer

explain(query)
query.query_tree.show()

# ## SQL Translator

# **Important Node**: The error message is resultant of line 191 of file data_structure/block.py

translate(query, rdbms)
print(query.translated_sql)
