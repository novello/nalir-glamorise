from .mapped_schema_element import MappedSchemaElement
from ..misc.similarity import similarity_words, if_schema_similar

class SchemaElement:

    def __init__(self, id=-1, name=None, type_elem=None):
        self.element_id = id
        self.name = name
        self.type = type_elem
        self.relation = None
        self.attributes = []
        self.primary_key = None
        self.default_attribute = None
        self.in_elements = []

    def is_schema_exist(self, tag):
        mapped_schema_element = None
        if self == self.relation.default_attribute:  
            if if_schema_similar(self.relation.name, tag) or if_schema_similar(self.name, tag):
                mapped_schema_element = MappedSchemaElement(self)
                mapped_schema_element.similarity = similarity_words(self.relation.name, tag)
                mapped_schema_element.similarity = 1 - (1 - mapped_schema_element.similarity) * (1 -
                    similarity_words(self.name,tag))
                

        elif if_schema_similar  (self.name, tag):
            
            mapped_schema_element = MappedSchemaElement(self)
            mapped_schema_element.similarity = similarity_words(self.name, tag)

        return mapped_schema_element


    def is_text_exist(self, value, connection):
        sql = 'select * from size WHERE size.relation = \'{0}\''.format(self.relation.name) 
        cursor = connection.cursor()
        cursor.execute(sql)
        size = 0
        for (line) in cursor:
            size = line[0]

        sql = ''
        if size < 2000:
            sql = 'select {0} from {1}'.format(self.name, self.relation.name)

        elif size >= 2000 and size < 100000:
            sql = 'select {0} from {1} where {2} like \'%{3}%\' LIMIT 0,2000'.format(self.name, self.relation.name, self.name ,value)

        else:
            sql = 'select {0} from {1} where match({2}) against(\'{3}\') LIMIT 0,2000'.format(self.name, self.relation.name, self.name ,value) 
        mapped_schema_element = MappedSchemaElement(self)
        cursor = connection.cursor()
        
        cursor.execute(sql)
        for (line) in cursor:
            mapped_schema_element.mapped_values += [line[0]]


        if len(mapped_schema_element.mapped_values) != 0:
            return mapped_schema_element

        return None


    def is_num_exist(self,number, operator, connection):
        cursor = connection.cursor()
        sql = 'select {0} from {1} where {2} {3} {4} LIMIT 0, 5'.format(self.name, self.relation.name, self.name, operator, number)
        cursor.execute(sql)
        mapped_schema_element = MappedSchemaElement(self)

        for (line) in cursor:
            mapped_schema_element.mapped_values += [str(line[0])]

        if len(mapped_schema_element.mapped_values) != 0:

            return mapped_schema_element

        return None


    def print_for_check(self):
        print('{0}.{1};\n'.format(self.relation.name, self.name))


    def __repr__(self):
        return '{2}: {0}.{1}; '.format(self.relation.name, self.name, self.element_id)
