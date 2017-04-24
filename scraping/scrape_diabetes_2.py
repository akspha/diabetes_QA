from bs4 import BeautifulSoup
from bs4 import NavigableString
#import requests
#import json
import urllib
from pprint import pprint
#from diabetes_engine  import *
import re
#common_diabetes_questions_as_a_string, N, questions = collect_diabetes_questions("diabetes_questions.csv")

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



def para_directly_under_h(tag ):
    """
        BeautifulSoup Tag object -> Bool
        Given a tag, return true if it is either a p or an li tag with non empty contents
    """

    return (tag.name == "p" or tag.name =="li")and tag.contents != "" 

def get_data(url):
    """
    String -> None
    Given an address, URL or a path to an HTML file on disk,
    extract headings and paragraph tags under those headings
    """
    try:
        
        r = urllib.urlopen(url).read()#.decode("utf-8")
        soup = BeautifulSoup(r, "html.parser")
       
        for h in soup.find_all(re.compile("^h[1-3]")):
            #for every tag starting with h followed by 1,2 or 3
            print "_____________________________________________"
            print    
            print h
            print
           
            
            if h.next_siblings != None:
                #look for <p> tags among  siblings and their descendents
                #skip if another h tag is encountered
                
                for sib in h.next_siblings:
                   
                   if str(sib.name).startswith('h'):
                                    break
                                
                   if para_directly_under_h(sib):
                        #<p> tags which are siblings of the h tag
                        print sib
                        
   
                   elif not (isinstance(sib, NavigableString) ):
  
                        if sib.descendants != None:
                            for n in sib.descendants:
                                 
                                if str(n.name).startswith('h'):
                                    break
                                
                                if para_directly_under_h(n):
                                    #<p> tags which are descendents of siblings h tag
                                    #Note: n, may be under a sibling of h like div but, not under
                                    # under another h
                                    #Note: this doesn't say if n is directly under sib, sib can be an h tag
                                    #if it is, we don't want n here!
                                    print n
                          
            print "_____________________________________________"
            print
                   

                
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

