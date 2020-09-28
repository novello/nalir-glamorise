import sys
sys.path.append('../')

import sys
sys.path.append('../')

import os
import time 
import logging
import xml.etree.ElementTree as et

from rdbms.rdbms import RDBMS
from data_structure.query import Query 
from components.stanford_parser import StanfordParser
from components.node_mapper import NodeMapper
from components.entity_resolution import entity_resolute
from components.tree_structure_adjustor import TreeStructureAdjustor
from components.explainer import explain
from components.sql_translator import translate
from misc.similarity import load_model
from misc.process_command import CommandProcessor
from copy import deepcopy
from data_structure.parse_tree import ParseTree
from inverted_index import  LateCandidateMapper

from config import ConfigHandler
from config import get_logger

logger = get_logger(__file__)
config = ConfigHandler()

if len(sys.argv) != 3:
    print('usage python {0} <process_file> <output_file>'.format(sys.argv[0]))
    sys.exit()


query_file = sys.argv[1]
rel_file = sys.argv[2]
if not os.path.isfile(query_file):
    print('Please type a valid file')
    sys.exit()


token_path = '/'.join(os.getcwd().split('/')[:-1] + ['zfiles', 'tokens.xml'])


tokens = et.parse(token_path)
rdbms = RDBMS(config.connection)
    
f_output = open(rel_file, 'w')
f_output.write('query | nalir_matches | nalir_result |\n')

i = 1
with open(query_file, 'r') as f:
    for line in f.readlines():
        results = []
        processed_line = line.split('\n')[0]
        logger.debug(str(i) + ") ### {0}".format(processed_line))
        
        queryOne = Query(processed_line,rdbms.schema_graph)
        result_map = ""
        response =  None
        try:
            StanfordParser(queryOne)
            result_map = NodeMapper.phrase_process(queryOne,rdbms,tokens,False)
            entity_resolute(queryOne)
            TreeStructureAdjustor.tree_structure_adjust(queryOne,rdbms)
            explain(queryOne)
            translate(queryOne, rdbms)
            logger.debug('2 {0}'.format(queryOne.translated_sql.replace('\n', ' ')))        
  
        except Exception as e:
            logger.error("error {0}".format(e))

        if result_map == "":    
            f_output.write("|{0}|{1}||\n".format(processed_line, \
                queryOne.translated_sql.replace('\n', ' ')))
        else:
            f_output.write("|{0}|{1}|{2}|\n".format(processed_line, \
                result_map, \
                queryOne.translated_sql.replace('\n', ' ')))
        
        f_output.flush()


        i+=1

f_output.close()

