###############################################
## Diabetes engine
## Akshay Surendra Phadnis

##Dependencies:

##Python 2.7

##NLTK library
##PyMongo Library

##diabetes_questions.csv # a csv file bearing one diabetes related question in each row


##
##
###############################################

from re import findall
from nltk.stem.lancaster import LancasterStemmer
from nltk import pos_tag , word_tokenize
from nltk.corpus import wordnet as wn
from pprint import pprint
import csv
import sys




st = LancasterStemmer()
def generate_permutations(l):
	from itertools import permutations as perm
	t = []
	for i in perm(l):
		t.append(i)
	return t
def generate_disjunctions(x):
	s = "(?:"
	s = s + ".*)|(?:.*".join(x)
	return s + ".*)"
    
def obtain_synonyms(word):
    """
    string -> list of strings
    Takes in word and returns it's synonyms in a list
    """
    list_of_synsets = wn.synsets(word)
    synonyms = []
    for synset in list_of_synsets:
            for lemma in synset.lemmas():
                     synonyms.append(lemma.name())
    return synonyms

def re_capitalize(s):
        if s == "":
                return s
        return "["+s[0].lower() + s[0].upper() + "]" + s[1:]
                
def idf(w,N,D):
    """string*number*string -> number
        w = word whos score is sought
        N =  number of documents
        D = Document 
    """
    from math import log
    d = D.count(w)
    if d == 0:
        return 0
    return log(N/d)


def collect_diabetes_questions(filename):
    """
        string -> (string,int, list of strings)
        Open a file specified by the filename and concatenate all questions together and return
        it along a list bearing the same questions and  the number of questions encountered.
        This collection is required to run the query generator
    """
    f = open(filename,"r")
    
    reader = csv.reader(f, delimiter= "\t")
    common_diabetes_questions = ""
    N = 0 # N = number of questions
    questions = []
    for row in reader:
        
        common_diabetes_questions = common_diabetes_questions  + str( row[0])
        questions.append(str(row[0]))
        N = N + 1
        
    f.close()

    ##account for any unicode characters that may appear
    common_diabetes_questions = common_diabetes_questions.decode('utf-8')

    return (common_diabetes_questions,N, questions)

