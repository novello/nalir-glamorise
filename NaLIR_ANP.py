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

from nalir import *

config_json_text = '''{
    "connection":{
        "host": "localhost",
        "password":"desenvolvimento123",
        "user":"nalir",
        "database":"anp"
    },
    "loggingMode": "ERROR",
    "zfiles_path":"/home/novello/nalir-glamorise/zfiles",
    "jars_path":"/home/novello/nalir-glamorise/jars/new_jars"
}
'''
config = ConfigHandler(reset=True,config_json_text=config_json_text)

rdbms = RDBMS(config)

# nlq_before='What was the monthly production of oil in the state of Rio de Janeiro and year 2015?'
# change_order = true
# relace_text = {monthly : per year per month}
# nlq_after='What was the production of oil per year per month in the state of Rio de Janeiro and year 2015?'
# nlq_before='What was the the field with the highest gas production?'
# replace_text_before = {gas production : production of gas} <-- ainda não precisa envelope noun resolve
# envelope_noun = true
# relace_text = {highest : per}
# nlq_after='What was the the field with the per "production of gas"?'
#nlq='What was the "production of oil" per "year" per "month" in the state of Rio de Janeiro and year 2015?'

nlq='What was the the field with the highest anp_gas_production?'
query = Query(nlq,rdbms.schema_graph)

# ## Stanford Dependency Parser

StanfordParser(query,config)
query.parse_tree

# **Important Note**: The graph vizualitation requires the program [Graphviz](https://graphviz.org/) (alongside with the graphviz python package) to be installed.

query.parse_tree.show()

# ## Node Mapper
import nltk
#nltk.download('averaged_perceptron_tagger')
#nltk.download('wordnet')
#nltk.download('punkt')
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
print('nlq: ', nlq)
print('query: ', query.translated_sql)
