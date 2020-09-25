from data_structure.parse_tree_node import ParseTreeNode
from data_structure.nl_sentence import NLSentence
from data_structure.query import Query
from rdbms.mapped_schema_element import MappedSchemaElement

#class FeedbackGenerator

def feedback_generate( history, query):
    feedback = "" 
    for  i in history:
        feedback += "#history " + i + "\n"

    if query != None:
        for i in range(len(query.sentence.output_words)):
            feedback += "#inputWord " + str(i+1) + " " + query.sentence.output_words[i] + "\n"
            
        deleted_list = query.parse_tree.deleted_nodes 
        for i in range(len(deleted_list)):
            min_node = deleted_list[i] 
            min_id = i 
            for j in range(i+1, len(deleted_list)):
                if deleted_list[j].word_order < min_node.word_order:
                    min_node = deleted_list[j]
                    min_id = j 

                temp = deleted_list[i] 
                deleted_list[i] == min_node 
                deleted_list[min_id] == temp
            for i in deleted_list:
                feedback += "#deleted " + i.word_order + " " + i.label + "\n"
            
            all_nodes = query.parse_tree.all_nodes 
            for i in range(len(all_nodes)):
                node_map = "" 
                NTVT = all_nodes[i]
                if len(NTVT.mapped_elements) > 0:
                    if NTVT.token_type == "VTNUM":
                        node_map += "#mapNum ; " 
                    else:
                        node_map += "#map ; " 
                    node_map += NTVT.label + "; " + NTVT.word_order + "; " + NTVT.choice 
                    
                    for j in range(len(NTVT.mapped_elements)):
                        if j < 5:
                            node_map += "; " 
                            mapped_element = NTVT.mapped_elements[j]
                            if mapped_element.schema_element.type == "entity" or\
                             mapped_element.schema_element.type == "relationship":
                                node_map += mapped_element.schema_element.name 
                            else:
                                node_map += mapped_element.schema_element.relation.name + "."  
                                node_map += mapped_element.schema_element.name
                        
                            if mapped_element.mapped_values.size() > 0 and j == NTVT.choice and\
                             NTVT.token_type[0:2:] == "VT" and not mapped_element.schema_element.type == "number"\
                             and not mapped_element.schema_element.type[-1] == "k":
                                node_map += "#" + mapped_element.choice 
                                for k in range(len(mapped_element.mapped_values)):
                                    if k < 5:
                                        node_map += "#" + mapped_element.mapped_values[k]
                                    else:
                                        break
                        else:
                            break
            feedback += node_map + "\n" 
            
        if not query.nl_sentences == []:
            feedback += "#general " + query.query_treeID + "\n"
        for i in query.nl_sentences:
            nl = i
            feedback += "#general " + nl.general()

        specific = query.nl_sentences[query.query_treeID].specific() 
        for i in specific:
            feedback += i
    if query != None and not query.translated_sql == []:
        title = query.translated_sql.split("\n")[0] 
        title = title[7::] 
        titles = title.split(", ") 
        cur_feedback = "#result "
        for i in titles:
            cur_feedback += "###" + i.replace("DISTINCT ", "")
        feedback += cur_feedback + "\n" 
            
        for i in range(len(query.final_result)):
            if i < 200:
                cur = "#result " 
                for j in query.final_result[i]:
                    cur += "###" + j 
                feedback += cur + "\n"
            else:
                break
        
    return feedback