def get_query(q, common_diabetes_questions,N, generate_re_focus = True):
    """
     string*string*int -> ( list of strings,string,string, list of tuples bearing words and tags)
     Takes in a question and a large corpus regarding diabetes as another string and number of questions in the corpus
     -detects  the ans type i.e. which among, recommendation, symptoms, causes, etc is it about
     -detects the focus of the question
     -detects the target of the relation described by ans type
     
    """
    
    #A question may belong to multiple ans types, this list
    #will store all of them
    ans_types = []

    # convert any capitals to lower case and get rid of the ? symbol
    q =  q.strip("?").lower() 

    #Parts of Speech tagging
    questionWords_and_tags = pos_tag((word_tokenize((q))))
    #questionWords_and_tags is a list of tuples of the format:
    # [ (word1,tag1),
    #   (word2, tag2),
    #    (word3, tag 3),
    #   ...
    # ]

    ##locating "diabetes" in the question
    try: 
        diabetes_index = questionWords_and_tags.index(("diabetes", "NNS"))
        
    except ValueError:
        #if it is not there assume the index to be 0
            if "diabetes" in q:
                diabetes_index = q.index("diabetes")
            else:
                     diabetes_index = 0
        
    ##Identifying focus and targets
    word_index = 0
    prefix = ""
    target = ""
    suffix = ""
    for w, t in questionWords_and_tags:
       
        
        #words like no, not, nothing, will be in the target
        #to account for negation
        if "no" in w:
            target = target + w + " "
            
        ## Any adjective (tagged'JJ') appearing immediately before "diabetes" will be a constituent of prefix
        if word_index == diabetes_index - 1 and t == "JJ":
            prefix = prefix + w + " "
        if word_index == diabetes_index + 1 and t == "JJ":
            suffix = suffix + w + " "
            #print w
            
        # Any Verb  (tagged'JJ')  or a number (tagged'CD') appearing before  "diabetes" within 3 words
        ## will also be a part of prefix
        if diabetes_index > word_index and diabetes_index - word_index<= 3 and ( t == 'VBN' or   t == 'CD') and len(w) > 2:
            prefix =prefix + w + " "

        if diabetes_index < word_index and diabetes_index - word_index<= 3 and ( t == 'VBN' or   t == 'CD' or t == "VBP") and len(w) > 2:
            suffix =suffix + w + " "
            


        ## Any word other than "diabetes" , if it is a noun  (tagged'NN' or 'NNS')  or adjective  (tagged'JJ')
        ##or verb  (tagged'VB') will be a part of the target
 
        if word_index != diabetes_index and (t == 'NN' or t == 'JJ' or t == 'VB' or t == 'NNS' ):
            target = target + w + " "

        
        word_index = word_index+ 1
        
    
    ## Get rid of trailing space, if any
   
    prefix = st.stem(prefix.strip(" "))
    suffix = st.stem(suffix.strip(" "))
    
    target_words =target.split(' ')
    

    
    target = target.strip(' ')
  
    if len(suffix) <= 2:
            suffix = ""
    if len(prefix) <= 2:
            prefix = ""
    focus = prefix  + " diabetes " + suffix
    
    if generate_re_focus:
           
            if suffix == "" and prefix == "":
                   
                if target != "" and target.strip(' '):
                     st_target = ".*".join( [  st.stem(tw.strip(" "))  for tw in target_words ] )  #<---
                     target_perms = [".*".join( list(t) ).strip(".*") for t in generate_permutations([ "["+ st_target[0].lower() + st_target[0].upper() + "]" + st_target[1:],"[Dd]iabetes"]) ]
                  
                     re_focus = generate_disjunctions( ["^[Dd]iabetes$"]+ target_perms )
                     
                else:
                        re_focus = "^[Dd]iabetes$" 
            else:
                  
                     re_focus = generate_disjunctions( [".*".join( list(t) ).strip(".*") for t in generate_permutations([ re_capitalize( prefix ),"[Dd]iabetes", "(?:"+generate_disjunctions(suffix.split(" "))+")?" ])] )
            
    	
  

    
    ##pprint(questionWords_and_tags)


    ##Detecting ans type to be among:
    ## causes, symptoms, prevetion, treatment, support groups,
    #tests and recommendations

    ##for each of these types :
    ##1. obtain synonyms of the ans type
    ##2. form a regular expression which is a disjunction of all the synonyms
    ##3. Match the question against this regular expression
    ##4. If there is a match, the question pertains to this ans type i.e.
    ##   ans type is the one for which synonyms are being considered

    ##CAUSES
    syn_causes = obtain_synonyms("causes")
    syn_causes.extend ( obtain_synonyms("lead") )
    re_cause = ".+(?:cause)"
    for w in syn_causes:
        if idf(w,N,common_diabetes_questions) > 1:
            re_cause =  re_cause + "|(?:"+ st.stem( w.replace("_", " ") ) + ".+)"
    re_cause = re_cause + ".+"
    
    ##pprint(re_cause)
    ##print
    
    if findall(re_cause,q ) != []:
        ans_types.append( "causes" )
        ans_types.append( "symptoms" )


    ##SYMPTOMS    
    syn_symps = obtain_synonyms("symptom")
    syn_symps.extend ( obtain_synonyms("sign") )
    syn_symps.extend ( obtain_synonyms("effect") )
    syn_symps.extend ( obtain_synonyms("effects") )
    syn_symps.extend ( obtain_synonyms("affect") )
    re_sym = ".+(?:symptom)"
    for w in syn_symps:
        if idf(w,N,common_diabetes_questions) > 1:
            re_sym =  re_sym + "|(?:"+st.stem( w.replace("_", " ") )+".+)"
    re_sym = re_sym + ".+"
    
    ##pprint(re_sym)
    ##print
    
    if findall(re_sym,q ) != []:
        ans_types.append( "symptoms")

    ##PREVENTION
    syn_prevent = obtain_synonyms("prevent")
    syn_prevent.extend( obtain_synonyms("prevention") )
    
    re_prevent= ".+(?:prevent)"
    for w in syn_prevent:
        if idf(w,N,common_diabetes_questions) > 1:
            re_prevent =  re_prevent + "|(?:"+st.stem( w.replace("_", " ") )+".+)"
    re_prevent = re_prevent + ".+"
    
    #pprint(re_prevent)
    #print
    
    if findall(re_prevent,q ) != []:
        ans_types.append("prevention")


    ##TREATMENT
    syn_treat = obtain_synonyms("treat")
    syn_treat.extend( obtain_synonyms("cure") )
    syn_treat.extend( obtain_synonyms("control") )
    syn_treat.extend( obtain_synonyms("reduce") )
    syn_treat.extend( obtain_synonyms("care") )
    re_treat =  ".+(?:treat)"
    for w in syn_treat:
        if idf(w,N,common_diabetes_questions) > 1:
            re_treat =  re_treat + "|(?:"+st.stem( w.replace("_", " ") )+".+)"
    re_treat = re_treat + ".+"
    
