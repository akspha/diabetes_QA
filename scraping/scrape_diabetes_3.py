#-*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from bs4 import NavigableString
import urllib
from pprint import pprint
from diabetes_engine  import *
import re
from math import ceil
import datetime
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
##    print tag.name
##    print len_with_tags
##    print len_without_tags
##    print
    
    return (tag.name == "p" or tag.name =="li") and tc_ratio == 1 


    
def get_data(url):
    """
    String -> None
    Given an address, URL or a path to an HTML file on disk,
    extract headings and paragraph tags under those headings
    and insert them into the MongoDB after generating focus, ans types ,etc
    """
##    try:
        
    r = urllib.urlopen(url).read()#.decode("utf-8")
    db = get_db()
    soup = BeautifulSoup(r, "html.parser")
    
    last_focus_with_diabetes = ""
    for h in soup.find_all(re.compile("^h[1-3]")):
        #for every tag starting with h followed by 1,2 or 3
        h_text = h.get_text().encode('utf-8').lower().strip("\n").strip("?")
        if h_text == "contact us":

            continue #certain cases not being dealt with TC ratio can be eliminated using the old fashioned way
        list_types,focus,target ,words_tags  = get_query(h_text,common_diabetes_questions_as_a_string,N )
        
        #" ".join(list_types)
      
        if h.next_siblings != None:
            #look for <p> tags among  siblings and their descendents
##                #skip if another h tag is encountered
##                print "_____________________________________________"
##                print    
##                print h
##                print
##                print "type: ", list_types
            
            answers_under_h = ""

            
            if "diabetes" in focus:
                last_focus_with_diabetes = focus
                #print "focus:", focus
            #else:
                #print "focus:", last_focus_with_diabetes
                
            for sib in h.next_siblings:
               if not (isinstance(sib, NavigableString) ):
               
                   if str(sib.name).startswith('h'):
                                    break
                                
                   if para_directly_under_h(sib):
                        #<p> tags which are siblings of the h tag
                       
                        answers_under_h = answers_under_h  +  " " +  sib.get_text().replace(u'\xa0', u' ').decode('latin1').encode("utf-8")
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
                                    
                                    #print n
                                    answers_under_h = answers_under_h  +  " " + n.get_text().replace(u'\xa0', u' ').decode('latin1').encode("utf-8")
        
        #store answers_under_h if it is non empty or != " " pr != ""
        if  not( answers_under_h == "" or answers_under_h == " "):
            #print "STORING...."
            #if not( last_focus_with_diabetes in h_text):
            
            
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
            #print "DIC: -"
            #pprint (dic)
            db.articles.insert(dic) #this line is commented to avoid redundant inserts!

                #store article title as focus followed by heading
##                d = {}
##                article_title_words = []
##                for h in head_words:
##                    d[h] = 1
##                for f in focus_words:
##                    d[f] = 1
##
##                for h in focus_words:
##                    if d.get(h,0) > 0:
##                        article_title_words.append(h)
##                for h in head_words:
##                    if d.get(h,0) > 0:
##                        article_title_words.append(h)
##                        
##                article_title_string = " ".join( article_title_words  )
##                
##                dic = {"article_section": answers_under_h.lower(), "section_title": " ".join(list_types).encode('utf-8'), "article_title":article_title_string.encode('utf-8'), "date_scraped":datetime.datetime.today(), "url": url.encode('utf-8')}
##                print "DIC: -"
##                pprint (dic)
##                db.articles.insert(dic) #this line is commented to avoid redundant inserts!
##            print "_____________________________________________"
##            print
                   

                

##    except IOError:
##        print "URL not found, please try again with the correct URL"
##        pass
##    
##    except UnicodeEncodeError:
##        pass
##    
##    except UnicodeDecodeError:
##        pass
##    except:
##        pass


#get_data("https://www.niddk.nih.gov/health-information/diabetes/overview/preventing-problems/heart-disease-stroke")

def extract_base_url(url):
    from re import split as rsplit,search
    #extension would be  three letters followed by a slash and preceded by a dot
    #or three letters following a dot, but ending the url
    r = "(?:\.[a-z]{3}$)|(?:\.[a-z]{3}/)"#this captures the extension
    return  (rsplit( r , url)[0] +  search(r, url).group(0)).strip("/")


