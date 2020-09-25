import json
import os
import numpy as np
from .edge import Edge
from .schema_element import SchemaElement

class SchemaGraph:
    KEY_EDGE = 0.99
    REL_EDGE = 0.995
    ATT_EDGE = 0.995

    def __init__(self, name, config):

        self.default_path = config.zfiles_path+'/{0}{1}.json'

        self.schema_elements = []
        self.weight = None
        self.path_graph_file = self.default_path.format(name, "Relations")
        with open(self.path_graph_file, 'r') as file:
            self.raw_graph_relation = json.load(file)
            for node in self.raw_graph_relation:
                relation = SchemaElement(len(self.schema_elements), node['name'], node['type'])
                relation.relation = relation

                self.schema_elements += [relation]
                for raw_attribute in node['attributes']:
                    attribute = SchemaElement(len(self.schema_elements), raw_attribute['name'], raw_attribute['type'])
                    attribute.relation = relation
                    relation.attributes += [attribute]
                    self.schema_elements += [attribute]

                    if raw_attribute.get('importance', None) is not None:
                        relation.default_attribute = attribute

                    if raw_attribute.get('type', None) == 'pk':
                        relation.primary_key = attribute

        self.weights = np.zeros((len(self.schema_elements), \
            len(self.schema_elements)))

        self.shortest_distance = np.zeros((len(self.schema_elements), \
            len(self.schema_elements)))


        relations = self.get_elements_by_type('relationship entity')
        for relation in relations:
            for attribute in relation.attributes:
                self.weights[relation.element_id][attribute.element_id] = self.ATT_EDGE

        self.path_edges_file = self.default_path.format(name, "Edges")
        with open(self.path_edges_file, 'r') as file:
            self.raw_edge_relation = json.load(file)
            for edge in self.raw_edge_relation:
                fk = self.search_attribute(edge['foreignRelation'], edge['foreignAttribute'])
                pk = self.search_relation(edge['primaryRelation'])
                if self.schema_elements[fk].relation.type == 'relationship':
                    self.weights[fk][pk] = self.REL_EDGE
                else:
                    self.weights[fk][pk] = self.KEY_EDGE
                self.schema_elements[pk].in_elements += [self.schema_elements[fk]]

        self.shortest_distance_compute()



    def shortest_distance_compute(self):
        self.shortest_distance = np.zeros(self.weights.shape)
        self.pre_elements = np.zeros(self.weights.shape, dtype=np.int32)

        for i in range(self.weights.shape[0]):
            for j in range(self.weights.shape[1]):
                if self.weights[i][j] > self.weights[j][i]:
                    self.weights[j][i] = self.weights[i][j]

            self.weights[i][i] = 1

        for i in range(self.weights.shape[0]):
            for j in range(self.weights.shape[1]):
                self.shortest_distance[i][j] = self.weights[i][j]

        for i in range(self.weights.shape[0]):
            self.dijkstra(i)


    def dijkstra(self, source):
        local_distance = np.zeros((len(self.schema_elements)))
        for i in range(local_distance.shape[0]):
            local_distance[i] = self.weights[source][i]

        for i in range(self.pre_elements.shape[0]):
            self.pre_elements[source][i] = source

        dealt = [False] * len(self.schema_elements)
        dealt[source] = True

        finished = False
        while not finished:
            max_distance = 0
            max_order = -1
            for i in range(self.weights.shape[0]):
                if not dealt[i] and local_distance[i] > max_distance:
                    max_distance = local_distance[i]
                    max_order = i

            dealt[max_order] = True
            for i in range(self.weights.shape[0]):
                new_distance = local_distance[max_order] * self.weights[max_order][i]
                if not dealt[i] and new_distance > local_distance[i]:
                    local_distance[i] = new_distance
                    self.pre_elements[source][i] = max_order

            finished = True

            for dealt_item in dealt:
                if not dealt_item:
                    finished = False
                    break

        for i in range(len(local_distance)):
            self.shortest_distance[source][i] = local_distance[i]

    def get_join_path(self, left, right):

        edges = []
        previous = right.element_id
        current =  right.element_id

        while self.schema_elements[current].relation.element_id \
            != left.relation.element_id:
            previous = self.pre_elements[left.element_id][current]

            if self.schema_elements[current].relation.element_id != \
                self.schema_elements[previous].relation.element_id:
                edges += [Edge(self.schema_elements[current], self.schema_elements[previous])]
            current = previous
        return edges

    def distance(self, source, destination):
        return self.shortest_distance[source.element_id][destination.element_id]


    def get_neighbors(self, element, type_list):
        types = type_list.split(' ')
        neighbors = []
        i = 0
        for compare_element in self.schema_elements:
            if self.weights[element.element_id][i] > 0:
                for tmp_type in types:
                    if compare_element.type == tmp_type:
                        neighbors += [compare_element]
            i+=1

        i = 0
        for compare_element in self.schema_elements:
            if self.weights[i][element.element_id] > 0:
                for tmp_type in types:
                    if compare_element.type == tmp_type:
                        neighbors += [compare_element]
            i+=1

        return neighbors


    def get_elements_by_type(self, type_list):
        types = type_list.split(' ')
        relations = []
        for element in self.schema_elements:
            for tmp_type in types:
                if element.type == tmp_type:
                    relations += [element]

        return relations


    def search_relation(self, relation_name):
        i = 0
        result = -1
        for element in self.schema_elements:
            if (element.type == "entity" or element.type == "relationship") and \
                element.name == relation_name:
                    result = i
                    break
            i+=1

        return result


    def search_attribute(self, relation_name, attribute_name):
        i = 0
        j = 0
        result = -1
        search_default_attribute = False
        for i  in range(len(self.schema_elements)):
            element = self.schema_elements[i]
            if (element.type == 'entity' or element.type == 'relationship') and \
            element.name == relation_name:
                if attribute_name == '*':
                    search_default_attribute = True

                for j in range(i+1, len(self.schema_elements)):
                    if (not search_default_attribute and self.schema_elements[j].name == attribute_name) or\
                     (search_default_attribute and self.schema_elements[j] == element.default_attribute):
                        result = j
                        break

                if search_default_attribute and result == -1:
                    result = i


        return result

    def print_for_check(self):
        entities = self.schema_elements
        i = 0
        for entity in entities:
            if entity.type == 'entity' or entity.type == 'relationship':
                print_line = '{0}: {1}.{2}: '.format(i,entity.relation.name,entity.name)
                for attribute in entity.attributes:
                    print_line += '{0} '.format(attribute.name)
                i+=1

                print(print_line)