##    pprint(re_treat)
##    print
    
    if findall(re_treat,q ) != []:
        ans_types.append( "treatment")

    ##SUPPORT
    syn_support = obtain_synonyms("support")
    re_support = ".+(?:support (?:group)?)"
    for w in syn_support:
        if idf(w,N,common_diabetes_questions) > 1:
            re_support =  re_support + "|(?:"+st.stem( w.replace("_", " ") )+".+)"
    re_support = re_support + ".+"
    
##    pprint(re_support)
##    print
    
    if findall(re_support,q ) != []:
        ans_types.append( "support groups")

        
    ##EXAMS AND TESTS
    re_tests_exams = ".+(?:test)"
    syn_exam = obtain_synonyms("exam")
    syn_exam.extend(obtain_synonyms("test"))
    for w in syn_exam:
        if idf(w,N,common_diabetes_questions) > 1:
            re_tests_exams =  re_tests_exams + "|(?:"+st.stem( w.replace("_", " ") )+".+)"
    re_tests_exams = re_tests_exams + ".+"
    
    #pprint(re_tests_exams)
    #print
    
    if findall(re_tests_exams,q ) != []:
        ans_types.append( "tests")

    ##RECOMMENDATIONS
    re_recommendations = ".+(?:recommend)"
    syn_rec =obtain_synonyms("recommend")
    syn_rec.extend(obtain_synonyms("suggest"))
    syn_rec.extend(obtain_synonyms("prescribe"))
    syn_rec.extend(obtain_synonyms("opinion"))
    syn_rec.append("what can")
    syn_rec.append("what should")
    syn_rec.append("what shall")
    for w in syn_rec:
        if idf(w,N,common_diabetes_questions) > 1:
            re_recommendations = re_recommendations + "|(?:"+st.stem( w.replace("_", " ") )+".+)"
    re_recommendations = re_recommendations + ".+"
    
    #pprint(re_recommendations)
    #print
    
    if findall(re_recommendations,q ) != []:
        ans_types.append( "recommendations")

    ##ALTERNATIVES
    syn_alternatives = obtain_synonyms("alternatives")
    re_alt = ".+(?:atlernative)"
    for w in syn_alternatives:
        if idf(w,N,common_diabetes_questions) > 1:
            re_alt =  re_alt + "|(?:"+ st.stem( w.replace("_", " ") ) + ".+)"
    re_alt = re_alt + ".+"
    if findall(re_alt,q ) != []:
        ans_types.append( "alternatives")

     ##REFERENCES
    syn_references = obtain_synonyms("references")
    syn_references.extend( obtain_synonyms("refer") )
    re_ref = ".+(?:references)"
    for w in syn_references:
        if idf(w,N,common_diabetes_questions) > 1:
            re_ref =  re_ref + "|(?:"+ st.stem( w.replace("_", " ") ) + ".+)"
    re_ref = re_ref + ".+"
    if findall(re_ref,q ) != []:
        ans_types.append( "references")

    ##OUTLOOK(PROGNOSIS)
    syn_outlook = obtain_synonyms("outlook")
    syn_outlook.extend(obtain_synonyms("prognosis"))
    syn_outlook.extend(obtain_synonyms("perspective"))
    
    re_out= ".+(?:outlook)"
    for w in syn_outlook:
        if idf(w,N,common_diabetes_questions) > 1:
            re_out =  re_out + "|(?:"+ st.stem( w.replace("_", " ") ) + ".+)"
    re_out = re_out + ".+"
    if findall(re_out,q ) != []:
        ans_types.append( "outlook")


    ##CONTACTING MEDICAL PROFESSIONAL
    syn_prof = obtain_synonyms("professional")
    syn_contact = obtain_synonyms("contact")
    syn_contact.extend( obtain_synonyms("call") )
    re_prof= ".*(?:contact.*medical.*professional)"
    for k in syn_contact:
        if idf(k,N,common_diabetes_questions) > 1:
            for w in syn_prof:
                if idf(w,N,common_diabetes_questions) > 1:
                    re_prof =  re_prof + "|(?:" +k+".*medical.*"+ st.stem( w.replace("_", " ")+".*" ) + ".+)"
    re_prof = re_prof + ".*"

    if findall(re_prof,q ) != []:
        ans_types =[ "when to contact a medical professional"]
        target = ""

   ##COMPLICATIONS
    syn_com = obtain_synonyms("complications")
    re_com = ".+(?:complications)"
    for w in syn_com:
        if idf(w,N,common_diabetes_questions) > 1:
            re_com =  re_com + "|(?:"+ st.stem( w.replace("_", " ") ) + ".+)"
    re_com = re_com + ".+"
    if findall(re_com,q ) != []:
        ans_types.append( "possible complications")

    #ans_types.append("intro")


    ##INTRO
    if ans_types == []:
        ans_types = ["intro"]

        
   
    if generate_re_focus:                     
            return (ans_types, focus, re_focus,target, questionWords_and_tags)
    else:
            return (ans_types, focus,target, questionWords_and_tags)


