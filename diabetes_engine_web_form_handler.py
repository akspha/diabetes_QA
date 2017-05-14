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
app._static_folder = 'j:\\medwhat\\diabetes_engine\\static'
@app.route('/')
def index():
    return """<!DOCTYPE html>
<html>
	<head>
		
		
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
                                font-size: large ;
                        }

                        .second{
                        font-size: large;
                        }
                        
                        body{
                        background-color: #1E90FF;
                        color: white ;
                        font-size: large ;
                        text-align:center;
                        }

                        .buttons{
                          padding: 12px 12px;
                          cursor: pointer;
                          text-align: center;
                          font-size: 16px ;
            
                          
                          background-color: white;
                         
                          border-radius: 12px;

                        }
                                                
            </STYLE>
			 
	    </header>
		
		<div id = "content">
		        <img src="/static/medwhat4.bmp" align = "left"/><br/><br/><br/><br/>
                        <div class = "heading">MEDICAL ARTIFICIAL INTELLIGENCE </div>
                        <div  class = "heading"> Your virtual diabetes assistant</div>

			
			
                        <br/>

			<form method = "POST" action = "/">
				
					<label class = "second">Enter your question :&nbsp;</label>
					<input type = "text" name = "question"  width = "100000"/><br/>
					<br/>
					<input class = "buttons"  type = "submit" value = "Go!"/> &nbsp;
					<input class = "buttons"  type = "reset" value = "Clear this form"/><br/>
					

					
				
			</form>
		    </div>

			

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
    q = q.strip("?").lower()
    

    
    #obtain metadata from a list of diabetes questions
    common_diabetes_questions_as_a_string, N, questions = collect_diabetes_questions("diabetes_questions.csv")
    
    #obtain the query for the given question
    list_types, focus, re_focus,target, questionWords_and_tags  = get_query(q,common_diabetes_questions_as_a_string,N )
                  
    re_ans_type = ""
    for at in list_types:
        first_letter = at[0]
        re_ans_type =  re_ans_type + "["+first_letter.upper()+first_letter.lower()+"]" + at[1:] + "|"
    re_ans_type =  re_ans_type.strip("|")

        
    articles = db.articles.find({ "article_title": { "$regex": re_focus}, "section_title":{"$regex":re_ans_type} })
        

    #from multiprocessing import Process
    #p = Process(target=extract_information, args=(q,list_types,focus,target, common_diabetes_questions_as_a_string, N,articles))
    #obtain the best answer after ranking several passages using the query returned above and other features
    ans = extract_information(q,list_types,focus,target, common_diabetes_questions_as_a_string, N,articles)
    
    
    

    return """<!DOCTYPE html>
<html>
	<head>
		
		
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
                                font-size: large ;
                        }

                        .second{
                        font-size: large;
                        }
                        
                        body{
                        background-color: #1E90FF;
                        color: white ;
                        font-size: large ;
                        text-align:center;
                        }

                        .buttons{
                          padding: 12px 12px;
                          cursor: pointer;
                          text-align: center;
                          font-size: 16px ;
            
                          
                          background-color: white;
                         
                          border-radius: 12px;

                        }
                                                
            </STYLE>
			 
	    </header>
		
		<div id = "content"><img src="/static/medwhat4.bmp" align = "left"/><br/><br/><br/><br/>
                        <div class = "heading">MEDICAL ARTIFICIAL INTELLIGENCE </div>
                        <div  class = "heading"> Your virtual diabetes assistant</div>

			
			
                        <br/>""" + ans + """</div>

			

	</body>
</html>"""




if __name__ == '__main__':
    app.run()
