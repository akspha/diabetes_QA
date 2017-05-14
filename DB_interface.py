###################################################
##MedWhat Diabetes Engine -Database Interface
##Akshay Surendra Phadnis
##April 21 2017
###################################################

def get_db():
    """
    Returns a connector to MongoDB
    """
    from pymongo import MongoClient
    client = MongoClient("localhost:27017")
    

    return client.diabetes_engine

def get_articles(db):
    """
    Returns the collection called articles
    """
    #return db.old_articles.find()#use this if , the original
    #data from CSV files with 195 rows is to be used!
    return db.articles.find()
def create_text_index(db):
    #This function creates a "text" index over the article_title_field
    db.articles.create_index({"article_title":"text"})
##db = get_db()
##def look_up(focus):
##    #return db.articles.find( {  "$where": "this.article_title == this.focus" } )
##    return db.articles.find( { "$where":   "Diabetes" == focus }  );
##for d in look_up("Diabetes"):
##    print d["section_title"]
