from re import findall
from datetime import date

units = ["[yY]ear", "[Mm]onth", "[Ww]eek", "[Dd]ays"]
months = {"[Jj]anuary":1, "[Ff]ebruary":2, "[Mm]arch":3, "[Aa]pril":4, "[Mm]ay":5, "[Jj]une":6, "[Jj]uly":7, "[Aa]ugust":8, "[Ss]eptember":9, "[Oo]ctober":10, "[Nn]ovember":11, "[Dd]ecember":12}
seasons = ["[Ss]pring", "[Ff]all", "[Ss]ummer", "[Mm]onsoon","[Ss]eason"]

def get_days(d, dmy = False):
    if not dmy:
        if "-" in d:
                   mm1, dd1, yyyy2 = tuple(d.split("-"))
        elif "/" in d:
            mm1, dd1, yyyy2 = tuple(d.split("/"))
        else:
            mm1, dd1, yyyy2 = tuple(d.split(" "))
        return date(int(yyyy2),int(mm1),int(dd1))
    else:
        if "-" in d:
                   dd1, mname, yyyy2 = tuple(d.split("-"))
        elif "/" in d:
            dd1, m, yyyy2 = tuple(d.split("/"))
        else:
           dd1, m, yyyy2 = tuple(d.split(" "))
        dd1 = dd1.strip("th").strip("nd").strip("st")
        #print date(int(yyyy2), int( months[ "["+m[0].upper() + m[0].lower()+ "]"+m[1:] ]),int(dd1)  )
        return date(int(yyyy2), int( months[ "["+m[0].upper() + m[0].lower()+ "]"+m[1:] ]),int(dd1)  )
    
def temporal_er(q):
    """
    String-> 
    """
    

    
    

    qn = len(q)
    try:
        since_then_idx = q.index("since then")
    except ValueError:
        since_then_idx = -1
    if 0 < since_then_idx < qn:
        q = q[:since_then_idx].replace("in","since")
        
    
    chronic_present_explicitly = False
    if "chronic" in q:
        chronic_present_explicitly = True
     
    re_date_format = "\d{1,2}(?:[- /])\d{1,2}(?:(?:[- /])\d{4})"
    date_from_to_period_match = findall("from.*"+ re_date_format + ".*to.*" +re_date_format, q )
    
    date_from_to_period_bool = False
    if date_from_to_period_match != [] :
        date_from_to_period = findall(re_date_format,q)
       
        if (get_days( date_from_to_period[1] ) - get_days( date_from_to_period[0] ) ).days > 7:
            date_from_to_period_bool = True
   
    date_from_today_bool = False
    date_period_match = findall("(?:since|from)?.*"+ re_date_format,q)
    
    if date_period_match  != []:
        date_period  = findall(re_date_format,q)
##        print date_period
##        print get_days( date_period[0] )
##        print date.today()
       
        if len(date_period)== 1 and (  date.today()-get_days( date_period[0] ) ).days > 7: 
            date_from_today_bool = True
   
    re_units ="(?:" +"|".join(units) + ")"
    units_period = findall('(?:since|from|last|previous|past|for)?.*'+re_units,q)
    #print units_period
    
    re_months ="(?:" +"|".join(months.keys()) + ")"
    months_period = findall('(?:since|from|through|for).*'+re_months + "(?:.*\d{4})?",q)
    
    months_year_text = " ".join( months_period)
    
    month_year_bool = False
    dates_m_y = []
    if months_period!= []:
        my = findall(re_months + "(?: \d{4})?",months_year_text)
        
        if  my != []:
         for mye in my:
             mye_lst = mye.split(' ')
             m= mye_lst[0]
             if len(mye_lst) > 1 :
                 y = mye_lst[1]
             else:
                 y = date.today().year
             
             dates_m_y.append( date( int(y),months[ "["+m[0].upper() + m[0].lower()+ "]"+m[1:]  ] ,1) )     
    
    num_my = len(dates_m_y)
    if num_my == 2:
         
         if  (dates_m_y[1] -dates_m_y[0]).days > 7:
             month_year_bool = True
         if (dates_m_y[1] -dates_m_y[0]).days < 0 :
            month_year_bool = False
            
            months_period =[]
             
    if num_my == 1:
        
        if (date.today() -dates_m_y[0]).days < 0 :
            month_year_bool = False
            
            months_period =[]
        if  (date.today() -dates_m_y[0]).days > 7:
             month_year_bool = True
    #print month_year_bool
    ##
    re_seasons ="(?:" +"|".join(seasons) + ")"
    seasons_period = findall('(?:since|from|through|for).*'+re_seasons,q)
    ##print seasons_period

    #day month year
    re_dmy_format = "\d{1,2}(?:th|nd|st)?(?:[- /])"+ re_months +"(?:(?:[- /])\d{4})"
    dmy_period_match = findall("from|since.*"+ re_dmy_format + "(?:.*to.*" +re_dmy_format+")?", q )
    
    dmy_period_bool = False
    if dmy_period_match != [] :
        dmy_period = findall(re_dmy_format,q)
        
        l_dmy = len(dmy_period)
        if l_dmy == 2:
            if (get_days( dmy_period[1],True ) - get_days( dmy_period[0] , True) ).days > 7:
                dmy_period_bool = True
            else:
                dmy_period_bool = False
        else:
           
            if ( date.today() - get_days( dmy_period[0], True ) ).days > 7:
                dmy_period_bool = True
                
            else:
                dmy_period_bool = False
        if not dmy_period_bool:
            months_period = []
            month_year_bool = False
        
    #day month
    re_dm_format = "\d{1,2}(?:th|nd|st)?(?:[- /])"+ re_months
    dm_period_match = findall("from since.*" + re_dm_format, q)
            
