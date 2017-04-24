from diabetes_engine  import *
from DB_interface import *

def test_extract_information(input_filename, output_filename):
    """
    string*string*int -> file
    Given diabetes questions in a csv, write the queries generated for first num_questions
    in the output file
    """
    
    db = get_db()
    
    
    common_diabetes_questions_as_a_string, N, questions = collect_diabetes_questions("diabetes_questions.csv")
    
    g =  open(output_filename,"w")
    
    f = open(input_filename, "r")
    questions = f.readlines()
    f.close()
    
    i = 0
    for q in questions:
        
        
    
        articles = get_articles(db)
        list_types,focus,target ,words_tags  = get_query(q,common_diabetes_questions_as_a_string,N )
        #note: N is the number of questions in the file diabetes_questions.csv, which is a context related / domain
        #specific corpus n this case
        #num_questions is the numbr of questions in the input file, roughly equal to  number of reads we have
        #to make from the file
   
        
        g.write(q+"\n")
        
        g.write("ANS TYPE:\n")
        for a_type in list_types:
            g.write(a_type+" ")
        g.write("\n")

        g.write("FOCUS:\n")
        g.write(focus)
        g.write("\n")
        
        g.write("TARGET:\n")
        g.write(target)
        g.write("\n")

        g.write("CHOSEN ANS: \n")
        g.write( extract_information(q,list_types,focus,target, common_diabetes_questions_as_a_string, N,articles) )
        g.write("\n")
        
        g.write("-------------------------------------\n")

        
        
        i = i + 1
        
    g.close()

test_extract_information("diabetes_engine_test_questions.txt", "diabetes_engine_test_results.txt")
