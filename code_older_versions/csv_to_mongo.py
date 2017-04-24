from pprint import pprint
def get_db():
    """
    Nothing -> database handle
    Open a connection to MongoDB and return a handle to a database pertaining to
    the diabetes engine
    """
    from pymongo import MongoClient
    client = MongoClient("localhost:27017")
    db = client.diabetes_engine
    #diabetes_engine is the name of a database
    #and it will be created if it does not exist
    return db

def get_csv_data(filename):
    """
    String -> list of dictionaries
    Read the contents of an input CSV file and return them as a list of dictionaries
    with one dictionary corresponding to each row
    """
    import csv
    f = open(filename, "r")
    r=  csv.DictReader(f)
    #pprint([dic for dic in r])
    return [dic for dic in r]

def put_data(data, db):
    """
    list of dictionaries*database hanlde -> None
    Given the contents of a CSV file as a list of
    dictionaries, put them in the database specified by the second argument
    which is a database handle
    """
    import datetime
    #from datetime import date
    #article_section   section_title article_title
    for d in data:
        db.old_articles.insert({"article_section": d["article_section"], "section_title": d["section_title"], "article_title": d["article_title"], "date_scraped":datetime.datetime.today(), "url":""})

def show(db):
    from pprint import pprint

    for a in db.articles.find() :
        pprint(a)
        print "-------------------------------------------------------------"

def find(fieldname,db)    :
    
    for row_dic in db.articles.find():
        
        print row_dic[fieldname]
        print "-------------------------------------------------------------"
        
if __name__ == "__main__":
    db = get_db()
    data = get_csv_data("articles.csv")#..ok
    #print len(data)
    put_data(data,db)#..ok
    #show(db) #..ok
    #find("article_section",db)#..ok
    #find("article_title",db)#..ok
    #find("section_title",db) #..ok
    