def proximity2(q, passage):
    """
    string*string -> int
    Takes in a question and a passage and returns
    a quantity indicating how close to each other do the words from the question
    appear in the passage
    """
    questionWords = q.split(" ")
    n = len(questionWords)
        
    proximity = 0
    i = 0
    while i < n-1:
            try:
                proximity = proximity + ( abs(passage.index(questionWords[i+1]) - passage.index(questionWords[i])) )
                i = i + 1
            except ValueError:
                    i = i + 1
                    continue
            
        
    if proximity  == 0:
        return 0
    
    return 1.0/proximity
    
def proximity(q, passage):
    """
    string*string -> int
    Takes in a question and a passage and returns
    a quantity indicating how close to each other do the words from the question
    appear in the passage
    """
    questionWords = q.split(" ")
    
    indices = []
    n = 0
    for w in questionWords:
        if w in passage:
            indices.append( passage.index(w))
            
        else:
            indices.append( 100000000 )
        n = n +1

        
    proximity = 0
    i = 0
    while i < n-1:
        proximity = proximity + ( abs(indices[i+1] - indices[i]) )
        i = i + 1
        
    if proximity  == 0:
        return -100000000
    
    return 1.0/proximity

def remove_tags(s):
    """ string -> string
        Return the input string after removing <p> and </p> tags from the string 
    """
    from bs4 import BeautifulSoup as bs
    return str(bs(s,"html.parser").get_text().encode('utf-8'))
    
