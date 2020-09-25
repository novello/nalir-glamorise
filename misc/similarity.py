from math import sqrt
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag, word_tokenize
from gensim.models import KeyedVectors  
from datetime import datetime

global lemmatizer

lemmatizer = WordNetLemmatizer()
model = None
#class SimilarityFuctions:
def postag(word):
    l = pos_tag(word_tokenize(word))
    if len(l) == 1:
        return l[0][1]
    elif len(l) > 1:
        return 'NNP' 

def lemmatize(word):
    p = postag(word)
    if (p[0]=='J'):
         p= 'a'
    elif (p[0]=='V'):
        p= 'v'
    elif (p[0]=='N'):
        p= 'n'
    elif (p[0]=='R'):
        p= 'r'
    else:
        p= 'n'
    return lemmatizer.lemmatize(word,pos=p)

def is_numeric(e):
    try:
        a = float(e)
        return True
    except:
        return False

def similarity(tree_node, element):
    if element.similarity > 0:
        #print('dont calculate to ',tree_node.label,' and ', element.schema_element.relation.name, element.schema_element.name, element.similarity)
        return

    #print('similarity btw ', tree_node.label, element.schema_element.relation.name, element.schema_element.name)
    node_label = tree_node.label
    if is_numeric(node_label) and element.schema_element.type == 'number':
        sum = 0
        for i in range(len(element.mapped_values)):
            sum += int(float(element.mapped_values[i]))

        size = int(float(node_label)) * len(element.mapped_values)
        element.similarity = 1.0 - float(abs(sum-size)/float(size))
    else:
        sims = [0.0] * len(element.mapped_values)
        mapped_values = element.mapped_values
        
        for i in range(len(mapped_values)):
            if mapped_values[i] is None or type(mapped_values[i]) == datetime:
                continue
            #print(node_label, mapped_values[i])   
            sims[i] = pq_sim(node_label, mapped_values[i])
            #print('similarity between: ', node_label, mapped_values[i], sims[i])
            #mapped_values[i].similarity = sims[i]

        # mapped_values.sort(key=lambda elem: elem.similarity)
        # for i in range(10):
        #     print(element.mapped_values[i]    )
        #sims.sort(reverse=True)
        for i in range(len(mapped_values)):
            for j in range(i + 1, len(mapped_values)):
                if sims[j] > sims[i]:
                    temp = sims[j]
                    sims[j] = sims[i]
                    sims[i] = temp
                    temp_value = mapped_values[j]
                    mapped_values[j] = mapped_values[i]
                    mapped_values[i] = temp_value

        element.choice = 0
        element.similarity = sims[0] 

def if_schema_similar(word1,word2):
    sim =  similarity_words(word1, word2)
    if sim > 0.5:
        return True
    return False

def similarity_words(word1, word2):
    sim = word_net_sim(word1, word2)
    #print('PQ SIM: ',pq_sim(word1, word2))
    if sim < pq_sim(word1, word2):

        sim = pq_sim(word1, word2)

    sim += (pq_sim(word1, word2) / 10.0)
    return sim

def word_net_sim(word1, word2):
    #print('')
    #print('---------------->>>>')
    sim = word_net_sim_compute(word1, word2)
    set_words_1 = word1.split('_')
    set_words_2 = word2.split('_')
    #print(set_words_1, set_words_2)
    for first_word in set_words_1:
        for sec_word in set_words_2:
            #print('---------------->')
            #print(lemmatizer.lemmatize(first_word), lemmatizer.lemmatize(sec_word) )
            sim_part = word_net_sim_compute(lemmatize(first_word), lemmatize(sec_word))
            if sim_part > sim:
                sim = sim_part

    return sim


def word_net_sim_compute(word1, word2):
    sim = 0
   
    POS_map = [['n', 'n'], ['v', 'v']]

    for pos in POS_map:
        synset_word_1 = wordnet.synsets(word1, pos[0])
        synset_word_2 = wordnet.synsets(word2, pos[1])
        for sword1 in synset_word_1:
            for sword2 in synset_word_2:
                score = sword1.wup_similarity(sword2)
                if score > sim:
                    sim = score

    #print('similarity: ', sim       )
    return sim 
def load_model ():
    global model
    print('load')
    model = KeyedVectors.load_word2vec_format('../../data/GoogleNews-vectors-negative300.bin',
         binary=True)
    

def word_embedding_compute(word1, word2):
    global model
    sim = 0
    set_words_1 = word1.split('_')
    set_words_2 = word2.split('_')
    for sword1 in set_words_1:
        for sword2 in set_words_2:
            try:
                sim_tmp = modelwv.similarity(sword1, sword2)
                if sim < sim_tmp:
                    sim = sim_tmp
            except KeyError:
                print ("Error in compare {0} and {1}".format(sword1, sword2))
                continue

    #print (sim)
    return sim

            
def pq_sim(a,b):
    Q = 2
    if len(a) == 0 or len(b) == 0:
        return 0

    a = a.lower()
    b = b.lower()

    similarity = 0
    arrayA = [''] * (len(a) - Q + 1)
    for i in range(len(arrayA)):
        for j in range(Q):
            arrayA[i] += a[i+j]


    arrayB = [''] * (len(b) - Q + 1)
    for i in range(len(arrayB)):
        for j in range(Q):
            arrayB[i] += b[i+j]

    same = 0
    for i in range(len(arrayA)):
        for j in range(len(arrayB)):
            if arrayA[i] == arrayB[j]:
                same+=1
                arrayA[i] = 'a'
                arrayB[j] = 'b'
    if len(arrayA) != 0 or len(arrayB) != 0:
        similarity = 2.0 * (same * 1.0 /(len(arrayA)*1.0 + len(arrayB) * 1.0))

    return sqrt(similarity)




