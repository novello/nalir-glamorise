from ..data_structure.entity_pair import EntityPair
from ..data_structure.parse_tree_node import ParseTreeNode
from ..data_structure.query import Query
from ..rdbms.schema_element import SchemaElement

def entity_resolute(query):
    query.entities = []
    nodes = query.parse_tree.all_nodes
    for i in range(len(nodes)):
        left = nodes[i]
        if left.get_choice_map() == None:
            continue
        left_map = left.get_choice_map().schema_element
        for j in range(i+1, len(nodes)):
            right = nodes[j]
            if right.get_choice_map() == None:
                continue
            right_map = right.get_choice_map().schema_element
            if left_map == right_map:
                if left.token_type == "VTTEXT" and left.token_type == "VTTEXT":
                    if left.label == right.label:
                        entity_pair = EntityPair(left, right)
                        query.entities.append(entity_pair)
                    else:
                        continue
                if left.token_type == "VTTEXT" and right.token_type == "NT" or\
                 left.token_type == "NT" and right.token_type == "VTTEXT" or\
                 left.token_type == "NT" and right.token_type == "NT":
                    if abs(left.word_order - right.word_order) > 2:
                        continue
                    else:
                        entity_pair = EntityPair(left, right)
                        query.entities.append(entity_pair)
