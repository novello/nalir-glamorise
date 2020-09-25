

class Edge:
	def __init__(self, left, right):
		self.left = left
		self.right = right


	def __str__(self):
		result = ""
		if self.left.type == "fk":
			result += '{0}.{1}'.format(self.left.relation.name, self.left.name)
		else:
			result += '{0}.{1}'.format(self.left.relation.name, self.left.relation.primary_key.name)

		result+= ' = '

		if self.right.type == "fk":
			result += '{0}.{1}'.format(self.right.relation.name, self.right.name)
		else:
			result += '{0}.{1}'.format(self.right.relation.name, self.right.relation.primary_key.name)

		return result	