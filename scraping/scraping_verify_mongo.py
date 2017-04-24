def get_db():
    from pymongo import MongoClient
    client = MongoClient("localhost:27017")
    

    return client.diabetes_engine

def show_url_counts_from_file(filename, set_urls = set([])):
    """
    String -> None
    Takesname of a file bearing one url on each line and for each url,
    shows that url and the number of times it appears in the urls collection
    """
    db = get_db()
    f = open(filename,"r")
    links = f.readlines()
    
    for link in links:
        if set_urls == set([])
            print link
            print db.urls.find({"link":link}).count()
            
            print
        else:
            print link
            print link in set_urls
        


def show_url_counts():
    """
    Prints urls and their counts in the collection named urls
    
    """
    db = get_db()
    set_urls = set([])
    count = 0
    for link in db.urls.find():
         print link
         #print link.count()
         print db.urls.find({"link":link}).count()
         print
         set_urls.add(link["link"])
         count = count + 1
    print len(set_urls) == count
    return set_urls

set_urls = show_url_counts()
show_url_counts_from_file("urls.txt", set_urls)


