import mysql.connector
from nltk.corpus import wordnet as wn
from .schema_graph import SchemaGraph

class RDBMS:
    def __init__(self, config):
        config_obj = config.connection
        self.conection = mysql.connector.connect(user=config_obj['user'],\
            password=config_obj['password'], host= config_obj['host'],\
            database=config_obj['database'])
        self.schema_graph = SchemaGraph(config_obj['database'],config)

    def conduct_sql(self, query):
        cursor = self.conection.cursor()
        cursor.execute(query)
        results = []
        for line in cursor:
            results += [line]

        return None

    def is_schema_exist(self, tree_node):
        attributes = self.schema_graph.get_elements_by_type('text number')

        for attribute in attributes:
            element = attribute.is_schema_exist(tree_node.label)

            if element is not None:
                tree_node.mapped_elements += [element]

        if len(tree_node.mapped_elements) != 0:
            return True
        else:
            return False

    def is_num_exist(self, operator, tree_node):
        text_attributes = self.schema_graph.get_elements_by_type('number')
        for text_attribute in text_attributes:
            element = text_attribute.is_num_exist(tree_node.label, operator, self.conection)
            if element is not None:
                tree_node.mapped_elements += [element]

        if len(tree_node.mapped_elements) != 0:
            return True
        else:
            return False

    def is_text_exist(self, tree_node):
        text_attributes = self.schema_graph.get_elements_by_type('text')

        for text_attribute in text_attributes:
            element = text_attribute.is_text_exist(tree_node.label, self.conection)
            if element is not None:
                tree_node.mapped_elements.append(element)

        if len(tree_node.mapped_elements) != 0:
            return True
        else:
            return False
