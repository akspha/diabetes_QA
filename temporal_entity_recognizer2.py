from re import findall as ref
from datetime import date
from pprint import pprint

units = {"[yY]ear":365, "[Mm]onths":30, "[Ww]eeks":7, "[Dd]ays":1}
months = {"[Jj]anuary":1, "[Ff]ebruary":2, "[Mm]arch":3, "[Aa]pril":4, "[Mm]ay":5, "[Jj]une":6, "[Jj]uly":7, "[Aa]ugust":8, "[Ss]eptember":9, "[Oo]ctober":10, "[Nn]ovember":11, "[Dd]ecember":12}
seasons = {"[Ss]pring":(3,20), "[Ff]all":(7,22), "[Ss]ummer": (5,20), "[Mm]onsoon":(6,15), "[Ww]inter":(12,21)}


    

def get_dates(q, num_days_after_which_disease_is_chronic= 30*3):
    """
    String -> list of Strings
    Given a question, extract all references to a date (in any form)
    """


    units_format = "(?:"+"|".join(units.keys()) + ")"
    
    mmddyyy_format = "(?:\d{1,2}(?:[- /])\d{1,2}(?:(?:[- /])\d{4}))"
    
    month_format ="(?:" +"|".join(months.keys()) + ")"
    
    seasons_format ="(?:" +"|".join(seasons) + ")"

    month_year_format = "(?:"+ month_format +  " \d{4}" + ")"

    month_day_format = "(?:"+ month_format + " \d{1,2}(?:th|st|rd|nd)?)"
    
    day_month_format = "(?:" + "\d{1,2}(?:th|st|rd|nd)? " + month_format  + ")"
    
    day_month_year_format = "(?:" + "\d{1,2}(?:th|st|rd|nd)? " + month_format + " \d{4})"

    season_year_format = "(?:" +  seasons_format + "(?:(?: \d{4})|(?: \d{2}))"+ ")"

    def get_py_date(s):
        """
        String -> Date
        """
        tyear = date.today().year
        
        tday = date.today().day
        
        if ref(mmddyyy_format,s) != []:
           
            if "-" in s:
                   mm1, dd1, yyyy2 = tuple(s.split("-"))
            elif "/" in s:
                mm1, dd1, yyyy2 = tuple(s.split("/"))
            else:
                
                mm1, dd1, yyyy2 = tuple(s.split(" "))
            return date(int(yyyy2),int(mm1),int(dd1))
        
        if ref( season_year_format, s) != []:
            
            ss, y = tuple(s.split(" "))
            if len(y) == 2:
                y = "20"+y
            m,d = seasons["["+ss[0].upper() + ss[0].lower()+ "]"+ss[1:] ]
            return date(int(y),int(m),int(d))
        
        if ref(seasons_format,s) != []:
            
           ss=  s[0]
           m,d = seasons["["+ss[0].upper() + ss[0].lower()+ "]"+ss[1:] ]
           
           return date(tyear, m, d)

        
        if ref(day_month_year_format,s)!= []:
            d, m, y =  tuple( s.split(" ") )
            
            for criterion in ["th","st","rd","nd"]:
                d = d.strip(criterion)
           
            return date(int(y),months["["+m[0].upper() + m[0].lower()+ "]"+m[1:] ],int(d) )
        
        if ref(month_year_format,s) != []:
           m, y =  tuple( s.split(" ") )
           return date(int(y),months["["+m[0].upper() + m[0].lower()+ "]"+m[1:] ],1 )
        
        
        
        if ref(day_month_format, s)!= []:

            d,m = tuple(s.split(" "))

            for criterion in ["th","st","rd","nd"]:
                d = d.strip(criterion)
                
            return date(tyear,months["["+m[0].upper() + m[0].lower()+ "]"+m[1:] ], int(d) )

        if ref(month_day_format, s)!= []:
            m, d =  tuple( s.split(" ") )
            
            for criterion in ["th","st","rd","nd"]:
                d = d.strip(criterion)
                
            return date(tyear,months["["+m[0].upper() + m[0].lower()+ "]"+m[1:] ], int(d) )
        
        
        if ref(month_format,s) != []:
            return date( tyear, months["["+s[0].upper() + s[0].lower()+ "]"+s[1:] ],1)
        
        ##    print"-------------------------------------------------------" #move to be left till # meet the end of the screen
        ##    print q
        ##    print "mmddyyy_format: ", ref(mmddyyy_format,q)
        ##    print "month_format: ", ref(month_format,q)
        ##    print "month_year_format: ", ref(month_year_format,q)
        ##    print "month_day_format: ", ref(month_day_format,q)
        ##    print "day_month_format: ", ref(day_month_format,q)
        
    re_date ="(?:" +"|".join([mmddyyy_format,season_year_format,seasons_format,day_month_year_format,month_year_format,day_month_format,month_day_format,month_format  ]) + ")"
    re_units = "(?:(?:\d)+)?(?: (?:" + "|".join(units.keys()) + "))"
    
    re_duration = "(?:"+ "|".join( [ "(?:(?:for|since) )"+ re_units,"(?:from "+re_date + " to " + re_date+")","(?:from(?: last | previous )? "+ re_date + ")", "(?:since(?: last | previous )? "+re_date + ")", "(?:"+re_date + ".*since then" + ")", "(?:through(?:out)? " + re_date])+"))"
    result_match = ref(re_duration,q)

    pydates = []
    result_string = " ".join(result_match)
    
    if result_match != []:#if potentially chronic
        dates_in_q = ref(re_date,result_string)
        
        
        for d in dates_in_q:
            pydates.append( get_py_date(d))

        units_in_q = ref(re_units, result_string)

        if len(units_in_q ) == 1:
           u =  units_in_q[0]
           
           num, unit =  u.split(" ")
           days = units["["+unit[0].upper() + unit[0].lower()+ "]"+unit[1:]]
           if int(num)*days >= 7:
               return True
           else:
                return False
            
            
    numdates = len(pydates)
    
    if numdates == 1:
       if ( date.today() - pydates[0]).days >=  num_days_after_which_disease_is_chronic :#7:#3*30:
           return True
       else:
            return False
    elif numdates == 0:
        return False
    elif numdates == 2:
        if (pydates[1] - pydates[0] ).days >= num_days_after_which_disease_is_chronic:#7: #3*30:
            return True
        else:
            return False


