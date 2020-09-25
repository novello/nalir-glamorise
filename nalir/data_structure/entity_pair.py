from .parse_tree_node import ParseTreeNode

class EntityPair(object):
    def __init__(self, right, left):
        self.right = right
        self.left = left

    def is_entity(self, node1, node2):
        if node1 == self.left.node_id and node2 == self.right.node_id:
            return True
        elif node1 == self.right.node_id and node2 == self.left.node_id:
            return True
        else:
            return False

    def __str__(self):
        return repr(self)

    def __repr__(self):
        left = f'({self.left.node_id}){self.left.label}'
        right = f'({self.right.node_id}){self.right.label}'
        return f'EntityPair{ (left,right) }'
