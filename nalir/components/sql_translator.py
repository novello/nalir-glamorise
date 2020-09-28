from ..data_structure.parse_tree_node import ParseTreeNode
from ..data_structure.parse_tree import ParseTree
from ..data_structure.block import Block
from ..data_structure.query import Query
from ..rdbms.rdbms import RDBMS
from . import node_inserter as node_inserter



def translate(query, db):
    pre_structure_adjustor(query)
    if len(query.query_tree.all_nodes) < 2:
        return
    query.blocks = []
    block_split(query)
    query.blocks[0].node_edge_gen(query.main_block, query.query_tree, query.graph)
    query.blocks[0].translate(query.main_block, query.query_tree)
    query.translated_sql = query.blocks[0].sql


def pre_structure_adjustor(query):
    if query.query_tree.all_nodes[0] is not None and len(query.query_tree.all_nodes[0].children) > 1:
        for i in range(1,len(query.query_tree.all_nodes[0].children)):
            ot = query.query_tree.all_nodes[0].children[i]
            if len(ot.children) == 2:
                left = ot.children[0]
                right = ot.children[1]
                if right.function in ["max", "min"]:
                    if len(right.children) == 0:
                        node_inserter.add_a_sub_tree(query.query_tree, right, left)

def block_split(query):
    query_tree = query.query_tree
    node_list =[query_tree.all_nodes[0]]

    while len(node_list) > 0:
        cur_node = node_list.pop()
        new_block = None
        if cur_node.parent is not None and cur_node.parent.token_type == "CMT":
            new_block =  Block(len(query.blocks), cur_node)
            query.blocks += [new_block]

        elif cur_node.token_type == "FT" and  cur_node.function != "max":
            new_block =  Block(len(query.blocks), cur_node)
            query.blocks += [new_block]

        for i in range(len(cur_node.children) - 1, -1, -1):
            node_list += [cur_node.children[i]]

    blocks = query.blocks
    if len(blocks) == 0:
        return

    main_block = blocks[0]

    for i in  range(len(blocks)):
        cur_root = blocks[i].block_root

        while cur_root.parent is not None:
            if  cur_root.parent.token_type == "CMT":
                main_block = blocks[i]
                break
            cur_root = cur_root.parent

    query.main_block = main_block

    for i in range(len(blocks)):
        block = blocks[i]
        if block.block_root.parent.token_type == "OT":
            block.outer_block = main_block
            query.main_block.inner_blocks.append(block)

        elif block.block_root.parent.token_type == "FT":
            for j in  range(len(blocks)):
                if blocks[j].block_root == block.block_root.parent:
                    block.outer_block = blocks[j]
                    blocks[j].inner_blocks+= [block]
