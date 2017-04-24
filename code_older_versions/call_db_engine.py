import cgi
from diabetes_engine import *
form = cgi.FieldStorage()
q =  form.getvalue('question')
print q
common_diabetes_questions_as_a_string, N, questions = collect_diabetes_questions("diabetes_questions.csv")
list_types,focus,target ,words_tags  = get_query(q,"",10 )
ans = extract_information(q,list_types,focus,target, "articles.csv", common_diabetes_questions_as_a_string, 10)