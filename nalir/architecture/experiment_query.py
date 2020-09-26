import sys
sys.path.append('../')

import os
import logging
import xml.etree.ElementTree as et

from rdbms.rdbms import RDBMS
from data_structure.query import Query
from components.stanford_parser import StanfordParser
from components.node_mapper import NodeMapper
from components.entity_resolution import entity_resolute
from components.tree_structure_adjustor import TreeStructureAdjustor
from components.sql_translator import translate


def run_query(nl_query, rdbms, config):
    query = Query(nl_query,rdbms.schema_graph)
    
    StanfordParser(query)
    NodeMapper.phrase_process(query,rdbms,config)
    entity_resolute(query)
    TreeStructureAdjustor.tree_structure_adjust(query,rdbms)
    translate(query, rdbms)
    
    return query.translated_sql