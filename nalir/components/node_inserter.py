import sys
from copy import deepcopy

from ..data_structure.parse_tree import ParseTree
from ..data_structure.parse_tree_node import ParseTreeNode
from ..data_structure.nl_sentence import NLSentence



def add_number_of(parse_tree, core, number_of):
    number_of.parent = core.parent
    number_of.children.append(core)
    #del(number_of.parent.children[number_of.parent.children.index(core)])
    #number_of.parent.children.insert(number_of.parent.children.index(core), number_of)
    idx = core.parent.children.index(core)
    number_of.parent.children[idx] = number_of
    core.parent = number_of
    parse_tree.all_nodes.append(number_of)

def add_node(parse_tree, new_parent, child):
    added = deepcopy(child)
    added.children = []
    added.parent = new_parent
    new_parent.children.append(added)
    parse_tree.all_nodes.append(added)
    return added

def add_sub_tree(parse_tree, right, left):
    right_parent = right.parent

    added = deepcopy(left)
    added.children.append(left)
    right.parent = added
    #del(right_parent.children[right_parent.children.index(right)])
    #right_parent.children.insert(right_parent.children.index(right), added)

    idx = right_parent.children.index(right)
    right_parent.children[idx] = added
    added.parent = right_parent

    added_children = added.children

    for i in range(len(added_children)):
        if added_children[i] != right and \
        len(added_children[i].mapped_elements) != 0 and \
        len(right.mapped_elements) != 0:
            choice = added_children[i].choice
            if added_children[i].mapped_elements[choice].schema_element.element_id ==\
                right.mapped_elements[right.choice].schema_element.element_id:
                del(added.children[i])
                if added.children[i] in parse_tree.all_nodes:
                    parse_tree.all_nodes.remove(added.children[i])
                else:
                    sys.exit()
                break

    added_nodes = [added]
    while len(added_nodes) != 0:
        cur = added_nodes.pop(0)
        parse_tree.all_nodes.append(cur)
        for node in cur.children:
            added_nodes.append(node)
        if cur != right:
            cur.is_added = True
    return added

def delete_node(query_tree, nl, delete_id):
    if delete_id < len(nl.all_nodes):
        dnode = nl.all_nodes[delete_id]
        del(nl.all_nodes[delete_id])
        del(nl.is_implicit[delete_id])
        del(nl.words[delete_id])
        if dnode is not None:
            query_tree.delete_node(dnode)

def add_a_sub_tree(parse_tree, new_parent, child):
    added = deepcopy(child)
    new_parent.children.append(added)
    added.parent=new_parent
    node_list = [added]
    while len(node_list) != 0:
        cur_node = node_list.pop(0)
        parse_tree.all_nodes.append(cur_node)
        for i in cur_node.children:
            node_list.append(i)
