from data_structure.tree_node import TreeNode
from data_structure.parse_tree_node import ParseTreeNode
from data_structure.parse_tree import ParseTree
from data_structure.query import Query
from rdbms.schema_graph import SchemaGraph


class Tree(object):
    def __init__(self, parse_tree):
        # print(parse_tree)
        self.all_nodes = []
        for node in parse_tree.all_nodes:
            self.all_nodes += [TreeNode(node)]

        self.root = self.all_nodes[0]

        for i in range(len(self.all_nodes)):
            node = self.all_nodes[i]
            parse_tree_node = parse_tree.all_nodes[i]
            parent = parse_tree_node.parent
            parent_pos = 0
            try:
                parent_pos = parse_tree.all_nodes.index(parent)
            except ValueError:
                parent_pos = -1

            if parent_pos >= 0:
                node.parent = self.all_nodes[parent_pos]
            else:
                node.parent = None

            for j in range(len(parse_tree_node.children)):
                child = parse_tree_node.children[j]
                child_pos = parse_tree.all_nodes.index(child)
                node.children.append(self.all_nodes[child_pos])

        hash(self)

        self.weight = 1.0
        self.invalid = 0
        self.cost = 0

    def tree_evaluation(self, schema_graph, query):
        for i in range(len(self.all_nodes)):
            self.all_nodes[i].have_children = []
            self.all_nodes[i].up_valid = True
            self.all_nodes[i].weight = 1.0

        self.weight = 1.0
        self.invalid = 0
        #print('zeroed invalid: ', self.invalid)
        for i in range(len(self.all_nodes)):
            self.all_nodes[i].node_evaluate(schema_graph, query)

        for i in range(len(self.all_nodes)):
            node = self.all_nodes[i]
            if not node.up_valid:
                #print('node invalid: ', node.label)
                self.invalid += 1
            for j in node.have_children:
                if not j:
                    #print('child node invalid from ', node.label)
                    self.invalid += 1
            self.weight *= node.weight

        # if self.invalid > 0:
        #     print(self)
        #print('all invalid: ', self.invalid)

    def move_sub_tree(self, new_parent, node):
        self.invalid = 0
        if new_parent == node:
            return False

        elif new_parent == node.parent:
            return False

        is_parent = False
        temp = new_parent
        while temp is not None:
            if temp.parent is not None and temp == node:
                #print (node.label, 'is parent of', new_parent.label)
                is_parent = True
                break
            temp = temp.parent
            # print(temp)

        if is_parent == False:
            old_parent = node.parent
            old_parent.children.remove(node)
            new_parent.children.append(node)
            node.parent = new_parent
            return True

        elif new_parent.parent == node and len(new_parent.children) == 0 and (new_parent.token_type == "OT" or
                                                                              new_parent.token_type == "FT"):
            #print (node.label, [x.label for x in node.children], new_parent.label)
            # getting parrent from current node
            node_parent = node.parent
            # setting new_parent to child of previous parent
            node_parent.children.append(new_parent)
            # remove new_parent of its oldests parent list
            # = node.children.remove(new_parent)
            new_parent.parent.children.remove(new_parent)
            # setting parent of new_parent
            new_parent.parent = node_parent
            # removing node from previous children parent list
            node_parent.children.remove(node)
            # setting new parent to node
            node.parent = new_parent
            #print ('node_parent: ', node_parent.label, 'current_node: ', node.label, 'chidren: ',[x.label for x in node.children], 'child: ', new_parent.label)
            # remove from current child list
            # node.children.remove(new_parent) already execute it on new_parent.parent.remove(node)
            # setting to new_parent list
            new_parent.children.append(node)
            return True
        else:
            return False

    def append_equal(self):
        node = TreeNode(None)
        node.label = "equals"
        node.node_id = 9999
        node.token_type = "OT"
        node.function = "="
        node.parent = self.all_nodes[0]
        self.all_nodes[0].children.append(node)
        self.all_nodes.append(node)

    def search_node_by_id(self, ID):
        for i in self.all_nodes:
            if i.node_id == ID:
                return i
        return None

    def __hash__(self):
        stack = []
        stack += [self.root, self.root]
        l = []

        while len(stack) != 0:
            r = stack.pop(len(stack) - 1)
            if r.label not in l:
                for idx in range(len(r.children)):
                    stack.append(r.children[idx])
                    stack.append(r.children[idx])

            l += [r.node_id]

        h = 1
        for i in l:
            h = 31*h + hash(i)
        #print(l, hash(frozenset(l)), h%10000000)
        self.hash_num = h % 100000
        # return h%10000000
        return self.hash_num
        # return h%10000000

    def compare_to(self, tree):
        if self.weight*100-self.cost > tree.weight*100-tree.cost:
            return -1
        elif tree.weight*100-tree.cost > self.weight*100-self.cost:
            return 1
        return 0

    def __repr__(self):
        result = ""
        result += "HashNum: " + str(self.hash_num) + " invalid: " + str(self.invalid) + \
            " weight: " + str(round(self.weight, 2)) + \
            " cost: " + str(self.cost) + "\n"
        node_list = [self.root]
        level_list = [0]
        while node_list != []:
            cur_node = node_list.pop(len(node_list) - 1)
            cur_level = level_list.pop(len(level_list) - 1)
            result += str((cur_level * 4) * " ")
            # for i in range(cur_level):
            #     result += 4 * " "
            result += "(" + str(cur_node.node_id) + ")"
            # ':' + cur_node.token_type+ ' p:' +  str(cur_node.parent) + "\n"
            result += cur_node.label + '\n'
            for i in range(len(cur_node.children)):
                node_list.append(cur_node.children[len(cur_node.children)-i-1])
                level_list.append(cur_level+1)
        return result

    def print_for_check(self):
        result = ""
        print(self)
        result += str(self) + "\n"
        print("All Nodes: ")
        result += "All Nodes: \n"
        for i in self.all_nodes:
            result += str(i)
            print(i)
        return result
