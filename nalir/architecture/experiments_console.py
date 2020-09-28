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
from components.explainer import explain
from components.sql_translator import translate

from misc.process_command import CommandProcessor

from config import ConfigHandler
from config import get_logger

database = '' if len(sys.argv) < 2 else sys.argv[1]
print(database)
config = ConfigHandler(database=database,reset=True)
logger = get_logger(__name__)

token_path = '/'.join(os.getcwd().split('/')[:-1] + ['zfiles', 'tokens.xml'])

command_processor = CommandProcessor()
tokens = et.parse(token_path)
print("load")
rdbms = RDBMS(config.connection)
print("loaded")
if config.defaultImplementation:
	logger.debug('entering data')


query_line='#query return me the publications of "H. V. Jagadish".'
print(query_line)
query_processed = command_processor.process_input(query_line)

while query_processed != CommandProcessor.EXIT_COMMAND:
	logger.debug('building query')
	query = Query(query_processed,rdbms.schema_graph)

	logger.info('Stanford Parser running')
	StanfordParser(query)

	logger.info('Node mapper running')
	NodeMapper.phrase_process(query,rdbms,tokens)

	logger.info(query.parse_tree)

	logger.info('Resolution Entities running')
	entity_resolute(query)
	logger.info(query.entities)

	logger.info('Tree Structure Adjustor running')
	TreeStructureAdjustor.tree_structure_adjust(query,rdbms)
	logger.info('query tree:\n{0}'.format(query.query_tree))

	logger.info('Explainer running')
	explain(query)
	logger.info('query tree:\n{0}'.format(query.query_tree))
	logger.info('Translate running')
	translate(query, rdbms)

	logger.info('sql:\n{0}'.format(query.translated_sql))

	break

	query_line = input("Input a query: ")
	query_processed = command_processor.process_input(query_line)
