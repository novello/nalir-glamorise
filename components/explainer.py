from data_structure.parse_tree import ParseTree
from data_structure.parse_tree_node import ParseTreeNode
from data_structure.nl_sentence import NLSentence
from data_structure.query import Query
import misc.similarity as sim
import components.node_inserter as node_inserter
from config import get_logger
logger = get_logger(__file__)

# class Explainer

def explain(query):
    for i in query.adjusted_trees:
        nl = explain_tree(i)
        query.nl_sentence.append(nl)

def explain_tree(tree):
    nl = NLSentence()
    if tree.all_nodes[0] is None or  tree.all_nodes[0].label != "ROOT":
        return None

    root = tree.all_nodes[0]
    if len(root.children) == 0 or  root.children[0].token_type != "CMT":
        return None

    cmt = root.children[0]
    nl.add_node(cmt, cmt.label, False)
    if len(cmt.children) == 0:
        return None

    cmt_child = cmt.children[0]
    add_the = False
    while  len(cmt_child.children) != 0 and cmt_child.token_type == "FT":
        label = ""
        if add_the == False:
            label += "the "
            add_the = True
        label += cmt_child.label
        nl.add_node(cmt_child, label, False)
        cmt_child = cmt_child.children[0]

    core_nt = cmt_child
    if  core_nt.token_type != "NT":
        return None

    add_core_nt(core_nt, add_the, nl)
    is_where = False
    for i in range(len(root.children)):
        condition = root.children[i]
        if  condition.token_type != "OT" or len(condition.children) != 2:
            continue

        if not is_where:
            nl.add_node(None, "where", False)

        left = condition.children[0]
        while left.token_type == "FT":
            label = ""
            if add_the == False:
                label += "the "
                add_the = True

            label += left.label
            nl.add_node(left, label, False)
            try:
                left = left.children[0]
            except Exception as e:
                logger.error("error by chidren zeroed")
                return

        if  left.parent.token_type != "FT" and "NT" in left.token_type and\
          left.mapped_elements[left.choice].schema_element.type != "number":
            number_of = ParseTreeNode(-1, "number of", "", "", None)
            number_of.token_type = "FT"
            number_of.function = "count"
            node_inserter.add_number_of(tree, left, number_of)
            nl.add_node(None, "the", False)
            nl.add_node(number_of, "number of", True)

        if left.token_type == "NT":
            add_core_nt(left, True, nl)

        if  not left.sub_tree_contain(core_nt):
            added = node_inserter.add_node(tree, left, core_nt)
            nl.add_node(added, "of the " + sim.lemmatize(core_nt.label), False)

        if  condition.function != "=":
            nl.add_node(condition, "is " + condition.toOT(), False)

        else:
            nl.add_node(condition, "is", False)

        right = condition.children[1]
        if "VT" in right.token_type and  right.token_type != "VTTEXT":
            add_core_nt(right, True, nl)

        elif right.parent.token_type != "FT" and  right.token_type != "FT":
            number_of = ParseTreeNode(-1, "number of", "", "", None)
            number_of.token_type = "FT"
            number_of.function = "count"
            node_inserter.add_number_of(tree, right, number_of)
            nl.add_node(number_of, "the number of", True)

        if right.token_type == "VTTEXT":
            right = node_inserter.add_sub_tree(tree, right, left)

        if right.token_type == "NT":
            add_core_nt(right, True, nl)

        if right.token_type == "FT":
            if right.function == "max":
                nl.add_node(right, "the most", False)

            elif right.function == "min":
                nl.add_node(right, "the least", False)
    return nl



def add_core_nt(core_nt, add_the, nl):
    node_list = [core_nt]
    while  len(node_list) != 0:
        core_child = node_list.pop()
        label = ""

        if core_child == core_nt:
            if not add_the:
                label += "the "

        elif core_child.token_type == "NT" and core_child.prep == "":
            core_child.prep = "of"

        elif "VT" in core_child.token_type  and core_child.prep == "":
            if  len(core_child.mapped_elements) != 0 and core_child.parent is not None and\
              len(core_child.parent.mapped_elements) != 0:

                if core_child.mapped_elements[core_child.choice].schema_element.relation.element_id !=\
                 core_child.parent.mapped_elements[core_child.choice].schema_element.relation.element_id:

                    if not nl.is_implicit[-1]:
                        core_child.prep = "of"
                    else:
                        nl.words[-1] += " of"

        if core_child.token_type == "OT" and len(core_child.children) > 0:
            label += core_child.label + " "
            core_child = core_child.children[0]

        if  len(core_child.prep) != 0:
            label += core_child.prep + " "

        if core_child.QT == "each":
            label += core_child.QT + " "

        if len(core_child.label.split(" ")) > 1:
            label += "\"" + core_child.label + "\""

        else:
            label += core_child.label
        nl.add_node(core_child, label, core_child.is_added)

        for i in range(len(core_child.children) - 1,-1, -1):
            node_list.append(core_child.children[i])
