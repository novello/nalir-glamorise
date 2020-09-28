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
logger.debug("Loading inverted index")
begin = time.time()
LateCandidateMapper()
end = time.time()
logger.debug("time to load verted index : {0}".format((end - begin) / 60.0))
    
f_output = open(rel_file, 'w+')
f_output.write('query |nalir_top#1 |  nalir top#2 | nalir top#3 | nalir top#4 | only_nalir_result | top #10 matches | scores |top #10 score matches| scores |all matches | all_scores |\n')

i = 1
with open(query_file, 'r') as f:
    for line in f.readlines():
        results = []
        processed_line = line.split('\n')[0]
        logger.debug(str(i) + ") ### {0}".format(processed_line))
        queryOne = Query(processed_line,rdbms.schema_graph)

        queryTwo = deepcopy(queryOne)
        response =  None
        try:
            StanfordParser(queryTwo)
            NodeMapper.phrase_process(queryTwo,rdbms,tokens,False)
            entity_resolute(queryTwo)
            TreeStructureAdjustor.tree_structure_adjust(queryTwo,rdbms)
            explain(queryTwo)
            translate(queryTwo, rdbms)
            logger.debug('2 {0}'.format(queryTwo.translated_sql.replace('\n', ' ')))
        
            for j in range(1,5):
                queryTmp = deepcopy(queryOne)
                StanfordParser(queryOne)
                
                if response is not None:
                    NodeMapper.phrase_process(queryOne,rdbms,tokens, True, j, response)
                else:
                    response = NodeMapper.phrase_process(queryOne,rdbms,tokens, True, j)

                entity_resolute(queryOne)            
                TreeStructureAdjustor.tree_structure_adjust(queryOne,rdbms)
                explain(queryOne)
                translate(queryOne, rdbms)
                results += [queryOne.translated_sql.replace('\n', ' ')]
                logger.debug('{2}->{1}) ### {0}'.format(queryOne.translated_sql.replace('\n', ' '), j, i))
  
        except Exception as e:
            logger.error("error {0}".format(e))

        if response is None:    
            f_output.write("{0}|{1}|{2}||\n".format(processed_line, \
                queryOne.translated_sql.replace('\n', ' '), \
                queryTwo.translated_sql.replace('\n', ' ')))
        else:
            size = 10 
            max_size = 10
            different_score = response[2][0][1]
            different_size = 0
            all_size = 0
            for idx,match in enumerate(response[2]):
                if idx == 0:
                    continue

                if different_score != match[1]:
                    
                    if different_size == 5:
                        break

                    different_score = match[1]
                    different_size += 1
                    all_size = idx

            print('all_size', all_size, 'diff_size', different_size)
            if len(response[2]) < size:
                size = len(response[2])
            f_output.write("{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}|{9}|{10}|{11}|\n".format( processed_line, \
                results[0],results[1],results[2],results[3], \
                queryTwo.translated_sql.replace('\n', ' '),\
                [x[0] for x in response[2]][:size],\
                [x[1] for x in response[2]][:size],\
                [x[0] for x in response[2]][:all_size],\
                [x[1] for x in response[2]][:all_size],\
                [x[0] for x in response[2]],\
                [x[1] for x in response[2]] ))
        results = []
        f_output.flush()


        i+=1

f_output.close()

