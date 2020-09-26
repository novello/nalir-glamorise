

class MappedSchemaElement:

    def __init__(self, schema_element):
        self.schema_element = schema_element
        self.similarity = -1
        self.mapped_values = []
        self.choice = -1

    def __lt__(self, other):
        if other is not None: 
            return self.similarity < other.similarity
        return False

    def __gt__(self, other):
        if other is not None:
            return self.similarity > other.similarity
        return False


    def __eq__(self, other):
        if other is not None:
            return self.similarity == other.similarity
        return False


    def __ne__(self, other):
        if other is not None:
            return self.similarity != other.similarity
        return False


    def __ge__(self, other):
        if other is not None:
            return self.similarity >= other.similarity
        return False      


    def __le__(self, other):
        if other is not None:
            return self.similarity <= other.similarity
        return False


    def __repr__(self):
        result = ''
        result += '{0}.{1} ({2}):'.format(self.schema_element.relation.name,self.schema_element.name, self.similarity)

        if len(self.mapped_values) > 0 and self.choice >= 0:
            result += '{0}'.format(self.mapped_values[0].encode('ascii', 'ignore'))
        else:
            result += 'choice == {0}'.format(self.choice)
        return result
