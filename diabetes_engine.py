###############################################
## Diabetes engine
## Akshay Surendra Phadnis

##Dependencies:
##Python 2.7
##NLTK library
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

def get_query(q, common_diabetes_questions,N):
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
            
        # Any Verb  (tagged'JJ')  or a number (tagged'CD') appearing before  "diabetes" within 3 words
        ## will also be a part of prefix
        if diabetes_index > word_index and diabetes_index - word_index<= 3 and ( t == 'VBN' or   t == 'CD'):
            prefix =prefix + w + " "

        if diabetes_index < word_index and diabetes_index - word_index<= 3 and ( t == 'VBN' or   t == 'CD' or t == "VBP"):
            suffix =suffix + w + " "


        ## Any word other than "diabetes" , if it is a noun  (tagged'NN' or 'NNS')  or adjective  (tagged'JJ')
        ##or verb  (tagged'VB') will be a part of the target
 
        if word_index != diabetes_index and (t == 'NN' or t == 'JJ' or t == 'VB' or t == 'NNS' ):
            target = target + w + " "

        
        word_index = word_index+ 1
        

    ## Get rid of trailing space, if any
    target.strip(" ")
    
    focus = prefix + " diabetes "+ suffix
    ##print "Focus: ", focus
    ##print "Target: ", target
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
    re_cause = ".+(?:cause)"
    for w in syn_causes:
        if idf(w,N,common_diabetes_questions) > 1:
            re_cause =  re_cause + "|(?:"+ st.stem( w.replace("_", " ") ) + ")"
    re_cause = re_cause + ".+"
    
    ##pprint(re_cause)
    ##print
    
    if findall(re_cause,q ) != []:
        ans_types.append( "causes" )


    ##SYMPTOMS    
    syn_symps = obtain_synonyms("symptom")
    syn_symps.extend ( obtain_synonyms("sign") )
    syn_symps.extend ( obtain_synonyms("effect") )
    syn_symps.extend ( obtain_synonyms("effects") )
    syn_symps.extend ( obtain_synonyms("affect") )
    re_sym = ".+(?:symptom)"
    for w in syn_symps:
        if idf(w,N,common_diabetes_questions) > 1:
            re_sym =  re_sym + "|(?:"+st.stem( w.replace("_", " ") )+")"
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
            re_prevent =  re_prevent + "|(?:"+st.stem( w.replace("_", " ") )+")"
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
    re_treat =  ".+(?:treat)"
    for w in syn_treat:
        if idf(w,N,common_diabetes_questions) > 1:
            re_treat =  re_treat + "|(?:"+st.stem( w.replace("_", " ") )+")"
    re_treat = re_treat + ".+"
    
    #pprint(re_treat)
    ##print
    
    if findall(re_treat,q ) != []:
        ans_types.append( "treatment")

    ##SUPPORT
    syn_support = obtain_synonyms("support")
    re_support = ".+(?:support (?:group)?)"
    for w in syn_support:
        if idf(w,N,common_diabetes_questions) > 1:
            re_support =  re_support + "|(?:"+st.stem( w.replace("_", " ") )+")"
    re_support = re_support + ".+"
    
    ##pprint(re_support)
    ##print
    
    if findall(re_support,q ) != []:
        ans_types.append( "support groups")

        
    ##EXAMS AND TESTS
    re_tests_exams = ".+(?:test)"
    syn_exam = obtain_synonyms("exam")
    syn_exam.extend(obtain_synonyms("test"))
    for w in syn_exam:
        if idf(w,N,common_diabetes_questions) > 1:
            re_tests_exams =  re_tests_exams + "|(?:"+st.stem( w.replace("_", " ") )+")"
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
    for w in syn_rec:
        if idf(w,N,common_diabetes_questions) > 1:
            re_recommendations = re_recommendations + "|(?:"+st.stem( w.replace("_", " ") )+")"
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
            re_alt =  re_alt + "|(?:"+ st.stem( w.replace("_", " ") ) + ")"
    re_alt = re_alt + ".+"
    if findall(re_alt,q ) != []:
        ans_types.append( "alternatives")

     ##REFERENCES
    syn_references = obtain_synonyms("references")
    syn_references.extend( obtain_synonyms("refer") )
    re_ref = ".+(?:references)"
    for w in syn_references:
        if idf(w,N,common_diabetes_questions) > 1:
            re_ref =  re_ref + "|(?:"+ st.stem( w.replace("_", " ") ) + ")"
    re_ref = re_ref + ".+"
    if findall(re_ref,q ) != []:
        ans_types.append( "references")

    ##OUTLOOK(PROGNOSIS)
    syn_outlook = obtain_synonyms("outlook")
    syn_outlook.extend(obtain_synonyms("prognosis"))
    re_out= ".+(?:outlook)"
    for w in syn_outlook:
        if idf(w,N,common_diabetes_questions) > 1:
            re_out =  re_out + "|(?:"+ st.stem( w.replace("_", " ") ) + ")"
    re_out = re_out + ".+"
    if findall(re_out,q ) != []:
        ans_types.append( "outlook")


    ##FUCTION
    syn_fun = obtain_synonyms("function")
    re_fun= ".+(?:function)"
    for w in syn_fun:
        if idf(w,N,common_diabetes_questions) > 1:
            re_fun =  re_fun + "|(?:"+ st.stem( w.replace("_", " ") ) + ")"
    re_fun = re_fun + ".+"
    if findall(re_fun,q ) != []:
        ans_types.append( "function")

    ##CONTACTING MEDICAL PROFESSIONAL
    syn_prof = obtain_synonyms("professional")
    syn_contact = obtain_synonyms("contact")
    syn_contact.extend( obtain_synonyms("cal") )
    re_prof= ".+(?:contact.+medical.+professional)"
    for q in syn_contact:
        if idf(q,N,common_diabetes_questions) > 1:
            for w in syn_prof:
                if idf(w,N,common_diabetes_questions) > 1:
                    re_prof =  re_prof + "|(?:" +q+".+medical.+"+ st.stem( w.replace("_", " ") ) + ")"
    re_prof = re_prof + ".+"
  
    
    if findall(re_prof,q ) != []:
        ans_types.append( "when to contact a medical professional")
   
        
    ##INTRO
    if ans_types == []:
        ans_types = ["intro"]

        
   
                         
    return (ans_types, focus,target, questionWords_and_tags)




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

