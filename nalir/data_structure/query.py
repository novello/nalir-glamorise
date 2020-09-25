from ..rdbms.schema_graph import SchemaGraph
from .sentence import Sentence
from .parse_tree import ParseTree
class Query(object):
    def __init__(self, query_input, graph):
        self.query_id = 0
        self.tree_table = []
        self.conj_table = []
        self.original_parse_tree = None
        self.parse_tree = None
        self.entities = []
        self.adjusting_trees = []
        self.adjusted_trees = []
        self.nl_sentence = []
        self.query_treeID = 0
        self.query_tree = ParseTree()
        self.main_block = None
        self.blocks = []
        self.translated_sql = ""
        self.final_result = []
        self.sentence = Sentence(query_input)
        self.graph = graph
