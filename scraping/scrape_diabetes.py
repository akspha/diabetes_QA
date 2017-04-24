from bs4 import BeautifulSoup
from bs4 import NavigableString
import requests
import json
import urllib
from pprint import pprint
from diabetes_engine  import *
import re
common_diabetes_questions_as_a_string, N, questions = collect_diabetes_questions("diabetes_questions.csv")

def get_links(url,link_focus = "diabetes"):
    """
    String -> dictionary with key,value in the format string,string
    Given the link to a page,
    extracts all the links pertaining to diabetes,
    the text between a tags becomes the key while the actual value of the
    href attribute becomes the value
    """
    article= {}
    r = urllib.urlopen(url).read()
    soup = BeautifulSoup(r,"html.parser")
    atags = soup.find_all('a')
    for element in atags:
        text = element.get_text().lower()
        if  link_focus in text :
            #synonyms of words in focus can also be used
            #if this focus is say gestational diabetes, we would want to
            #extract links about diabetes and pregnancy (both appearing in the same link)
            article[text] = element["href"]
            
    return article
#article = get_links("https://www.niddk.nih.gov/health-information/diabetes")

def get_data1(article_url = "https://www.niddk.nih.gov/health-information/diabetes/overview/symptoms-causes"):
    """
    The article (an article page) is assumed to be a page with textual content, i.e. enough p tags,
    not an index page like a telephone directory with web links to various other pages
    dic with key,value format string,string -> 
    """
    article = urllib.urlopen(article_url).read()
    soup = BeautifulSoup(article,"html.parser")
    ptags = soup.find_all('h2') #p => parent
    for ptag in ptags:
        text = ptag.get_text().lower()
        print text
        
        list_types,focus,target ,words_tags  = get_query(text,common_diabetes_questions_as_a_string,N )
        print list_types #section title
        print focus #article title
        print target
        print ptag.next_sibling.next_sibling #article
        


#get_data1()

def get_data2(article_url = "https://www.niddk.nih.gov/health-information/diabetes/overview/risk-factors-type-2-diabetes"):
    """
    The article (an article page) is assumed to be a page with textual content, i.e. enough p tags,
    not an index page like a telephone directory with web links to various other pages
    dic with key,value format string,string -> 
    """
    article = urllib.urlopen(article_url).read()
    soup = BeautifulSoup(article,"html.parser")
    for ptag in soup.find_all("p"):
        print ptag.get_text()
   
    print 
        
##        list_types,focus,target ,words_tags  = get_query(text,common_diabetes_questions_as_a_string,N )
##        print list_types #section title
##        print focus #article title
##        print target
##        print ptag.next_sibling.next_sibling #article
        
###get_data2()
##def para_directly_under_h(tag,h_num ):
##    print "**********************************"
##    #if there has been an h with a number higher than or equal to h_num, the return value should be False
##    print tag
##    for t in tag.previous_siblings :
##        print t
##    previous_heads = [int(str(t.name).strip('h') ) >= h_num for t in tag.previous_siblings if str(t.name).startswith('h')]
##    #print previous_heads'
##    print (tag.name == "p" or tag.name =="li")and tag.contents != "" and (any(previous_heads))
##    print "**********************************"
##    return (tag.name == "p" or tag.name =="li")and tag.contents != "" and (any(previous_heads))

def para_directly_under_h(tag,h_num ):
##    print "**********************************"
    #if there has been an h with a number higher than or equal to h_num, the return value should be False
##    print tag
##    for t in tag.previous_siblings :
##        print t
##    previous_heads = [int(str(t.name).strip('h') ) >= h_num for t in tag.previous_siblings if str(t.name).startswith('h')]
##    #print previous_heads'
##    print (tag.name == "p" or tag.name =="li")and tag.contents != "" and (any(previous_heads))
##    print "**********************************"
    return (tag.name == "p" or tag.name =="li")and tag.contents != "" #and (any(previous_heads))

def get_data(url):
    try:
        
        r = urllib.urlopen(url).read()#.decode("utf-8")
        soup = BeautifulSoup(r, "html.parser")
       
        for h in soup.find_all(re.compile("^h[1-3]")):
            
            print "_____________________________________________"
            print    
            print h
            print
           
            h_num  = int( str(h.name).strip('h'))
            if h.next_siblings != None:
                #look for <p> tags among  siblings and their descendents
                for sib in h.next_siblings:
                   
                   
                    
                    if str(sib.name).startswith('h'):
                                    break
                                
                    if para_directly_under_h(sib, h_num):
                        
                        print sib
                        
    ##                    print "PARAGAPH!"
                        
                    elif not (isinstance(sib, NavigableString) ):
    ##                    print "looking for descendents of sib : ", sib
    ##                    print "==============================================="
                        if sib.descendants != None:
    ##                        print "descendents  != None"
                            for n in sib.descendants:
                                
                                if str(n.name).startswith('h'):
                                    break
                                
    ##                            print "desc: ", n
                                if para_directly_under_h(n, h_num):
                                    #Note: n, may be under a sibling of h like div but, not under
                                    # under another h
                                    #Note: this doesn't say if n is directly under sib, sib can be an h tag
                                    #if it is, we don't want n here!
                                    print n
    ##                                print "PARAGAPH!"
    ##                else:
    ##                    print "sib: ", sib.get_text()
            print "_____________________________________________"
            print
                   
            #look for <p> tags among  children
    ##        if  h.descendents != None:
    ##            
    ##            for c in h.descendents:
    ##                
    ##                if para_directly_under_h(c, h_num):
    ##                    #print "DESC:"
    ##                    print c
                
    except IOError:
        print "URL not found, please try again with the correct URL"
    
#get_data("https://www.niddk.nih.gov/health-information/diabetes/overview/risk-factors-type-2-diabetes")#..ok
#get_data("https://www.niddk.nih.gov/health-information/diabetes/overview/preventing-type-2-diabetes") # ..ok


#get_data("https://www.niddk.nih.gov/health-information/diabetes/overview/tests-diagnosis")#..ok
#get_data(" ")#..ok

#Testing
#get_data("test1.html")#..ok
#get_data("test2.html")#..ok
#get_data("test3.html")#..ok
#get_data("test4.html") #..ok
#get_data("test5.html") #..ok
print "------------------------------------------------------------------------------------------"

