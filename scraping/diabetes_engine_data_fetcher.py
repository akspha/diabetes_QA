###################################################
##MedWhat Diabetes Engine-Crawler
##Akshay Surendra Phadnis
###################################################

#-*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from bs4 import NavigableString
import urllib
from diabetes_engine  import *
import re
from math import ceil
import datetime
from DB_interface import get_db

#Fetch the metadata necessary for running the query generator
common_diabetes_questions_as_a_string, N, questions = collect_diabetes_questions("diabetes_questions.csv")

def para_directly_under_h(tag ):
    """
        BeautifulSoup Tag object -> Bool
        Given a tag, return true if it is either a p or an li tag with non empty contents
    """
    len_with_tags = len((tag).encode('utf-8'))
    len_without_tags = len((tag.get_text().encode('utf-8')))
    if len_without_tags == 0:
        tc_ratio = 5 #some number != 1
    else:
        tc_ratio = int( round( len_with_tags / float(len_without_tags) ) )

    
    return (tag.name == "p" or tag.name =="li") and tc_ratio == 1 


    
def get_data(url):
    """
    String -> None
    Given an address, URL or a path to an HTML file on disk,
    extract headings and paragraph tags under those headings
    and insert them into the MongoDB after generating focus, ans types ,etc
    """

        
    r = urllib.urlopen(url).read()
    db = get_db()
    soup = BeautifulSoup(r, "html.parser")
    
    last_focus_with_diabetes = ""
    for h in soup.find_all(re.compile("^h[1-3]")):
        #for every tag starting with h followed by 1,2 or 3
        h_text = h.get_text().replace(u'\xa0', u' ').replace(u'\0xe2', u' ').decode('latin1').encode('utf-8').lower().strip("\n").strip("?")
        if h_text == "contact us":

            continue #certain cases not being dealt with TC ratio can be eliminated using the old fashioned way
        list_types,focus,target ,words_tags  = get_query(h_text,common_diabetes_questions_as_a_string,N )
        
      
        if h.next_siblings != None:
            #look for <p> tags among  siblings and their descendents
               #skip if another h tag is encountered

            answers_under_h = u""

            
            if "diabetes" in focus:
                last_focus_with_diabetes = focus
           
                
            for sib in h.next_siblings:
               if not (isinstance(sib, NavigableString) ):
               
                   if str(sib.name).startswith('h'):
                                    break
                                
                   if para_directly_under_h(sib):
                        #<p> tags which are siblings of the h tag
                       
                        answers_under_h = answers_under_h  +  " " +  sib.get_text().replace(u'\xa0', u' ').replace(u'\0xe2', u' ').decode('latin1').encode("utf8")
                        #print answers_under_h

               

                   if sib.descendants != None:
                        for n in sib.descendants:
                            if not (isinstance(n, NavigableString) ): 
                                if str(n.name).startswith('h'):
                                    break
                                
                                if para_directly_under_h(n):
                                    #<p> tags which are descendents of siblings h tag
                                    #Note: n, may be under a sibling of h like div but, not under
                                    # under another h
                                    #Note: this doesn't say if n is directly under sib, sib can be an h tag
                                    #if it is, we don't want n here!
                                    
                                    answers_under_h = answers_under_h  +  " " + n.get_text().replace(u'\xa0', u' ').replace(u'\0xe2', u' ').decode('latin1').encode("utf8")
        
        #store answers_under_h if it is non empty or != " " pr != ""
        if  not( answers_under_h == "" or answers_under_h == " "):
            
            
            
            head_words = h_text.split(" ")
            focus_words = last_focus_with_diabetes.split(" ")
            
            #store article title as heading followed by focus
            d = {}
            article_title_words = []
            for h in head_words:
                d[h] = 1
            for f in focus_words:
                d[f] = 1

            for h in head_words:
                if d.get(h,0) > 0:
                    article_title_words.append(h)
            for h in focus_words:
                if d.get(h,0) > 0:
                    article_title_words.append(h)
                    
            article_title_string = " ".join( article_title_words  )
            
            dic = {"article_section": answers_under_h.lower(), "section_title": " ".join(list_types).encode('utf-8'), "article_title":article_title_string.encode('utf-8'), "date_scraped":datetime.datetime.today(), "url": url.encode('utf-8')}
            
            db.articles.insert(dic) #this line is commented to avoid redundant inserts!





def extract_base_url(url):
    from re import split as rsplit,search
    #extension would be  three letters followed by a slash and preceded by a dot
    #or three letters following a dot, but ending the url
    r = "(?:\.[a-z]{3}$)|(?:\.[a-z]{3}/)"#this captures the extension
    return  (rsplit( r , url)[0] +  search(r, url).group(0)).strip("/")



def mark_url(db,url):
    """
        String -> puts it into mongo db thereby marking it as seen
    """
    db.urls.insert({"link":url})

    
def crawl(url,db,link_focus = "diabetes"):
    """
    String -> dictionary with key,value in the format string,string
    Given the link to a page,
    extracts all the links pertaining to diabetes,
    the text between a tags becomes the key while the actual value of the
    href attribute becomes the value
    
    """
    
    
    base_url = extract_base_url(url)
    
    print "base_url: ", base_url
    
    r = urllib.urlopen(url).read()
    soup = BeautifulSoup(r,"html.parser")
    
    atags = soup.find_all('a')
    
   
    
    mark_url(db,url)
    print "marked.."
    print url
    print

    
    for element in atags:
       
        
        text = element.get_text().lower()
        
        link=  element.get("href","")

        if link == "":
            continue
        

                
        db_occurences = db.urls.find({"link":link}).count()
       
       
        
        
        
        if  ( link.startswith(base_url) )and   ( link_focus in text or link_focus in link) and db_occurences  == 0 :
            print "SCRAPING..."
            print link
            print
            
            
            try:    
                get_data(link)
               
                crawl(link, db)
            except:

                continue
        

    return

db = get_db()
def crawl_websites_in_file(filename):
    """
    String -> None

    Given a file with urls on each line,crawl all of them
    """
    with open(filename, "r") as f:
        urls = f.readlines()
        for url in urls:
            print url
            print 
            if not('dictionary' in url.lower()) and not (url[-3:] in ['bmp', 'png','jpg','mp3']) :
                if  url.startswith("www"):
                    for prefix in ["http://","https://"]:
                        try:
                               
                                crawl( prefix + url,db)
                        except:
                            print "some exception happened..moving on to https instead of http.."
                            continue
                           
                else:
                            crawl(url,db)
                            
               
            
#crawl_websites_in_file("scrape_links.txt")
