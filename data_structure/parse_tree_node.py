
class ParseTreeNode:
    NODEID = 0

    def __init__(self, word_order, label, pos, relationship, parent):
        self.node_id = self.__class__.NODEID
        self.__class__.NODEID +=1
        self.word_order = word_order
        self.label = label
        self.pos = pos
        self.relationship = relationship
        self.parent = parent
        self.children = []
        self.mapped_elements = []
        self.choice = -1
        self.token_type = "NA"
        self.function = "NA"
        self.QT = ""
        self.prep = ""
        self.left_rel = ""
        self.is_added = False
        
    def get_choice_map(self):
        if self.choice >= 0 and len(self.mapped_elements) >0:
            return self.mapped_elements[self.choice]
        else:
            return None

    def sub_tree_contain(self, child):
        nodeList = [self]
        while len(nodeList) != 0:
            node = nodeList.pop(0)
            if len(node.mapped_elements) == 0 or\
             len(child.mapped_elements) == 0 or \
             node.choice <0 or child.choice <0:
                continue
            elif node.mapped_elements[node.choice].schema_element == child.mapped_elements[child.choice].schema_element:
                return True
            for node in node.children:
                nodeList.append(node)
        return False

    def toOT(self):
        if self.pos == "JJR":
            return self.label + " than"
        else:
            return self.label

    def __repr__(self):
        return '{0} - {1}'.format(self.node_id, self.label)

    def __eq__(self, other):
        if other is None or type(other) != type(self): 
            return False
        elif other.node_id == self.node_id:
            return True
        else:
            return False


    # def __eq__(self, other):
    #     if other and type(self) == type(other):
    #         return self.node_id == other.node_id
    #     return False
