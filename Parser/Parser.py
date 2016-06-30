import mysql.connector
from mysql.connector import Error
from dateutil import parser
from datetime import date,timedelta
import re
import calendar
from nltk.tokenize import RegexpTokenizer
import sys


#q_from_user="How much !money $did I spend on shopping and restaurant using chase sapphire since 2014 02-01!!"
#q_from_user="What is my account balance?"

q_from_user=str(sys.argv)

##########################
##  normalize sentence  ##
##########################

def normalize(string):
    string=string.lower()
    return string


#########################
##  tokenize sentence  ##
#########################

def keyword(string):
    string=normalize(string)
    tokenizer = RegexpTokenizer(r'\w+')
    stop_word=["i","did","do","am","please","you","u"]
    response = tokenizer.tokenize(string)
    return [word for word in response if word not in stop_word]


####################################
##  package date parser redefine  ##
####################################

def parse(self, timestr, default=None,
          ignoretz=False, tzinfos=None,
          **kwargs):
    return self._parse(timestr, **kwargs)
parser.parser.parse = parse

############################
##  date parser function  ##
############################

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
            elif subdate[0].year is None and subdate[0].month is not None:
                subdate[0].year=today.year
        if "last" in substring:
            if "year" in substring:
                subdate[0].year=today.year-1
            if "month" in substring:
                subdate[0].year=today.year
                subdate[0].month=today.month-1
                if subdate[0]==0:
                    subdate[0].year=today.year-1
                    subdate[0].month=12
            elif subdate[0].year is None and subdate[0].month is not None:
                subdate[0].year=today.year-1
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




######################
##  parse category  ##
######################

def parse_category(keywords):
    category_dict={"shopping":"Shopping",
                   "restaurant":"Restaurants",
                   "food":"Food & Dining",
                   "gas":"Gas & Fuel",
                   "movie":"Movies & DVDs",
                   "clothing":"Clothing",
                   "clothes":"Clothing"}
    category_filt=[category_dict[word] for word in keywords if word in category_dict.keys()]
    query="','".join(category_filt)
    if query!='':
        query="txn.category_name in ('"+query+"')"
    else:
        query=''
    return query


#########################
##  parse institution  ##
#########################

def parse_institution(keywords):
    institution_dict={"chase":"Chase",
                      "boa":"BOA",
                      "discover":"Discover"
                     }
    institution_filt=[institution_dict[word] for word in keywords if word in institution_dict.keys()]
    query="','".join(institution_filt)
    if query!='':
        query="act.institution in ('"+query+"')"
    else:
        query=''
    return query

#######################
##  parse card name  ##
#######################

def parse_card(keywords):
    card_dict={"freedom":"Freedom",
               "sapphire":"Sapphire",
               "cashReward":"CashReward",
               "checking":"Checking",
               "saving":"Saving"
              }
    card_filt=[card_dict[word] for word in keywords if word in card_dict.keys()]
    query="','".join(card_filt)
    if query!='':
        query="act.card_name in ('"+query+"')"
    else:
        query=''
    return query



##########################
##  parse account type  ##
##########################

def parse_accounttype(keywords):
    accounttype_dict={"credit":"200",
                      "debit":"100','101"
                     }
    accounttype_filt=[accounttype_dict[word] for word in keywords if word in accounttype_dict.keys()]
    query="','".join(accounttype_filt)
    if query!='':
        query="act.account_type in ('"+query+"')"
    else:
        query=''
    return query


########################
##  Data definition  ##
########################

_txn_table = 'transaction txn join account act on txn.account_id=act.id'
_acc_table = 'account'

_question_dict = {
    'acc_balance': [['how', 'much', 'have', 'balance'],
                    [0.2, 0.2, 0.1, 0.8],
                    [" sum(case when act.account_type in ('200','201') then -act.balance when act.account_type not in ('200','201') then act.balance end) from "+_acc_table+' act '],
                    ['Your account balance is {}']],
                    
    'card_limit' : [['credit', 'limit', 'more'],
                    [0.4, 0.4, 0.2],
                    [' max(act.total_limit) from '+ _acc_table + ' act '],
                    ['Your credit card total limit is {}']],
                    
    'txn_spend'  : [['how', 'much', 'spend', 'cost'],
                    [0.2, 0.2, 0.4, 0.2],
                    [' sum(txn.amount) from ' + _txn_table ],
                    ['You have spent {}']],
                    
    'txn_count'  : [['how', 'many', 'times', 'spend'],
                    [0.2, 0.2, 0.4, 0.2],
                    [' count(1) from '+ _txn_table],
                    ['You have spent {} times']]
                    
}#
#_filter_dict = {
#
#}
_filter_date_range  = ['since', 'from', 'last', 'between', 'this']
_filter_category    = ['shopping', 'food', 'movie', 'gas']
_filter_merchant    = ['target', 'bloomingdales']
_filter_institution = ['chase', 'boa', 'discover']
_filter_acc_type    = ['debit', 'credit', 'checking', 'saving']



######################
##  Class Question  ##
######################

class Question:
    name ='';
    keywords=[];
    keywordScores = [];
    queryTemplate = '';
    answerTemplate = '';
    
    def __init__(self, n, kws, scores, temp, answer):
        self.name = n
        self.keywords = kws
        self.keywordScores = scores
        self.queryTemplate = temp;
        self.answerTemplate = answer;


    def calScore (self, words):
        total = 0
        for w in words:
            for i, v in enumerate(self.keywords):
                if w == v:
                    total += self.keywordScores[i]
        return total


    def getQuery(self):
        return self.queryTemplate

    def getAnswer(self, results):
        return self.answerTemplate.format(results);


####################
##  Class Filter  ##
####################

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
        obj = Question(key, value[0], value[1], value[2][0], value[3][0])
        questionList.append(obj)

                    
init()
                

########################
##  Error Definition  ##
########################
class BotError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
    def __str__(self):
        return repr(self.code)


###################################
##  Returns the matched question ##
###################################
def matchQuestion(words):
    max = 0
    question = questionList[0]
    
    for q in questionList :
        score = q.calScore(words)
        if score > max:
            max = score
            question = q
    if(max <=0):
       raise BotError('ERROR-1001', 'Keywords didnot match any predefined category')  
    else:
       return question




#####################
##  compose query  ##
#####################

def compose_query(string):
    query=["select"]
    keywords=keyword(string)
    
    question = matchQuestion(keywords);
    query.append(question.queryTemplate)
    
    filt_list=[]
    
    filt_list.append(parse_category(keywords))
    filt_list.append(parse_institution(keywords))
    filt_list.append(parse_card(keywords))
    filt_list.append(parse_accounttype(keywords))
    filt_list.append(parse_date(string))
    filt=" and ".join(filter(None,filt_list))
    
    if filt!='':
        query.append(" where ")
        query.append(filt)
    
    query.append(";")
    result = " ".join(query)
    return(result, question)




########################################
##  connect to database query result  ##
########################################

def connect():
    """ Connect to MySQL database """
 
    try:
        conn = mysql.connector.connect(host='localhost',
                                       database='innovation',
                                       user='root',
                                       password='admin')
        if conn.is_connected():
            #print('Connected to MySQL database')
            cursor = conn.cursor()
            result = compose_query(q_from_user)

            #print "executing query: {}".format(query)
            cursor.execute(result[0])
            row = cursor.fetchone()
 
            while row is not None:
                print result[1].getAnswer(row[0]);
                return row[0]
 
    except Error as e:
        print(e)
 
    else: 
       conn.close()
 

connect()