def extract_information(q,list_types,focus,target, common_diabetes_questions_as_a_string, N, articles):
    """
    
    Given the ans types, focus and target, along with the name of the file bearing

    the dataset, retreieve the ans pertaining to the query formed by the first three arguments
    """
    max_score = -1*float('inf')
    max_overlap_target= -1*float('inf')
    best_ans = ""
    
  
    #check to see if the focus appears some where in the name of an article
    focusWords = (focus).split(" ")
    
    #collect synonyms of words in focus
    focusWords2 = []
    for w in focusWords:
        focusWords2.extend(obtain_synonyms(w))
        
    #collect word roots of words in focus
    focusWords3 = []
    for w in focusWords2:
        focusWords3.append(st.stem(w))
        
    focusWords.extend(focusWords2)
    focusWords.extend(focusWords3)


    targetWords = (target).split(" ")
    
    #collect synonyms of words in target
    targetWords2 = []
    for w in targetWords:
        targetWords2.extend(obtain_synonyms(w))
        
    #collect word roots of words in target    
    targetWords3 = []
    for w in targetWords:
        targetWords3.append(st.stem(w))

    targetWords.extend(targetWords2)
    targetWords.extend(targetWords3)

   
    
    candidate_answers = []
    
    for row_dic in articles:
            
            article_title = row_dic["article_title"].lower()
            title_words = article_title.split(' ')
            title_syns = []
            
            for w in title_words:
                if w != '-':
                    title_syns.append(w)
                    title_syns.append(st.stem(w) )
                    title_syns.extend( obtain_synonyms(w) )
                    title_syns.extend( obtain_synonyms(st.stem(w) ))
            title_syns2 = []
            for w in title_syns:
                title_syns2.append(st.stem(w))
            title_syns.extend(title_syns2)

            raw_common_words = list ( set(title_syns).intersection(set(focusWords)) )
            common_words = []
            for i in raw_common_words:
                if not i == '':
                    common_words.append(i)
                

            num_common_words_focus_title = len(common_words)
          
            #we are going to have one key to each article from the pass on data in parse_file()

            P_q_article_title = proximity2(q, article_title)
                
            #if there the article title indeed pertains to the focus
            #procure the entire row about that article, as a dictionary
            article = row_dic["article_section"]
                   
         
            #once the ans type has atleast a partial match,
            # we use the following metrics to score the candidate passage

            #number of words in common with the target
            #article = article.lower()
            article = remove_tags(article.lower().replace(u'\xa0', '').replace(u'\0xe2', u'').decode('latin1').encode("utf8")) #<----------------------------

            articleWordsSet =  set(article.split(' '))
            
              
            commons_target_articles =  list( articleWordsSet.intersection(set(targetWords)) )
              
            while '' in commons_target_articles:
                  commons_target_articles.remove('')
                  
            CTA2 = proximity(" ".join(targetWords),article )#len(commons_target_articles)


            a_types= ("".join(list_types) ).lower()
            CTA  = 0
            for w in (commons_target_articles):
                    if w in a_types:
                            continue
                    if w in target:
                            CTA = CTA + 20
                    else:
                             CTA = CTA + 1
                    
           
            #how close do the words inside the question appear in the article
            P_q_article = proximity2(q, article)
           
            ans_category =  row_dic["section_title"]
            ans_category =  ans_category.lower()
            overlap_section_title_ans_type =  len( set(ans_category.split(' ')).intersection(set(list_types)))

            list_types_candidatePassage, focus_candidatePassage,target_candidatePassage, candidatePassage_and_tags = get_query(article, common_diabetes_questions_as_a_string,N,generate_re_focus = False) #treat each candidate passage as a question
            overlap_focii = len( set(focus_candidatePassage).intersection(set(focusWords)))
            overlap_targets = len( set(target_candidatePassage).intersection(set( targetWords)))
            overlap_anstypes = len( set(list_types_candidatePassage).intersection(set(list_types)))
            #P_article_title*(CTA/100.0+1) #+ P_q_article_title*(CTA/100.0+1) #P_q_article
            score =    10*CTA + num_common_words_focus_title   +  overlap_targets + overlap_focii #  + overlap_anstypes

##            if score > max_score:
##                    max_score = score
##                    max_overlap_target = overlap_targets
##                    best_ans = article
##                    
##            elif score == max_score:
##                 if overlap_targets >= max_overlap_target:
##                         best_ans = article
##                    
            
            
           
            candidate_answers.append( (score,overlap_targets,article) )
                      
          
    #return the passage with the highest score
    if candidate_answers == []:
        return "No answer found!"
   
    return max( candidate_answers )[2]