##    print "-------------------------"
##    print q
##    print "seasons: " , seasons_period != []
##    print "month_year: ", month_year_bool
##    print "units: ", units_period != []
##    print "months_period: ", months_period != []
##    print "date from today: ", date_from_today_bool
##    print "date from to: ", date_from_to_period_bool
##    print "chronic_present_explicitly: ", chronic_present_explicitly
##    print "day month year: ", dmy_period_bool
##    
    return any([seasons_period != [], month_year_bool, units_period != [], months_period != [], date_from_today_bool, date_from_to_period_bool, chronic_present_explicitly]) 

#######date formats   
##print temporal_er("She has been sick from 03/05/1991 to 03/15/1991") == True #..ok
##print temporal_er("She has been sick from 03/05/1991 to 03 15 1991")  == True
##print temporal_er("She has been sick from 03/05/1991 to 03/05/1991") == False #..ok
##print temporal_er("She has been sick from 03/05/1991 to 04/05/1991") == True #..ok
##print temporal_er("She has been sick from 03/05/1991 to 03/05/1992")  == True#..ok
##print temporal_er("She has been sick from 03/05/1992 to 03/05/1992") == False #..ok
####
####dates compared with today
####+ve examples
print temporal_er("She has been sick since 03/06/1991") == True #..ok
print temporal_er("She has been sick since 03/02/2017")  == True#..ok
##-ve examples
print temporal_er("She has been sick since 03/20/2017") == False #..ok ## date within days of today
print temporal_er("She has been sick since 03/02/2018")  == False#..ok ##  date< than today 
##
######units
###### +ve examples
##print temporal_er("it's been weeks") == True #..ok
##print temporal_er("it started days ago") == True#..ok
##print temporal_er("for years, she has been suffering") == True#..ok
##print temporal_er("Several months have passed and she is still recovering")== True#..ok
##print temporal_er("She has been weak for a year") == True #..ok
####
######-ve examples , those that return []
##print temporal_er("") == False#..ok 
##print temporal_er("she is ill today") == False#..ok
##print temporal_er("What is your favorite season") == False#..ok ##Season is not being treated as unit as examples like this would be mis-classified
##
####
######months
###if a year is not specified, system will assume the
###current year!
##
######+ve examples
##
##print temporal_er("it's been like this since December") == False #..ok 
##print temporal_er("she suffered through December") == False#..ok
##print temporal_er("I have been 18 since December") == False #..ok
##print temporal_er("I have been 18 since January")  == True #This temporal entity recognizer is not specifcic
###to medical terms
##print temporal_er("I have been ill since January") == True
##print temporal_er("She has suffered from diabetes since February") == True
##print temporal_er("She has suffered from diabetes since April") == False
####
###### -ve examples , those that return []
##print temporal_er("") == False #..ok 
##print temporal_er("Penicilin was discoveredin May") == False#..ok
##print temporal_er("It is my birthday in february") == False #..ok
####
######seasons
#### ##+ve examples
##print temporal_er("it's been like this since Fall") == True #..ok
##
##print temporal_er("she suffered through Monsoon") == True#..ok
####
##### -ve examples , those that return []
##print temporal_er("") == False#..ok 
##print temporal_er("Spring is my favorite season") == False#..ok
####
######date formats
##print temporal_er("I have been having this problem since 12-02-2015") == True#..ok
##print temporal_er("I have been having this problem since 12-02-2018") == False #..ok
##print temporal_er("I have been having this problem since 03-18-2017") == False #..ok
##
####
######Other examples
##
##print temporal_er("last fall i was  ill") == False #..ok
##print temporal_er("I have been diabetic for past 2 years") == True #..ok
##print temporal_er("I have been diabetic from previous Spring") == True #..ok
##print temporal_er("I have been diabetic from previous Spring") == True #..ok
##
##
###Month/Season Year  combination
######+ve examples
##print temporal_er("My birthday was in December 2008 and since February, I i have been ill") == True #chronic
##print temporal_er("My birthday was in December 2008 and since February 2009, I i have been ill") == True #chronic
##print temporal_er("My birthday was in December 2008 and since February 2019, I i have been ill") == False #chronic
##print temporal_er("I had a heart attacks from  January 2009 to February 2009 ") == True #chronic
##print temporal_er("I had a heart attack in  January 2017 and since then I have had mild tremors")  == True# chronic
##
##
##print temporal_er("I have had chronic diarrhoea") == True
######
######print "---------------------"
######-ve examples
##print temporal_er("I had a heart attack in  December 2018 and since then I have had mild tremors") == False #not chronic, yet to happen
##print temporal_er("I had a heart attack in  December 2017 and since then I have had mild tremors")  == False#not chronic
##print temporal_er("I had a heart attacks from  December 2008 to February 2008 ") == False #not possible, therefore not chronic
##
##
######
######
##
####these quesitions are treated as if they were asked today
##
##print temporal_er("I have been having pain since March started")  == True
##print temporal_er("I have been having pain since January started") == True
##print temporal_er("I have been having pain since April started") == False
###this is a counter/negative example
##
##print temporal_er("I had a heart attack in  March 2017 and since then I have had mild tremors") == True##
##print temporal_er("My birthday was in December 2008 and since then, I i have been ill") == True #chronic
##print temporal_er("I had a heart attack in  December 2008 and since then I have had mild tremors") == True #chronic
##print temporal_er("I had a heart attack in  February 2017 and since then I have had mild tremors")  == True#chronic
##print temporal_er("I had a heart attack in  February 2050 and since then I have had mild tremors")  == False#chronic
##print temporal_er("I had a heart attacks throughout  December 2008 ") == True #chronic
##print temporal_er("I had a heart attacks from  December 2008 to February 2009 ") == True #chronic
##print temporal_er("I had a heart attacks from  January 2009 to February 2009 ") == True #chronic
##print temporal_er("I had a heart attack in  January 2017 and since then I have had mild tremors")  == True# chronic
##
##
##print temporal_er("I have had chronic diarrhoea") == True
######
######print "---------------------"
######-ve examples
##print temporal_er("I had a heart attack in  December 2018 and since then I have had mild tremors") == False #not chronic, yet to happen
##print temporal_er("I had a heart attack in  December 2017 and since then I have had mild tremors")  == False#not chronic
##print temporal_er("I had a heart attacks from  December 2008 to February 2008 ") == False #not possible, therefore not chronic
##
##
######
######
##
####these quesitions are treated as if they were asked today
##
##print temporal_er("I have been having pain since March started")  == True
##print temporal_er("I have been having pain since January started") == True
##print temporal_er("I have been having pain since April started") == False
#####this is a counter/negative example
####
##print temporal_er("I had a heart attack in  March 2017 and since then I have had mild tremors") == True
####system is going to assume this means from begining of March till today and hence, it will return True
##
####!!!
####If year is not specified, system should assume the current year
####Month day - resolve clashes with  months_period, months_year #!!!
##
##print temporal_er("since December 8th i have been ill")  ==  False #..ok #!!!
##print temporal_er("since December 8 i have been ill")  ==  False
##print temporal_er("since January 8 i have been ill")  ==  True
###print temporal_er("since June 8 i have been ill")  ==  False # yet to happen
##
###print temporal_er("since 8th December i have been ill")  ==  False #..ok #!!!
###print temporal_er("since 8 December i have been ill")  ==  False
##print temporal_er("since 8 January i have been ill")  ==  True
##print temporal_er("since 8 June i have been ill")  ==  False # yet to happen


#day month  year
#resolved clashes with months_period, months_year

print temporal_er("since 8 June 8 i have been ill") == False  #this should not be allowed #..ok
print temporal_er("since 8 June 2016 i have been ill") == True #this should not be allowed #..ok
print temporal_er("since 2 March 2017 I have been ill") == True #..ok
print temporal_er("since 28 March 2017 I have been ill") == False #..ok

print temporal_er("since 8th June 8 i have been ill") == False  #this should not be allowed #..ok
print temporal_er("since 8th June 2016 i have been ill") == True #this should not be allowed #..ok
print temporal_er("since 2nd March 2017 I have been ill") == True #..ok
print temporal_er("since 28th March 2017 I have been ill") == False #..ok
print temporal_er("since 1st March 2017 I have been ill") == True #..ok



##Month day case #!!!

