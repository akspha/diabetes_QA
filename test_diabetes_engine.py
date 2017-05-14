from diabetes_engine  import *
from DB_interface import *
import time
def test_extract_information(input_filename, output_filename):
    """
    string*string*int -> file
    Given diabetes questions in a csv, write the queries generated for first num_questions
    in the output file
    """
    start_time = time.time()
    db = get_db()
    
    
    common_diabetes_questions_as_a_string, N, questions = collect_diabetes_questions("diabetes_questions.csv")
    
    g =  open(output_filename,"w")
    
    f = open(input_filename, "r")
    questions = f.readlines()
    f.close()
    
    i = 0
    for q in questions:
        
        
       
        
        list_types, focus, re_focus,target, questionWords_and_tags  = get_query(q,common_diabetes_questions_as_a_string,N )
        
       
                
        re_ans_type = ""
        for at in list_types:
            first_letter = at[0]
            re_ans_type =  re_ans_type + "["+first_letter.upper()+first_letter.lower()+"]" + at[1:] + "|"
        re_ans_type =  re_ans_type.strip("|")

        
        articles = db.articles.find({ "article_title": { "$regex": re_focus}, "section_title":{"$regex":re_ans_type} })
        
        #note: N is the number of questions in the file diabetes_questions.csv, which is a context related / domain
        #specific corpus n this case
        #num_questions is the numbr of questions in the input file, roughly equal to  number of reads we have
        #to make from the file
   
        
        g.write(q+"\n")
        
        g.write("ANS TYPE:\n")
        for a_type in list_types:
            g.write(a_type+" ")
        g.write("\n")

        g.write("re_ans_type:\n")
        g.write(re_ans_type)
        g.write("\n")
        
        g.write("FOCUS:\n")
        g.write(focus)
        g.write("\n")
        
        g.write("re_focus:\n")
        g.write(re_focus)
        g.write("\n")
        
        g.write("TARGET:\n")
        g.write(target)
        g.write("\n")

        
        g.write("CHOSEN ANS: \n")
        g.write( extract_information(q,list_types,focus,target, common_diabetes_questions_as_a_string, N,articles) )
        g.write("\n")
        
        g.write("-------------------------------------\n")

        
        
        i = i + 1
        
    end_time = time.time()
    g.write(str(end_time - start_time))    
    g.close()
    

test_extract_information("diabetes_engine_test_questions5.txt", "diabetes_engine_test_results5.txt")
