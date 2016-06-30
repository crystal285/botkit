import mysql.connector
from mysql.connector import Error
 
 
def connect():
    """ Connect to MySQL database """
    try:
        conn = mysql.connector.connect(host='localhost',
                                       database='innovation',
                                       user='root')
        if conn.is_connected():
            print('Connected to MySQL database')
            cursor = conn.cursor()
            cursor.execute("select count(1) from account;")
            row = cursor.fetchone()
 
            while row is not None:
                print(row)
                row = cursor.fetchone()
 
    except Error as e:
        print(e)
 
    finally:
        conn.close()
 

connect()



from dateutil import parser
from datetime import date,timedelta
import re
import calendar

def parse(self, timestr, default=None,
          ignoretz=False, tzinfos=None,
          **kwargs):
    return self._parse(timestr, **kwargs)
parser.parser.parse = parse


def parse_date(string):
    query_date=[]
    response=[]
    label=""
    substr = re.split('( on | in | between | from | and | to | since )',string)
    for substring in substr:
        substring = "".join(" " if c in ('!','.',':',',','-') else c for c in substring)    #ignore punctuation
        
        subdate=list(parser.parser().parse(substring, None, fuzzy_with_tokens=True))    #parse date

        today=date.today()
        if "today" in substring:
            subdate[0]=today
        if "yesterday" in substring:
            subdate[0]=today-timedelta(1)
        if "this" in substring:
            if "year" in substring:
                subdate[0].year=today.year
            if "month" in substring:
                subdate[0].year=today.year
                subdate[0].month=today.month
        if "last" in substring:
            if "year" in substring:
                subdate[0].year=today.year-1
            if "month" in substring:
                subdate[0].year=today.year
                subdate[0].month=today.month-1
                if subdate[0]==0:
                    subdate[0].year=today.year-1
                    subdate[0].month=12
        if subdate[0].year is None and (subdate[0].month is not None or subdate[0].day is not None):
            subdate[0].year=today.year

        if substring==' from ' or substring==" between " or substring==" since ":
            query_date.append("txn.posted_date>='")
            label="between"
        elif substring==' to ' or (substring==" and " and label=="between") or substring==" until " or substring==" till ":
            query_date.append("txn.posted_date<='")
            label="and"

        if subdate[0].year is not None or subdate[0].month is not None or subdate[0].day is not None:
            if label=="between":
                if subdate[0].month is None:
                    subdate[0].month=1
                    subdate[0].day=1
                elif subdate[0].day is None:
                    subdate[0].day=1
                norm_date = "-".join([str(subdate[0].year),str(subdate[0].month),str(subdate[0].day)])
                query_date.append(norm_date)
                query_date.append("'")
            elif label=="and":
                if subdate[0].month is None:
                    subdate[0].month=12
                    subdate[0].day=calendar.monthrange(subdate[0].year,subdate[0].month)[1]
                elif subdate[0].day is None:
                    subdate[0].day=calendar.monthrange(subdate[0].year,subdate[0].month)[1]
                norm_date = "-".join([str(subdate[0].year),str(subdate[0].month),str(subdate[0].day)])
                query_date.append(norm_date)
                query_date.append("'")
            else:
                if subdate[0].month is None:
                    norm_date_1 = "-".join([str(subdate[0].year),"01","01"])
                    norm_date_2 = "-".join([str(subdate[0].year),"12","30"])
                    norm_date = "' and '".join([norm_date_1,norm_date_2])
                    query_date.append("txn.posted_date between '")
                    query_date.append(norm_date)
                    query_date.append("'")
                elif subdate[0].day is None:
                    norm_date_1 = "-".join([str(subdate[0].year),str(subdate[0].month),"01"])
                    norm_date_2 = "-".join([str(subdate[0].year),str(subdate[0].month),str(calendar.monthrange(subdate[0].year,subdate[0].month)[1])])
                    norm_date = "' and '".join([norm_date_1,norm_date_2])
                    query_date.append("txn.posted_date between '")
                    query_date.append(norm_date)
                    query_date.append("'")
                else:
                    norm_date = "-".join([str(subdate[0].year),str(subdate[0].month),str(subdate[0].day)])
                    query_date.append("txn.posted_date='")
                    query_date.append(norm_date)
                    query_date.append("'")
        
    response="".join(query_date) 
    response=response.replace("'txn.posted_date","' and txn.posted_date")
    return response
    
    
    
