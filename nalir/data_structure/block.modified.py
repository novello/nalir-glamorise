
from .parse_tree_node import ParseTreeNode
from .sql_element import SQLElement

from ..rdbms.schema_element import SchemaElement
from ..rdbms.schema_graph import SchemaGraph
from ..rdbms.edge import Edge

from ..config import get_logger
logger = get_logger(__file__)


class Block(object):
    def __init__(self, block_id, block_root):
        self.block_id = block_id
        self.block_root = block_root
        self.outer_block = None
        self.inner_blocks = []
        self.all_nodes = []
        self.edges = []
        self.select_elements = []
        self.from_elements = []
        self.conditions = []
        self.group_elements = []
        self.sql = ""

    def node_edge_gen(self, main_block, query_tree, graph):
        for i in range(len(self.inner_blocks)):
            self.inner_blocks[i].node_edge_gen(main_block, query_tree, graph)

        l = [self.block_root]

        while len(l) > 0:
            node = l.pop(0)
            self.all_nodes += [node]
            for i in node.children:
                l += [i]

        for i in range(len(self.inner_blocks)):
            for j in self.inner_blocks[i].all_nodes:
                try:
                    self.all_nodes.remove(j)
                except ValueError as e:
                    continue

        for i in range(len(self.all_nodes)):
            node = self.all_nodes[i]
            if len(node.mapped_elements) > 0:
                left = node.mapped_elements[node.choice].schema_element.relation
                contains_left = False
                for j in range(len(self.from_elements)):
                    if self.from_elements[j].element_id == left.element_id:
                        contains_left = True
                        break

                if not contains_left:
                    self.from_elements.append(left)

                right = None
                p = node.parent.parent
                if len(node.parent.mapped_elements) > 0:
                    right = node.parent.mapped_elements[node.parent.choice].schema_element.relation

                elif node.parent.token_type == "OT" and p is not None and len(p.mapped_elements) > 0:
                    right = p.mapped_elements[p.choice].schema_element.relation

                if right is not None:
                    for j in graph.get_join_path(left, right):
                        self.edges.append(j)

    def translate(self, main_block, query_tree):
        for i in range(len(self.inner_blocks)):
            self.inner_blocks[i].translate(main_block, query_tree)

        # SELECT
        if self.block_root.token_type == "NT":
            sql_element = SQLElement(self, self.block_root)
            self.select_elements.append(sql_element)

        elif self.block_root.token_type == "FT":
            if len(self.block_root.children) == 1 and self.block_root.children[0].token_type == "NT":
                sql_element = SQLElement(self, self.block_root.children[0])
                self.select_elements.append(sql_element)

            elif len(self.block_root.children) == 1 and self.block_root.children[0].token_type == "FT":
                if len(self.block_root.children[0].children) == 1 and \
                        self.block_root.children[0].children[0].token_type == "NT":
                    sql_element = SQLElement(
                        self.inner_blocks[0], self.block_root.children[0].children[0])
                    self.select_elements.append(sql_element)

        for i in range(len(self.inner_blocks)):
            if self.block_root != self.inner_blocks[i].block_root.parent:
                self.select_elements.append(
                    self.inner_blocks[i].select_elements[0])

        if self.outer_block is not None and self.outer_block == main_block:
            related_inner_node = self.find_related_node_from_self(main_block)
            if related_inner_node is not None:
                sql_element = SQLElement(self, related_inner_node)
                self.select_elements.append(sql_element)

        for i in range(len(self.all_nodes)):
            if self.all_nodes[i].QT == "each":
                sql_element = SQLElement(self, self.all_nodes[i])
                self.select_elements.append(sql_element)

        if len(query_tree.root.children) > 1 and len(query_tree.root.children[1].children) == 2 and\
                query_tree.root.children[1].children[1].function == "max":
            node = query_tree.root.children[1].children[1].children[0]
            sql_element = SQLElement(self, node)
            self.select_elements.append(sql_element)

        # FROM
        for i in range(len(self.edges)):
            left = False
            right = False
            for j in range(len(self.from_elements)):
                if self.from_elements[j].element_id == self.edges[i].left.relation.element_id:
                    left = True
                    break

            for j in range(len(self.from_elements)):
                if self.from_elements[j].element_id == self.edges[i].right.relation.element_id:
                    right = True
                    break

            if not left:
                self.from_elements.append(self.edges[i].left.relation)

            if not right:
                self.from_elements.append(self.edges[i].right.relation)

        for b in self.inner_blocks:
            self.from_elements.append(b)

        # WHERE
        if self == main_block and len(query_tree.root.children) > 1 and len(self.inner_blocks) > 0:
            for i in range(1, len(query_tree.root.children)):
                complex_condition = query_tree.root.children[i]
                right = complex_condition.children[1]
                condition = ""
                condition += self.inner_blocks[0].select_elements[0].to_string(
                    self, "")
                condition += " " + complex_condition.function + " "
                if len(self.inner_blocks) > 1:
                    condition += self.inner_blocks[1].select_elements[0].to_string(
                        self, "")

                else:
                    condition += right.label
                self.conditions.append(condition)

        for i in range(len(self.all_nodes)):
            cur_node = self.all_nodes[i]
            if not cur_node.token_type == "NT" and len(cur_node.mapped_elements) > 0:
                condition = ""
                condition += cur_node.mapped_elements[cur_node.choice].schema_element.relation.name
                condition += "." + \
                    cur_node.mapped_elements[cur_node.choice].schema_element.name
                if cur_node.parent.token_type == "OT":
                    condition += " " + cur_node.parent.function + " "

                elif cur_node.mapped_elements[cur_node.choice].choice == 0 \
                     and cur_node.token_type != "VTNUM":
                    condition += " LIKE \"%"

                else:
                    condition += " = "

                if cur_node.token_type == "VTNUM":
                    condition += cur_node.label

                else:
                    if cur_node.mapped_elements[cur_node.choice].choice == 0:
                        condition += cur_node.label + "%\""

                    else:
                        choice = cur_node.choice
                        mapped_choice = cur_node.mapped_elements[choice].choice
                        var = cur_node.mapped_elements[choice].mapped_values[mapped_choice]
                        condition += "\"" + var + "\""
                self.conditions.append(condition)

        if self == main_block:
            for i in range(len(self.inner_blocks)):
                inner_related = self.inner_blocks[i].find_related_node_from_self(
                    main_block)
                choice = -1
                if inner_related is not None and inner_related.choice != None:
                    choice = inner_related.choice
                if inner_related is not None and inner_related in self.inner_blocks[i].all_nodes:
                    left = SQLElement(main_block, inner_related)
                    right = SQLElement(self.inner_blocks[i], inner_related)
                    condition = left.to_string(main_block, "") + " = " +\
                        right.to_string(
                            main_block, inner_related.mapped_elements[choice].schema_element.name)
                    self.conditions.append(condition)

                elif inner_related is not None:
                    left = SQLElement(main_block, inner_related)
                    right = SQLElement(
                        self.inner_blocks[i].inner_blocks[0], inner_related)
                    condition = left.to_string(main_block, "") + " = " +\
                        right.to_string(
                            main_block, inner_related.mapped_elements[choice].schema_element.name)
                    self.conditions.append(condition)

        for i in range(len(self.edges)):
            self.conditions.append(str(self.edges[i]))

        # GROUP BY
        if self.outer_block is not None and self.outer_block == main_block:
            for i in range(len(self.all_nodes)):
                for j in range(len(self.outer_block.all_nodes)):
                    if self.all_nodes[i].node_id == self.outer_block.all_nodes[j].node_id:
                        element = SQLElement(self, self.all_nodes[i])
                        self.group_elements.append(element)

        for i in range(len(self.all_nodes)):
            if self.all_nodes[i].QT == "each":
                sql_element = SQLElement(self, self.all_nodes[i])
                self.group_elements.append(sql_element)
        self.sql_gen()

    def sql_gen(self):
        self.sql += "SELECT "
        if self.outer_block == None:
            self.sql += "DISTINCT "
        
        for i in range(len(self.select_elements)):
            if i != 0:
                self.sql += ", "

            if self.select_elements[i].block == self and self.select_elements[i].node.parent.token_type == "FT":
                self.sql += self.select_elements[i].node.parent.function + "("

            elif self.select_elements[i].block.outer_block is not None and\
                    self.select_elements[i].block.outer_block == self and\
                    self.select_elements[i].node.parent.parent is not None and\
                    self.select_elements[i].node.parent.parent.token_type == "FT":

                self.sql += self.select_elements[i].node.parent.parent.function + \
                    "("

            self.sql += self.select_elements[i].to_string(self, "")
            if self.select_elements[i].block == self and self.select_elements[i].node.parent.token_type == "FT":
                self.sql += ")"

            elif self.select_elements[i].block.outer_block is not None and\
                    self.select_elements[i].block.outer_block == self and\
                    self.select_elements[i].node.parent.parent is not None and\
                    self.select_elements[i].node.parent.parent.token_type == "FT":
                self.sql += ")"

            if i == 0 and self.outer_block is not None:
                self.sql += " as " + self.block_root.function

        if self.outer_block == None:
            self.sql += "\n"

        else:
            self.sql += " "

        self.sql += "FROM "
        for i in range(len(self.from_elements)):
            if i != 0:
                self.sql += ", "
                if self.from_elements[i-1].__class__ == self.__class__:
                    self.sql += "\n"

            if self.from_elements[i].__class__ == self.__class__:
                self.sql += "("
                self.sql += self.from_elements[i].sql
                self.sql += ") block_"
                self.sql += str(self.from_elements[i].block_id)

            else:
                self.sql += self.from_elements[i].name

        if len(self.conditions) > 0:
            if self.outer_block == None:
                self.sql += "\n"

            else:
                self.sql += " "

            self.sql += "WHERE "
            for i in range(len(self.conditions)):
                if i != 0:
                    self.sql += " AND "
                self.sql += self.conditions[i]
        # GLAMORISE
        # if len(self.group_elements) > 0:
        #     if self.outer_block is None:
        #         self.sql += "\n"

        #     else:
        #         self.sql += " "

        #     self.sql += "GROUP BY "
        #     for i in range(len(self.group_elements)):
        #         if i != 0:
        #             self.sql += ", "

        #         self.sql += self.group_elements[i].to_string(self, "")

    def find_related_node_from_self(self, main_block):
        outer_nt = main_block.block_root
        if main_block.block_root == "FT":
            outer_nt = main_block.block_root.children[0]

        node_list = [self.block_root]
        while len(node_list) > 0:
            inner_nt = node_list.pop(0)
            if inner_nt.token_type == "NT":
                if inner_nt.node_id == outer_nt.node_id:
                    return inner_nt

            for i in inner_nt.children:
                node_list.append(i)

        return None

    def __repr__(self):
        result = "block_" + str(self.block_id) + \
            " root: " + str(self.block_root.label)
        if self.outer_block is not None:
            result += "; outer: block_" + str(self.outer_block.block_id)

        if len(self.inner_blocks) > 0:
            result += "; inner: "

        for i in self.inner_blocks:
            result += "block_" + str(i.block_id) + " "

        return result
