from copy import deepcopy
import sys

from ..data_structure.tree import Tree
from ..data_structure.parse_tree_node import ParseTreeNode
from ..config import ConfigHandler
from ..config import get_logger

logger = get_logger(__file__)
config = ConfigHandler()

class TreeStructureAdjustor:


	@staticmethod
	def tree_structure_adjust(query,  db):
		query.adjusting_trees = []
		query.invalid = []
		pre_trees = {}
		##print('Running Adjust')
		TreeStructureAdjustor.adjust(query, db,False, pre_trees)
		if len(query.adjusting_trees) == 0 or (len(query.adjusting_trees) > 0 and query.adjusting_trees[0].cost > 3):
			max_min = False
			#for i in range(len(query.parse_tree.all_nodes)):
			for node in query.parse_tree.all_nodes:
				##print("node: ", node.label, node.token_type, node.function)
				if node.function == 'max' or node.function == 'min':
					max_min = True
					break

			if max_min:
				##print('Running again')
				TreeStructureAdjustor.adjust(query, db, True, pre_trees)

		adjusted_trees = query.adjusting_trees
		##print(adjusted_trees)
		adjusted_trees.sort(key=lambda elem : ((elem.weight * 100) - elem.cost) * -1 )
		#print(adjusted_trees)
		##print(query.invalid)
		for i  in range(len(adjusted_trees)):
			adjusted_tree = adjusted_trees[i]

			for j in range(len(adjusted_tree.all_nodes)):
				node = adjusted_trees[i].all_nodes[j]
				node.children.sort(key=lambda elem: elem.node_id)
			hash(adjusted_tree)


		linked_list = []
		i = 0
		while i  < len(adjusted_trees):
			if adjusted_trees[i].hash_num in linked_list:
				# TODO: remove item
				adjusted_trees.pop(i)
				i-=1
			else:
				linked_list += [adjusted_trees[i].hash_num]
			i+=1

		TreeStructureAdjustor.build_adjusted_trees(query)

	@staticmethod
	def adjust(query, db,add_equal, pre_trees):
		parse_tree = query.parse_tree
		adjusted_trees = query.adjusting_trees
		query.nl_sentences = []

		tree = Tree(parse_tree)


		TreeStructureAdjustor.pre_adjust(tree)

		##print(tree)
		if add_equal:
			tree.append_equal()

		##print('evaluating Tree')
		##print('---------------------------------')
		tree.tree_evaluation(db.schema_graph, query)
		##print('---------------------------------')
		#print(tree)
		#sys.exit()
		if tree.invalid == 0:
			##print('not invalid: ', tree)
			adjusted_trees.append(tree)
			##print ('tree is invalid')
		# else:
		# 	#print('invalid: ', tree)
		queue = [tree]

		pre_trees[tree.hash_num] = tree.cost
		##print('tree cost: ', tree.cost)
		while len(queue) != 0 and len(queue) < 100:
			##print('poping and extent')
			cur_tree = queue.pop(0)
			ext_trees = TreeStructureAdjustor.extend(cur_tree, db.schema_graph,query)

			##print('iterate over ext_trees')
			for add_tree in ext_trees:
				##print(add_tree)
				if add_tree.hash_num in pre_trees:
					if pre_trees[add_tree.hash_num] > add_tree.cost:
						#pre_trees.remove(pre_trees[add_tree.hash_num])
						pre_trees[tree.hash_num] = add_tree.cost
				else:
					queue += [add_tree]
					pre_trees[add_tree.hash_num] = add_tree.cost
					if add_tree.invalid == 0:
						##print('tree to add', add_tree)
						adjusted_trees += [add_tree]
					else:
						query.invalid += [add_tree]
						##print('adding equal', add_tree)

		#print(adjusted_trees)
		query.adjusted_trees = 	adjusted_trees




	@staticmethod
	def pre_adjust(tree):
		for i in range(len(tree.all_nodes)):
			tree_node = tree.all_nodes[i]
			if tree_node.function == 'avg' or tree_node.function == 'sum':
				if len(tree_node.children) == 0:
					tree.move_sub_tree(tree_node, tree_node.parent)
			elif  tree_node.token_type == 'OT' and len(tree_node.children) == 0:
				tree.move_sub_tree(tree_node, tree_node.parent)





	@staticmethod
	def extend(tree, schema_graph, query):

		extended_trees = []
		if tree.cost > 4:
			return extended_trees
		##print('extent node')
		for i in range(1,len(tree.all_nodes)):
			##print('extent node:',i)
			tree_node = tree.all_nodes[i]
			extended_trees += TreeStructureAdjustor.extend_node(tree, tree_node, schema_graph, query)

		for i in range(len(extended_trees)):
			new_tree = extended_trees[i]
			hash(new_tree)

		return extended_trees


	@staticmethod
	def extend_node(tree, node, schema_graph, query):
		extended_trees = []
		for i in range(len(tree.all_nodes)):
			new_tree = deepcopy(tree)
			new_tree.cost+=1
			new_node = new_tree.all_nodes[i]
			if new_node.node_id != node.node_id:
				#print(node.label, ' ==? moved ', new_node.label,)
				if_Added = new_tree.move_sub_tree(new_node, new_tree.search_node_by_id(node.node_id))
				if if_Added:
					#print("chosed")
					##print(new_tree)
					##print('---------------------------------')
					new_tree.tree_evaluation(schema_graph, query)
					#print(new_tree)
					#sys.exit()
					##print('--------------------------------')
					if new_tree.invalid < tree.invalid or (new_tree.invalid == tree.invalid and \
						new_tree.weight * 10000 - new_tree.cost > tree.weight*10000 - tree.cost):
						extended_trees += [new_tree]
						#print('----')
						#print(new_tree)
						#print('----')

				#else:
					#print("not chosed")

		##print(extended_trees)
		return extended_trees


	@staticmethod
	def build_adjusted_trees(query):
		adjusting_trees = query.adjusting_trees
		query.adjusted_trees = []
		adjusted_trees =  query.adjusted_trees


		i = 0
		##print(query.adjusted_trees)
		while i < len(adjusting_trees) and i < 5:
			##print (adjusting_trees[i])
			adjusting_tree = adjusting_trees[i]
			adjusted_tree = deepcopy(query.parse_tree)

			for j in range(len(adjusting_tree.all_nodes)):
				lack_node = adjusting_tree.all_nodes[j]

				if adjusted_tree.search_node_by_id(lack_node.node_id) is None:
					new_node = ParseTreeNode(lack_node.node_id, lack_node.label, '','', None)
					new_node.token_type = lack_node.token_type
					new_node.node_id = lack_node.node_id
					new_node.function = lack_node.function
					adjusted_tree.all_nodes += [new_node]
					#print('adding node ', new_node)



			for j in range(len(adjusted_tree.all_nodes)):
				adjusted_tree.all_nodes[j].children = []

			for j in range(len(adjusting_tree.all_nodes)):
				cur_node = adjusting_tree.all_nodes[j]
				cur_parse_node = adjusted_tree.search_node_by_id(cur_node.node_id)

				if cur_node.label != 'ROOT':
					cur_parse_node.parent = adjusted_tree.search_node_by_id(cur_node.parent.node_id)

				for k in range(len(cur_node.children)):
					cur_parse_node.children += [adjusted_tree.search_node_by_id(cur_node.children[k].node_id)]


			adjusted_trees += [adjusted_tree]
			i+=1
		query.adjusted_trees = 	adjusted_trees
		#logger.info(query.adjusted_trees)
		if len(query.adjusted_trees) > 0:

			query.query_treeID = 0
			query.query_tree = adjusted_trees[query.query_treeID]
			##print(adjusted_tree[query.query_treeID])

		for i in range(len(query.query_tree.all_nodes)):
			ot_parse_tree_node =  query.query_tree.all_nodes[i]
			if ot_parse_tree_node.token_type == 'OT' and len(ot_parse_tree_node.children) == 2:
				left = ot_parse_tree_node.children[0]
				right = ot_parse_tree_node.children[1]

				if left.token_type == 'VTNUM':
					ot_parse_tree_node.children[1] = left
					ot_parse_tree_node.children[0] = right
