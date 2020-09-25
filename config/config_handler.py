import json
import os
from .debug_mode import debug_mapping

obj = {'mas': 'mas', 'mondial': 'Mondial', 'imdb':'imdb_v02'}
class ConfigHandler:
	
	__instance = None
	def __init__(self, database='', reset=False):

		if ConfigHandler.__instance is None or reset:
			config_path = '/'.join(__file__.split('/')[:-1] + ['config.json'])
			config_file = open(config_path, 'r')
			 
			ConfigHandler.__instance = json.load(config_file)
			ConfigHandler.__instance.setdefault('table_file', None)
			dataset_config = database if database != '' else ConfigHandler.__instance['databaseConfig']
			print('database: ', database)
			dataset_config_path = '/'.join(__file__.split('/')[:-1] \
				+ ['{}_config.json'.format(dataset_config.lower())])

			ConfigHandler.__instance['connection']['database'] = obj[dataset_config]
			config_database_file = open(dataset_config_path, 'r') 
			
			ConfigHandler.__instance.update(json.load(config_database_file))
			ConfigHandler.__instance['loggingMode'] = \
				debug_mapping[ConfigHandler.__instance['loggingMode']]
			print(ConfigHandler.__instance)

		self.__dict__ = ConfigHandler.__instance
		