def remove_p_tags(s):
    """ string -> string
        Return the input string after removing <p> and </p> tags from the string 
    """
    return s.replace("<p>","").replace("</p>"," ")
    
def extract_information(q,list_types,focus,target, dataFile, common_diabetes_questions_as_a_string, N):
    """
    list_of_strings*string*string*string -> string
    Given the ans types, focus and target, along with the name of the file bearing

    the dataset, retreieve the ans pertaining to the query formed by the first three arguments
    """
    with open(dataFile, "rb") as f:
        candidate_answers = []
        candidate_rows = []
        r = csv.DictReader(f)
        for row_dic in r:
           
           
            title_words = row_dic["article_title"].split(' ')
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
            #we are going to have one key to each article from the pass on data in parse_file()

            #check to see if the focus appears some where in the name of an article
            focusWords = (focus).split(" ")

            focusWords2 = []
            for w in focusWords:
                focusWords2.extend(obtain_synonyms(w))

            focusWords3 = []
            for w in focusWords2:
                focusWords3.append(st.stem(w))
                
            focusWords.extend(focusWords2)
            focusWords.extend(focusWords3)


            targetWords = (target).split(" ")

            targetWords2 = []
            for w in targetWords:
                targetWords2.extend(obtain_synonyms(w))
                
            targetWords3 = []
            for w in targetWords:
                targetWords3.append(st.stem(w))

            targetWords.extend(targetWords2)
            targetWords.extend(targetWords3)
             
            common_words = list ( set(title_syns).intersection(set(focusWords)) )
            num_common_words = len(common_words)
            
            #focus is just one word
            if  common_words != []:
                
                #if there the article title indeed pertains to the focus
                #procure the entire row about that article, as a dictionary
                
                for ans_type in list_types:
                    #for each ans type (causes, recommendations, intro) obtained from the query
                    #check which one that is atleast (exact matches for cases like causes and causes and partial for intro and _intro_) a partial match 
                    #to the section title
                    
                    ans_category =  row_dic["section_title"]
                    ans_category =  ans_category.lower()
                    
                    if ans_type in ans_category:
                          article = row_dic["article_section"]
                       
                         
                          #once the ans type has atleast a partial match,
                          # we use the following metrics to score the candidate passage

                          #number of words in common with the target
                          #article = article.lower()
                          article = remove_p_tags(article.lower())

                          articleWordsSet =  set(article.split(' '))
                          
                          commons_target_articles =  list( articleWordsSet.intersection(set(targetWords)) )
                          
                          while '' in commons_target_articles:
                              commons_target_articles.remove('')
                              
                          CTA = len(commons_target_articles)
                          
                          #how close do the words inside the question appear in the article
                          P = proximity(q, article)

                          list_types_candidatePassage, focus_candidatePassage,target_candidatePassage, candidatePassage_and_tags = get_query(article, common_diabetes_questions_as_a_string,N) #treat each candidate passage as a question
                          #and obtain ans types,etc for the candidate passage.

                          overlap_focii = len( set(focus_candidatePassage).intersection(set(focusWords)))
                          overlap_targets = len( set(target_candidatePassage).intersection(set( targetWords)))
                          overlap_anstypes = len( set(list_types_candidatePassage).intersection(list_types))

                          score =  10*num_common_words + CTA+ P + overlap_focii  + overlap_targets+ overlap_anstypes
                          #When there is no target, CTA willbe zero and CTA*P will make the score 0, therefore, N+ P is chosen

                          candidate_answers.append( (score,1.0/P,article) )
                          
                
         #  
        #return the passage with the highest score
        if candidate_answers == []:
            return ""
        return max( candidate_answers )[2]
def test_extract_information(input_filename, output_filename, num_questions):
    """
    string*string*int -> file
    Given diabetes questions in a csv, write the queries generated for first num_questions
    in the output file
    """
    common_diabetes_questions_as_a_string, N, questions = collect_diabetes_questions(input_filename)
    g =  open(output_filename,"w")
    i = 0
    for q in questions:
        
        if i == num_questions :
            break
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
        g.write( extract_information(q,list_types,focus,target, "articles.csv",common_diabetes_questions_as_a_string,N) )
        g.write("\n")
        
        g.write("-------------------------------------\n")

        
        
        i = i + 1
        
    g.close()

while(True):
    q  = raw_input("Enter your question ?\n")
    if q == "quit":
        break
    common_diabetes_questions_as_a_string, N, questions = collect_diabetes_questions("diabetes_questions.csv")
    list_types,focus,target ,words_tags  = get_query(q,common_diabetes_questions_as_a_string,N )
    ans = extract_information(q,list_types,focus,target, "articles.csv", common_diabetes_questions_as_a_string, N)
##    print "ANS TYPE:"
##    for t in list_types:
##        print t
##    print "FOCUS:"
##    print focus
##
##    print "TARGET:"
##    print target
##
##    print "POS:\n"
##    pprint(words_tags)
##    print "CHOSEN ANS:"
    pprint(ans)
    print




#test_extract_information("diabetes_questions.csv", "diabetes_questions_answers.txt", 100)
