import json
import os
from .debug_mode import debug_mapping

class ConfigHandler:

	__instance = None
	def __init__(self, database='', reset=False, config_json_text=None):

		if ConfigHandler.__instance is None or reset:

			if config_json_text is None:
				config_path = os.sep.join(__file__.split(os.sep)[:-1] + ['config.json'])				
				config_file = open(config_path, 'r')

				ConfigHandler.__instance = json.load(config_file)
				ConfigHandler.__instance.setdefault('table_file', None)

				#dataset_config = database if database != '' else ConfigHandler.__instance['databaseConfig']
				# dataset_config_path = '/'.join(__file__.split('/')[:-1] \
				# 	+ ['{}_config.json'.format(dataset_config.lower())])

				#config_database_file = open(dataset_config_path, 'r')
				#ConfigHandler.__instance.update(json.load(config_database_file))

				# Moving the specific database name to connection string
				#ConfigHandler.__instance['connection']['database'] = ConfigHandler.__instance['database']
				#del ConfigHandler.__instance['database']

				ConfigHandler.__instance['loggingMode'] = \
					debug_mapping[ConfigHandler.__instance['loggingMode']]
			else:
				ConfigHandler.__instance = json.loads(config_json_text)
				ConfigHandler.__instance.setdefault('table_file', None)

		self.__dict__ = ConfigHandler.__instance
