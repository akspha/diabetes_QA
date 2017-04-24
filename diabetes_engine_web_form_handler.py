###################################################
##MedWhat Diabetes Engine Interface
##Akshay Surendra Phadnis
##April 21 2017
###################################################
from flask import Flask
from flask import request
from flask import render_template
from DB_interface import *
from diabetes_engine  import *

app = Flask(__name__)


    



@app.route('/')
def index():
    return """<!DOCTYPE html>
<html>
	<head>
		<link rel = "stylesheet" href = "interface.css">
		
	</head>
	
	<body>
		<header>
                    <STYLE type="text/css">
                          
                        header {font-family: Georgia}
                        
                        .heading{
                                text-align: center;
                                font-family: Georgia;
                                color: white ;
                                text-align:center;
                                font-size: xx-small ;
                        }

                        #second{
                        font-size: small;
                        }
                        
                        body{
                        background-color: #1E90FF;
                        color: white ;
                        font-size: xx-small ;
                        }
                        
                     </STYLE>
			 
			
		
		
		</header>
		
		<div id = "content">
                        <div class = "heading">MEDICAL ARTIFICIAL INTELLIGENCE </div>
                        

			<div class = "heading" id = "second"> Your virtual diabetes assistant</div>
			
                        <br/>

			<form method = "POST" action = ".">
				<fieldset>
					<label>Enter your question :&nbsp;</label><input type = "text" name = "question"/><br/>
					<label>Ans:&nbsp;</label><br/>
					<input class = "buttons"  type = "submit" value = "Go!"/> &nbsp;
					<input class = "buttons"  type = "reset" value = "Clear this form"/><br/>
					

					
				</fieldset>
			</form>

			

	</body>
</html>
"""


@app.route('/', methods=['POST', 'GET'])

def my_form_post():
    """
     -> String  
    Extracts the input from the text field and passes it to the diabetes engine as a question.
    The answer from diabetes engine is returned
    """
    
    #get connector to mongodb database
    db = get_db()
    #fetch all articles from 
    articles = get_articles(db)
    

    #extract the input from the form input field
    q = request.form['question']

    

    
    #obtain metadata from a list of diabetes questions
    common_diabetes_questions_as_a_string, N, questions = collect_diabetes_questions("diabetes_questions.csv")
    
    #obtain the query for the given question
    list_types,focus,target ,words_tags  = get_query(q,common_diabetes_questions_as_a_string,N )

    #from multiprocessing import Process
    #p = Process(target=extract_information, args=(q,list_types,focus,target, common_diabetes_questions_as_a_string, N,articles))
    #obtain the best answer after ranking several passages using the query returned above and other features
    ans = extract_information(q,list_types,focus,target, common_diabetes_questions_as_a_string, N,articles)
    
    
    

    return ans


if __name__ == '__main__':
    app.run()
