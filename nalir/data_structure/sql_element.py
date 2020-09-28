from ..rdbms.schema_element import SchemaElement
from ..config import get_logger

from .parse_tree_node import ParseTreeNode

logger = get_logger(__file__)

class SQLElement(object):
    def __init__(self, block, node):
        self.block = block
        self.node = node

    def to_string(self, block=None, attribute=""):
        result = ""
        if block == self.block:
            try:
                element = self.node.mapped_elements[self.node.choice].schema_element
                result += element.relation.name + "." + element.name
            except Exception as e:
                logger.info("str format {2}:{3} {0} {1}".format(self.node.choice, self.node.mapped_elements, self.node.label, self.node.token_type))

        elif self.block.outer_block == block:
            if attribute == "":
                result += "block_" + str(self.block.block_id) + "." + self.node.parent.function
            else:
                result += "block_" + str(self.block.block_id) + "." + attribute
        else:
            if attribute == "":
                result += "block_" + str(self.block.outer_block.block_id) + "." + self.node.parent.function
            else:
                result += "block_" + str(self.block.block_id) + "." + attribute
        return result

    def __repr__(self):
        return "{0} {1}".format(self.node.label, self.node.mapped_elements)
