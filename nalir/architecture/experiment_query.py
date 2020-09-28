import sys
sys.path.append('../')

import os
import logging
import xml.etree.ElementTree as et

from nalir.data_structure.query import Query
from nalir.components.stanford_parser import StanfordParser
from nalir.components.node_mapper import NodeMapper
from nalir.components.entity_resolution import entity_resolute
from nalir.components.tree_structure_adjustor import TreeStructureAdjustor
from nalir.components.explainer import explain
from nalir.components.sql_translator import translate


def run_query(nl_query, rdbms, config):
    query = Query(nl_query,rdbms.schema_graph)
    
    StanfordParser(query, config)
    NodeMapper.phrase_process(query,rdbms,config)
    entity_resolute(query)
    TreeStructureAdjustor.tree_structure_adjust(query,rdbms)
    translate(query, rdbms)
    explain(query)
    return query.translated_sql.replace('\n', ' ')