##print get_dates("",7) == False
##print get_dates(" ",7) == False
##
####
##print get_dates("I have been ill since 5 weeks",7) == True #..ok
##print get_dates("I have been pregnant for 9 months now",7) == True #..ok
##print get_dates("My birthday was 0 weeks ago & I have been pregnant for 9 months now",7) == True #..ok
##print get_dates("I have been pregnant for 0 months now",7) == False #..ok
####           
####            
##print get_dates("She has been sick from 03/05/1991 to 03/15/1991",7)  == True #..ok
##print get_dates("She has been sick from 03/05/1991",7) == True #..ok
##print  get_dates("She has been sick from 03/05/1991 to December",7)
##print get_dates("She has been sick from 03/05/1991 to 5 December 1991",7) == True #..ok
##print get_dates("She has been sick from 03/05/1991 to 5 December",7) == True #..ok
##print get_dates("She has been sick from 03/05/1991 to 5th December",7) == True #..ok
##print get_dates("She has been sick from 5th December 1992 to 03/05/1993",7) == True #..ok
##print get_dates("She has been sick from 5th October to December",7) == True #..ok
##print get_dates("She has been sick from 03/05/1991 to 03 15 1991",7)  == True
##print get_dates("She has been sick from 03/05/1991 to 03/05/1991",7) == False #..ok
##print get_dates("She has been sick from 03/05/1991 to 04/05/1991",7) == True #..ok
##print get_dates("She has been sick from 03/05/1991 to 03/05/1992",7)  == True#..ok
##print get_dates("She has been sick from 03/05/1992 to 03/05/1992",7) == False #..ok
##print get_dates("She has been sick from Fall 15 to 03/05/1992",7) == False #..ok
##print get_dates("She has been sick from Fall 2015 to 03/05/1992",7) == False #..ok
######
######dates compared with today
####+ve examples
##print get_dates("She has been sick since 03/06/1991",7) == True #..ok
##print get_dates("She has been sick since 03/02/2017",7)  == True#..ok
####-ve examples
##print get_dates("She has been sick since 03/20/2017",7) == False #..ok ## date within days of today
##print get_dates("She has been sick since 03/02/2018",7)  == False#..ok ##  date< than today 
##
##########months
#######if a year is not specified, system will assume the
#######current year!
######
##########+ve examples
####
##print get_dates("it's been like this since December",7)  == False #..ok 
##print get_dates("she suffered through December",7) == False#..ok
##print get_dates("I have been 18 since December",7) == False #..ok
##print get_dates("I have been 18 since January",7)  == True #This temporal entity recognizer is not specifcic
###to medical terms
##print get_dates("I have been ill since January",7) == True
##print get_dates("She has suffered from diabetes since February",7) == True
##print get_dates("She has suffered from diabetes since April",7)== False
######
###### -ve examples , those that return []
##print get_dates("Penicilin was discoveredin May",7) ==False#..ok
##print get_dates("It is my birthday in february",7) == False #..ok
##
##
##
##
######date formats
##print get_dates("I have been having this problem since 12-02-2015",7) == True#..ok
##print get_dates("I have been having this problem since 12-02-2018",7)==False #..ok
##print get_dates("I have been having this problem since 03-18-2017",7) == True #..ok
##
##
#####Month/Season Year  combination
########+ve examples
##print get_dates("My birthday was in December 2008 and since February, I i have been ill",7) == True #chronic #..ok
##print get_dates("My birthday was in December 2008 and since February 2009, I i have been ill",7) == True #chronic #..ok
##
##
##print get_dates("My birthday was in December 2008 and since February 2019, I i have been ill",7) == False #chronic #..ok
##
##print get_dates("I had a heart attacks from January 2009 to February 2009 ",7) == True #chronic #..ok
##print get_dates("I had a heart attack in January 2017 and since then I have had mild tremors",7)  == True# chronic #..ok
##
##
##
########-ve examples
##print get_dates("I had a heart attack in  December 2018 and since then I have had mild tremors",7) == False #not chronic, yet to happen #..ok
##print get_dates("I had a heart attack in  December 2017 and since then I have had mild tremors",7)  == False#not chronic #..ok
##print get_dates("I had a heart attacks from December 2008 to February 2008 ",7) ==False #not possible, therefore not chronic #..ok
##
##
##
######these quesitions are treated as if they were asked today
####
##print get_dates("I have been having pain since March started",7)  == True #..ok
##print get_dates("I have been having pain since January started",7) == True #..ok
##print get_dates("I have been having pain since April started",7) ==False  #..ok
#####this is a counter/negative example
##
##print get_dates("I had a heart attack in  March 2017 and since then I have had mild tremors",7) == True## #..ok
##print get_dates("My birthday was in December 2008 and since then, I i have been ill",7) == True #chronic #..ok
##print get_dates("I had a heart attack in  December 2008 and since then I have had mild tremors",7)== True #chronic #..ok
##print get_dates("I had a heart attack in  February 2017 and since then I have had mild tremors",7) == True#chronic #..ok
##print get_dates("I had a heart attack in  February 2050 and since then I have had mild tremors",7)  == False#chronic #..ok
##print get_dates("I had a heart attacks throughout December 2008 ",7) ==True #chronic #..ok
##print get_dates("I had a heart attacks from December 2008 to February 2009 ",7) == True #chronic #..ok
##print get_dates("I had a heart attacks from January 2009 to February 2009 ",7) == True #chronic #..ok
##print get_dates("I had a heart attack in January 2017 and since then I have had mild tremors",7) == True# chronic #..ok
##
##
########-ve examples
##print get_dates("I had a heart attack in December 2018 and since then I have had mild tremors",7) == False #not chronic, yet to happen #..ok
##print get_dates("I had a heart attack in December 2017 and since then I have had mild tremors",7)  == False#not chronic #..ok
##print get_dates("I had a heart attacks from December 2008 to February 2008 ",7) == False #not possible, therefore not chronic #..ok
##
##
##
##print get_dates("I had a heart attack in March 2017 and since then I have had mild tremors",7)== True#..ok
######system is going to assume this means from begining of March till today and hence, it will return True
##
##
##
######If year is not specified, system should assume the current year
######Month day - resolve clashes with  months_period, months_year #!!!
####
##print get_dates("since December 8th i have been ill",7)  ==  False #..ok #!!!
##print get_dates("since December 8 i have been ill",7)  ==  False #..ok
##print get_dates("since January 8 i have been ill",7)  == True #..ok
##
##print get_dates("since June 8 i have been ill",7)  ==  False # yet to happen #..ok
##
##print get_dates("since 8th December i have been ill",7)   == False##  False #..ok #!!!
##print get_dates("since 8 December i have been ill",7)  == False ##  False
##print get_dates("since 8 January i have been ill",7)  ==  True
##print get_dates("since 8 June i have been ill",7)  ==  False # yet to happen
####
####
######day month  year
######resolved clashes with months_period, months_year
##
##print get_dates("since 8 June 8 i have been ill",7) == False  #this should not be allowed #..ok
##print get_dates("since 8 June 2016 i have been ill",7) == True #this should not be allowed #..ok
##print get_dates("since 2 March 2017 I have been ill",7) ==True #..ok
##print get_dates("since 28 March 2017 I have been ill",7)== False #..ok
##
##print get_dates("since 8th June 8 i have been ill",7) == False  #this should not be allowed #..ok
##print get_dates("since 8th June 2016 i have been ill",7) == True #this should not be allowed #..ok
##print get_dates("since 2nd March 2017 I have been ill",7) == True #..ok
##print get_dates("since 28th March 2017 I have been ill",7) == False #..ok
##print get_dates("since 1st March 2017 I have been ill",7) == True #..ok
##print get_dates("I had a heart attack in  March 2017 and since 01 January 2015 I have had mild tremors",7)== True #..ok
##print get_dates("During Monsoon I missed Spring",7) == False #..ok
##print get_dates("Eversince  Fall  started, I missed Spring",7) == False #..ok
