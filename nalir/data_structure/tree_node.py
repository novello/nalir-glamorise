from .parse_tree_node import ParseTreeNode
from ..rdbms.schema_graph import SchemaGraph


class TreeNode (object):
    NODEID = 0

    def __init__(self, parse_tree_node=None):

        self.node_id = -1
        self.label = ""
        self.token_type = "NA"
        self.function = "NA"
        self.parent = None
        self.children = []

        self.mapped_element = None
        self.has_qt = False
        self.up_valid = True
        self.have_children = []
        self.weight = 0.98

        if parse_tree_node is not None:
            self.node_id = parse_tree_node.node_id
            self.label = parse_tree_node.label
            self.token_type = parse_tree_node.token_type
            self.function = parse_tree_node.function

            if parse_tree_node.QT != "":
                self.has_qt = True
            else:
                self.has_qt = False

            if parse_tree_node.choice >= 0 and \
                    len(parse_tree_node.mapped_elements) > parse_tree_node.choice-1 \
                    and len(parse_tree_node.mapped_elements) != 0:
                self.mapped_element = parse_tree_node.mapped_elements[
                    parse_tree_node.choice].schema_element
                #schema_element = self.mapped_element
                ##print("Element Mapped ", schema_element.relation.name, schema_element.name, "to", self.label)

    def node_evaluate(self, schema_graph, query):
        self.node_valid_test()
        self.node_weight_compute(schema_graph, query)
        # print('---------')

    def node_valid_test(self):
        if self.token_type == "ROOT":
            if self.parent is not None:
                self.up_valid = False

            for i in range(len(self.children)):
                if self.children[i].token_type != "CMT" and \
                        self.children[i].token_type != "OT":
                    self.children[i].up_valid = False
                    #print('A --> {0} Invalid children ~> {1} by ROOT -> CMT'.format(self.label, self.children[i].label))

        if self.token_type == "CMT":
            num = 0
            for i in range(len(self.children)):
                child = self.children[i]
                if (child.token_type == "FT" and child.function != "min"
                        and child.function != "max") or child.mapped_element is not None:
                    num += 1
                else:
                    #print('B --> {0} Invalid by FT/min/max/ not mapped: {1}'.format(self.label, child.label))
                    child.up_valid = False
            if num == 0:
                self.have_children += [False]
                # self.have_children.append(False)
            elif num > 1:
                for i in range(len(self.children)):
                    #print("O --> Invalidating Children of ", self.label)
                    self.children[i].up_valid = False

        elif self.token_type == "FT":
            if self.function == "max" or self.function == "min":
                if self.parent.token_type != "OT" or \
                        self.parent.function != "=":
                    #print('C--> {0} Invalid by x/in FT not followed by OT/='.format(self.label))
                    self.up_valid = False

                for i in range(len(self.children)):
                    #print('S --> invaliding children of {0} current {1}'.format(self.label, self.children[i].label))
                    self.children[i].up_valid = False
            else:
                if self.function == "sum" or self.function == "avg":
                    if self.parent.token_type != "OT" and \
                            self.parent.token_type != "CMT":
                        self.up_valid = False
                        #print('D --> {0} Invalid by s/a FT not followed by OT/='.format(self.label))
                else:
                    if self.parent.token_type == "OT" or \
                            self.parent.token_type == "CMT" or\
                            self.parent.function == "sum" or \
                            self.parent.function == "avg":
                        self.up_valid = True
                    else:
                        #print("M --> Invalidating by  operator")
                        self.up_valid = False
                if len(self.children) == 0:
                    self.have_children += [False]
                    # self.have_children.append(False)
                elif len(self.children) == 1:
                    child = self.children[0]
                    if child.mapped_element is None and \
                            child.function != "count":
                        #print('N --> Invalidating children n')
                        child.up_valid = False
                else:
                    for i in range(len(self.children)):
                        self.children[i].up_valid = False

        elif self.token_type == "NT":
            for i in range(len(self.children)):
                child = self.children[i]
                if child.token_type != "OT" and \
                        child.mapped_element is None:
                    #print('E --> None mapped element for: ', self.label, 'by', child.label)
                    child.up_valid = False

        elif self.token_type == "VTTEXT" or self.token_type == "VTNUM":
            for i in range(len(self.children)):
                #print("T -->  ", self.label, "has not chilldren")
                self.children[i].up_valid = False

            if self.parent.token_type != "NT" and  \
                    self.parent.token_type != "OT":
                #print('F --> Parent must be an NT/OT: ', self.label,  self.token_type, self.parent.label    )
                self.up_valid = False
                self.have_children += [False, False]
                # self.have_children.append(False)
                # self.have_children.append(False)

        elif self.token_type == "OT":
            if len(self.children) > 2:
                for i in range(len(self.children)):
                    #print('P --> invalidating children')
                    self.children[i].up_valid = False

            elif len(self.children) == 0:
                #self.have_children += [False]
                self.have_children += [False, False, False]
                # self.have_children.append(False)
                # self.have_children.append(False)
                # self.have_children.append(False)

            elif len(self.children) == 1:
                child = self.children[0]
                if child.token_type == "VTNUM" and \
                        child.mapped_element is not None:
                    if self.parent.token_type != "NT":
                        self.up_valid = False
                        #print('Q --> Invalide token ',self.label,' child: ', child.label )

                elif child.token_type == "VTNUM" \
                        or child.token_type == "NT" \
                        or child.token_type == "VTTEXT" \
                        or child.token_type == "FT":
                    if self.parent.token_type != "ROOT":
                        ##print(self.parent.token_type, self.parent.label)
                        self.up_valid = False
                        #print('R --> Invalidating children')

                    self.have_children += [False]
                    # self.have_children.append(False)

                else:
                    if self.parent.token_type != "ROOT" and  \
                            self.parent.token_type != "NT":
                        #print('G --> Father must be ROOT/NT', child.label, 'by', self.label)
                        self.up_valid = False
                    self.have_children += [False, False, False]
                    # self.have_children.append(False)
                    # self.have_children.append(False)
                    # self.have_children.append(False)

            elif len(self.children) == 2:
                left_right = 0
                right = 0

                for i in range(len(self.children)):
                    child = self.children[i]
                    if child.token_type == "VTNUM" or \
                            child.token_type == "VTTEXT" or \
                            child.function == "max" or \
                            child.function == "min":
                        right += 1
                    elif child.token_type == "NT" or child.token_type == "FT":
                        left_right += 1
                    else:
                        #print("H --> Must be father of max/min/vttext/nt/ft: ", child.label, 'by', self.label)
                        child.up_valid = False

                if left_right+right == 0:
                    if self.parent.token_type != "ROOT" and \
                            self.parent.token_type != "NT":
                        self.up_valid = False
                        #print('I --> Father must be ROOT/NT', child.label, 'by', self.label)
                    self.have_children += [False, False, False]
                    # self.have_children.append(False)
                    # self.have_children.append(False)
                    # self.have_children.append(False)

                elif left_right+right == 1:
                    if self.parent.token_type != "ROOT":
                        self.up_valid = False
                        #print('J --> Father must be ROOT ')
                    self.have_children += [False]
                else:
                    if right == 2:
                        self.have_children += [False]

                    if self.parent.token_type != "ROOT":
                        self.up_valid = False
                        #print('K --> Father must be ROOT: ', self.parent.label,':', self.label)

    def node_weight_compute(self, schema_graph, query):
        self.weight = 0.98
        if self.mapped_element is None:
            ##print('NOT MAPPED VALUE {0}'.format(self.label))
            return

        elif self.parent is not None and self.parent.token_type == "OT":
            if len(self.parent.children) == 1 and self.token_type == "VTNUM":
                if self.parent.parent is not None and self.parent.parent.mapped_element is not None:
                    self.weight = schema_graph.distance(
                        self.mapped_element, self.parent.parent.mapped_element)
            return

        elif self.parent is None or self.parent.mapped_element is None:
            return

        if self.mapped_element != self.parent.mapped_element:
            ##print(self.mapped_element, self.parent.mapped_element)
            self.weight = schema_graph.distance(
                self.mapped_element, self.parent.mapped_element)

        else:
            for i in range(len(query.entities)):
                if query.entities[i].is_entity(self.parent.node_id, self.node_id):
                    return
            self.weight = 0.95

    def compareTo(self, node):
        if self.node_id > node.node_id:
            return 1
        elif self.node_id < node.node_id:
            return -1
        else:
            return 0

    # def __eq__(self, other):
    #     #print('comparison')
    #     if other and type(other) == type(self):
    #         return other.node_id == self.node_id
    #     return False

    def __str__(self):
        result = ""
        result += str(self.node_id) + ". "
        result += self.label + ": "
        result += self.token_type + " "
        result += "valid: "
        result += str(self.up_valid) + "! "
        for i in self.have_children:
            result += str(i) + " "
        result += "| "
        if self.mapped_element is not None:
            result += str(self.mapped_element) + " "
        result += " weight: " + str(round(self.weight, 2))
        return result