##print extract_base_url("www.aspkfkffk.com/kddk") #..ok
##print extract_base_url("https://www.niddk.nih.gov/health-information/diabetes")#..ok
##print extract_base_url("https://www.niddk.nih.gov")#..ok
##print extract_base_url("https://docs.python.org/2.0/lib/match-objects.html")#..ok
##print extract_base_url("https://trello.com/b/F02Uq6II/diabetes-qa")#..ok
##print extract_base_url("http://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/breast-cancer-wisconsin.data")#..ok

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
    
    
    r = urllib.urlopen(url).read()
    soup = BeautifulSoup(r,"html.parser")
    
    atags = soup.find_all('a')
    
   
    
    mark_url(db,url)
    
##    sum_db_occurences = 0
##    
##    num_atags = 0
    
    for element in atags:
       
        
        text = element.get_text().lower()
        
        link=  element.get("href","")

        if link == "":
            continue
        
        
##        if link.startswith("/"):
##                link =  base_url + link
                
        db_occurences = db.urls.find({"link":link}).count()
       
        #num_atags = num_atags  + 1
        
        
        
                
        if ( link.startswith(base_url) )and ( link_focus in text or link_focus in link) and db_occurences  == 0 :
            print "SCRAPING..."
            print link
            print
            
            
            try:    
                get_data(link)
                #print "MARK!"
                #mark_url(db,link)
                #print "RECURSE"
                crawl(link, db)
            except:

                continue
##        elif db_occurences != 0:
##             sum_db_occurences =  sum_db_occurences + 1
                
        
##    if sum_db_occurences  == num_atags
##        #base condition for the recursion
##        print "BASE condition HIT"
##        return

    return
db = get_db()
#crawl("https://www.niddk.nih.gov/health-information/diabetes",db)
def crawl_websites_in_file(filename):
    """
    String -> None

    Given a file with urls on each line,crawl all of them
    """
    with open(filename, "r") as f:
        urls = f.readlines()
        for url in urls:
            if  url.startswith("www"):
                for prefix in ["http://","https://"]:
                    try:
                    
                            crawl( prefix + url,db)
                    except:
                        continue
                       
            else:
                        crawl(url,db)
               
            
crawl_websites_in_file("scrape_links.txt")

#article = crawl("https://www.niddk.nih.gov/health-information/diabetes")
#print "Crawling complete!"

#article = crawl("http://www.childrenwithdiabetes.com")
#print "Crawling complete!"
#crawl("https://www.niddk.nih.gov/health-information/diabetes/overview/preventing-problems/heart-disease-stroke")





    
#get_data("https://www.niddk.nih.gov/health-information/diabetes/overview/risk-factors-type-2-diabetes")#..ok #dumped!
#get_data("https://www.niddk.nih.gov/health-information/diabetes/overview/preventing-type-2-diabetes") # ..ok #dumped!



#get_data("https://www.niddk.nih.gov/health-information/diabetes/overview/tests-diagnosis")#..ok #dumped!
#get_data(" ")#..ok


#get_data("https://www.niddk.nih.gov/health-information/health-communication-programs/ndep/living-with-diabetes/youth-teens/what-diabetes/Pages/publicationdetail.aspx") # ..ok


#get_data("https://www.niddk.nih.gov/health-information/health-communication-programs/ndep/partnership-community-outreach/campaigns/diabetes-heart-health/Pages/default.aspx") #..ok#dumped!

#There is nothing useful about diabetes here..

##        
##db = get_db()
##mark_url(db,"https://www.niddk.nih.gov/health-information/diabetes/overview/risk-factors-type-2-diabetes")
##mark_url(db,"https://www.niddk.nih.gov/health-information/diabetes/overview/preventing-type-2-diabetes") # ..ok #dumped!
##mark_url(db,"https://www.niddk.nih.gov/health-information/diabetes/overview/tests-diagnosis")#..ok #dumped!
##mark_url(db,"https://www.niddk.nih.gov/health-information/health-communication-programs/ndep/living-with-diabetes/youth-teens/what-diabetes/Pages/publicationdetail.aspx") # ..ok
##mark_url(db,"https://www.niddk.nih.gov/health-information/health-communication-programs/ndep/partnership-community-outreach/campaigns/diabetes-heart-health/Pages/default.aspx") #..ok#dumped!

#Testing
##get_data("test1.html")#..ok
##print "------------------------------------------------------------------------------------------"
##
##get_data("test2.html")#..ok
##print "------------------------------------------------------------------------------------------"
##
##get_data("test3.html")#..ok
##print "------------------------------------------------------------------------------------------"
##
##get_data("test4.html") #..ok
##print "------------------------------------------------------------------------------------------"
##
##get_data("test5.html") #..ok
##print "------------------------------------------------------------------------------------------"

