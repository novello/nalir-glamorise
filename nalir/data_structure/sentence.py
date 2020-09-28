
class Sentence (object):
    def __init__(self, query):
        self.word_list = []
        self.output_words = []
        self.word_dict = {}

        self.word_split(query)
        for word in self.word_list:
            word = word.replace(' ', '_')
            self.output_words.append(word)
            i = len(self.output_words)
            self.word_dict[word] = i
        
    def word_split(self, query):
        cur_word = ''
        while query[-1] == '.'or query[-1] == '\t' or query[-1] == ' ' or\
         query[-1] == '?' or query[-1] == '\n':
            query = query[:len(query) - 1]
        query += ' '
        if_cited = False
        for i in range(len(query)):
            c = query[i]
            if c == '\t' or c == '\n' or c == ' ':
                if if_cited == False:
                    idx = 0                        
                    if len(cur_word) > 0:
                        self.word_list.append(cur_word)
                    
                    cur_word = ""
                    while i< len(query) - 1 and (query[i+1] == '\t' or query[i+1] == '\n' or\
                     query[i+1] == ' ' or query[i+1] == ','):
                        i+=1
                else:
                    cur_word += query[i]
            elif c == '\'':
                if if_cited == False:
                    if query[i+1] == 't':
                        cur_word += query[i]
                    else:
                        self.word_list.append(cur_word)
                        self.word_list.append("\'s")
                        cur_word = ""
                        if i < len(query) - 1 and query[i+1] == 's':
                            i+=1
                        i+=1
                else:
                    cur_word += query[i]
            elif c == ',':
                if if_cited == False:
                    self.word_list.append(cur_word)
                    
                    
                    cur_word = ""
                    while i < len(query)-1 and (query[i+1] == '\t' or query[i+1] == '\n' or\
                     query[i+1] == ' ' or query[i+1] == ','):
                        i+=1
                else:
                    cur_word += query[i]
            elif c == '\"':
                if if_cited == False:
                    if_cited = True
                else:
                    if_cited = False
            else:
                cur_word += query[i]

    def __str__(self):
        result = ""
        for i in self.output_words:
            result += "\"" + i + "\" "
        return result + '\n'