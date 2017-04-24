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
