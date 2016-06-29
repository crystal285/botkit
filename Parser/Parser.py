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




############################################################################################
## Data definition
_txn_table = 'transaction'
_acc_table = 'acount'

_question_dict = {
    'acc_balance': [['how', 'much', 'have', 'balance'],
                    [0.2, 0.2, 0.1, 0.8],
                    [' act.balance from '+_acc_table+' act ']],
                    
    'card_limit' : [['credit', 'limit', 'more'],
                    [0.4, 0.4, 0.2],
                    [' max(act.total_limit) from '+ _txn_table + ' act ']],
                    
    'txn_spend'  : [['how', 'much', 'spend', 'cost'],
                    [0.2, 0.2, 0.4, 0.2],
                    [' sum(txn.amount) from ' + _txn_table + ' txn ' ]],
                    
    'txn_count'  : [['how', 'many', 'times', 'spend'],
                    [0.2, 0.2, 0.4, 0.2],
                    [' count(1) from '+ _txn_table + ' txn ']]
                    
}
#
#_filter_dict = {
#
#}
_filter_date_range  = ['since', 'from', 'last', 'between', 'this']
_filter_category    = ['shopping', 'food', 'movie', 'gas']
_filter_merchant    = ['target', 'bloomingdales']
_filter_institution = ['chase', 'boa', 'discover']
_filter_acc_type    = ['debit', 'credit', 'checking', 'saving']



## Class Question
class Question:
    name ='';
    keywords=[];
    keywordScores = [];
    queryTemplate = '';
    
    def __init__(self, n, kws, scores, temp):
        self.name = n
        self.keywords = kws
        self.keywordScores = scores
        self.queryTemplate = temp;


    def calScore (self, words):
        total = 0
        for w in words:
            for i, v in enumerate(self.keywords):
                if w == v:
                    total += self.keywordScores[i]
        return total


    def getQuery(self):
        return self.queryTemplate



## Class Filter
class Filter:
    name = '';
    queryTemplate ='';
    valuesInOrder= [];

    def __init__(self, n, temp, values):
        self.name = n
        self.queryTemplate = temp
        self.valuesInOrder = values

    def getQuery(self):
        print 'print filter query';



questionList = [];
filterList = [];

def init():
    for key, value in _question_dict.iteritems():
        obj = Question(key, value[0], value[1], value[2][0])
        questionList.append(obj)

                    
init()
                    
                    
## compose sql query based on the provided keywords
def selectQuery(words):
    max = 0
    qestion = questionList[0]
    
    for q in questionList :
        score = q.calScore(words)
        if score > max:
            max = score
            question = q

    print 'score = {}'.format(max)
    print question.getQuery()


selectQuery(['how', 'many', 'times', 'balance']);




