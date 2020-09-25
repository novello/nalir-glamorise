import os
from nltk.parse.stanford import StanfordDependencyParser as STDParser
from nltk.parse.stanford import StanfordParser as STParser
from copy import deepcopy
from data_structure.parse_tree import ParseTree
#from nltk.parse.stanford import StanfordNeuralDependencyParser

# Configure path
#os.environ['CLASSPATH'] = "/home/rafael/jars/stanford-postagger-2018-02-27/:/home/rafael/jars/stanford-parser-full-2018-02-27/:/home/rafael/jars/stanford-ner-2018-02-27/"

all_path = '/'.join(os.getcwd().split('/')[:-1] + ['jars', 'new_jars'])
#print(all_path)

os.environ['STANFORD_PARSER'] = all_path
os.environ['STANFORD_MODELS'] = all_path #"/home/rafael/jars/stanford-postagger-2018-02-27/models:/home/rafael/jars/stanford-ner-2018-02-27/classifiers"

ID_IDX = 0
WORD_IDX = 1
POSTAG_IDX = 2
PARENT_IDX = 3
PARENT_WORD = 4

class StanfordParser:

    def __init__(self,query):
        self.parse(query)
        #print('\n'.join(query.tree_table))
        self.build_tree(query)
        self.fix_conj(query)


    def parse(self,query):
        #print(query.sentence)
        #print('in parse method')
        self.depParser = STDParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
        self.parser = STParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
        
        result = self.depParser.parse_sents([query.sentence.output_words])

        self.map_words = { 'ROOT' :  [0] }
        self.map_words_index = {'ROOT': 0 }
        self.parent_index = {}

        for idx in range(len(query.sentence.output_words)):
            if self.map_words.get(query.sentence.output_words[idx], None) is None:
                self.map_words[query.sentence.output_words[idx]] = []
            self.map_words[query.sentence.output_words[idx]] += [idx + 1]
            self.map_words_index[query.sentence.output_words[idx]] = 0

        #print(self.map_words)
        self.parent_index = deepcopy(self.map_words_index)
        item = next(result)
        dep = next(item)

        self.tree = dep.tree()
        dependency_list =  list(dep.triples())
        dep_root_item = [(('ROOT', 'ROOT'),'root',dependency_list[0][0])]
        dep_dict = {}

        for item in dep_root_item + dependency_list:
            #print(item[0][0], item[2][0])
            process_items = [item[0], item[2]]

            if dep_dict.get(item[2][0], None) is None:
                dep_dict[item[2][0]] = []
            dep_dict[item[2][0]] += [item]

        tree_table = []
        #treeTable[0] = (1, )
        #for item in self.
        for idx in range(len(query.sentence.output_words)):
            real_idx = idx + 1

            word = query.sentence.output_words[idx]
            idx_dep = self.map_words_index[word]

            dependency = dep_dict[word][idx_dep]
            relation = dependency[1]
            tag = dependency[2][1]

            parent_word = dependency[0][0]
            parent_idx =  self.parent_index[word]
            parent_word_idx = self.map_words[parent_word][0] #STRONGLY ASSUMPTION

            tree_table_item = [real_idx, word.replace('_',' '), tag, parent_word_idx, parent_word, relation]
            tree_table += [tree_table_item]
            #print(tree_table_item)

            if relation.startswith('conj'):
                query.conj_table += [str(parent_word_idx)+' '+str(real_idx)]

            self.map_words_index[word] = idx_dep + 1
            self.parent_index[word] = parent_idx + 1

        query.tree_table = tree_table
        #print(query.tree_table)

    def build_tree(self,query):
        #print('in build tree method')
        query.parse_tree = ParseTree()
        done_list = [False] * len(query.tree_table)
        i = 0

        for tree_table_item in query.tree_table:
            if tree_table_item[PARENT_IDX] == 0:
                done_list[i] = True
                query.parse_tree.build_node(tree_table_item)
            i+=1

        finished = False
        while not finished:
            i = 0
            for i in range(len(query.tree_table)):
                if not done_list[i]:
                    if query.parse_tree.build_node(query.tree_table[i]):
                        #print(query.parse_tree)
                        done_list[i] = True
                        break


            finished = True
            for done_list_item in done_list:
                if not done_list_item:
                    finished = False
                    break

    def fix_conj(self, query):
        #print('in fix conj')
        if len(query.conj_table) == 0:
            return
        i = 0
        #print(query.conj_table)
        for conj_table_item in query.conj_table:
            numbers = conj_table_item.split(' ')
            gov_idx = int(numbers[0])
            dep_idx = int(numbers[1])
            gov_node = query.parse_tree.search_node_by_order(gov_idx)
            dep_node = query.parse_tree.search_node_by_order(dep_idx)
            logic = ','

            if query.parse_tree.search_node_by_order(dep_node.word_order-1) is not None:
                logic = query.parse_tree.search_node_by_order(dep_node.word_order-1).label

            if logic.lower() == 'or':
                query.conj_table[i] = query.conj_table[i]
                dep_node.left_rel = 'or'
                for j in range(len(gov_node.parent.children)):
                    if gov_node.parent.children[j].left_rel == ',':
                        gov_node.parent.children[j].left_rel = 'or'

            elif logic.lower() == 'and' or logic.lower() == 'but':
                query.conj_table[i] = query.conj_table[i]
                dep_node.left_rel = 'and'

                for j in range(len(gov_node.parent.children)):
                    if gov_node.parent.children[j] == ',':
                        gov_node.parent.children[j].left_rel = 'and'

            elif logic.lower() == ',':
                dep_node.left_rel = ','

            dep_node.parent = gov_node.parent
            gov_node.parent.children += [dep_node]
            gov_node.children.remove(dep_node)
            dep_node.relationship = gov_node.relationship
            i+=1
