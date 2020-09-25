class NLSentence(object):
    def __init__(self, node=None, word="", is_implicit=None):
        if node is not None:
            self.all_nodes = [node]
            self.words = [word]
            self.is_implicit = [is_implicit]
        else:
            self.all_nodes = []
            self.words = []
            self.is_implicit = []

    def add_node(self, node, word, is_implicit):
        self.all_nodes += [node]
        self.words += [word]
        self.is_implicit += [is_implicit]
    
    def general(self):
        result = ""
        for i in range(len(self.words)):
            if self.is_implicit[i]:
                continue
            else:
                result += self.words[i]
            if i < len(self.words)-1:
                result += " "
            else:
                result += ". "
        return result + '\n'
    
    def specific(self):
        results = []
        result = ''
        for i in range(len(self.words)):
            if self.is_implicit[i]:
                result += '#implicit '+self.words[i]
            else:
                result += "#explicit " + self.words[i]
            if i != len(self.words)-1:
                result += ' '
            else:
                result += ". "
            results.append(result + "\n")
            result = ''
        return results
    
    def __str__(self):
        result = ''
        for i in range(len(self.words)):
            if self.is_implicit[i]:
                result += "[" + self.words[i] + "]"
            else:
                result += self.words[i]
            if i != len(self.words)-1:
                result += ' '
            else:
                result += ". "
        return result + '\n'
    