import csv
of = open("articles.csv", "w")
writer = csv.writer(of)
def put_into_articles(filename,):
    with open(filename,  "r") as f:
        reader = csv.reader(f,delimiter = ",")
        for row in reader:
                print (row)
                #row = [row[0].replace('\x00', '')]
                writer.writerow(row)
####            
##put_into_articles("non-diabetes_article_sections.csv")
##put_into_articles("diabetes_article_sections.csv")

