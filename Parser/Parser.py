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
import re

def parse(self, timestr, default=None,
          ignoretz=False, tzinfos=None,
          **kwargs):
    return self._parse(timestr, **kwargs)
parser.parser.parse = parse

def parse_date(string):
    response=[]
    substr = re.split(' and | to ',string)
    for substring in substr:
        substring = "".join(" " if c in ('!','.',':',',','-') else c for c in substring)
        date=parser.parser().parse(substring, None, fuzzy=True)
        response.append(date[0])
    return response
    
ddd=parse_date("How much money did I spend from 2014 11 27 to April 14")
print ddd