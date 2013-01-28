import hmac
import hashlib
import string
import random
import cgi
import re
import urllib2
import time
import datetime
from xml.dom import minidom
from google.appengine.api import memcache
from google.appengine.api import images
from bs4 import BeautifulSoup

user_re=re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
pass_re=re.compile(r"^.{3,20}$")
email_re=re.compile(r"^[\S]+@[\S]+\.[\S]+$")

var_re=re.compile(r'<var>[0-9]+\.[0-9]+</var>')
markup_id_re=re.compile(r'<a id="pl\.[0-9]+\.[0-9]+"></a>')
anchor_re=re.compile(r'<a id="bill[0-9.]+"></a>')

SECRET = 'somesecretshityo'
IP_URL="http://api.hostip.info/?ip="

def resize_image(image,width=0,height=0):
    return images.resize(image, width, height)

def convertDateToTimeStamp(date):
    date=substitute_char(date,'-','')
    date=substitute_char(date,':','')
    try:
        d=datetime.datetime.strptime(date, '%Y%m%d %H%M%S').date()
        t=int(time.mktime(d.timetuple()))
        return str(t)+'000'
    except Exception:
        return None

def convertDateTimeStringtoDateTime(date):
    try:
        d = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        return d
    except Exception:
        return None

def convertCommitteeDateStringtoDate(time_string):
    try:
        t = time.strptime(time_string,'%B %d, %Y %I:%M %p')
        return t
    except Exception:
        return None

def getMonthNumberFromString(s):
    return time.strptime(s,'%B').tm_mon

def getTodaysDate():
    return datetime.date.today()

def offsetDatebyDays(date,days):
    z=datetime.timedelta(days=days)
    return date-z

def getCurrentBillsDateString():
    d=offsetDatebyDays(getTodaysDate(),4)
    return str(d.year)+"-"+str(d.month)+"-"+str(d.day)

def getCommitteeMeetings(url):
    response=get_contents_of_url(url)
    if response!=None:
        soup=BeautifulSoup(response)
        meeting_text = soup.find_all('div','leg_col1of3-Last')
        if meeting_text[0]:
            return meeting_text[0]
    return None

def parseCommitteeMeetings(url):
    response=get_contents_of_url(url)
    if response!=None:
        soup=BeautifulSoup(response)
        meeting_text = soup.find_all('div','leg_col1of3-Last')
        if meeting_text[0]:
            if meeting_text[0].p.p:
                m=meeting_text[0].p.p
                return [text for text in m.stripped_strings]
            return meeting_text[0]
    return None

def getBillText(url):
    bill_page=get_contents_of_url(url)
    clean_bill=substitute_char(bill_page,var_re,'')
    clean_bill=substitute_char(clean_bill,markup_id_re,'')
    soup=BeautifulSoup(clean_bill)
    for e in soup.find_all('br'):
        e.extract()
    br = soup.new_tag('br')
    
    bill_text = soup.find_all('div','xtend')

    for e in bill_text[0]('a'):
        bill_text[0].a.insert_before(br)
        first_link = bill_text[0].a
        first_link.find_next("a")

    return bill_text[0]

def clear_cache(key):
    if key!=None:
        memcache.delete(key)
    else:
        memcache.flush_all()

def getFromCache(key):
    result=memcache.get(key)
    return result

def putInCache(key,data,time=86400):
    memcache.set(key,data,time=time)

def get_contents_of_url(url):
    try:
        content=urllib2.urlopen(url).read()
        return content
    except urllib2.HTTPError, e:
        #checksLogger.error('HTTPError = ' + str(e.code))
        return None
    except urllib2.URLError, e:
        #checksLogger.error('URLError = ' + str(e.reason))
        return None
    except Exception:
        #import traceback
        #checksLogger.error('generic exception: ' + traceback.format_exc())
        return None

def get_coords(ip):
    url=IP_URL+ip
    content=get_contents_of_url(url)

    if content:
        results=minidom.parseString(content)
        coords=results.getElementsByTagName("gml:coordinates")
        if coords and coords[0].childNodes[0].nodeValue:
            lon,lat=coords[0].childNodes[0].nodeValue.split(',')
            return db.GeoPt(lat,lon)

def substitute_char(s,char,sub):
    result = re.sub(char,sub,s)
    return result

def bill_text_remove_markup(text):
    text=substitute_char(text,var_re,'')
    return text

def check_valid_entry(entry,check):
    result=""
    if check.match(entry)!=None:
        result=entry
    return result

def make_secure_val(s):
    return "%s|%s" % (s, hmac.new(SECRET, s).hexdigest())

def check_secure_val(h):
    val=h.split('|')[0]
    if h == make_secure_val(val):
        return val

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt=make_salt()
    h=hashlib.sha256(name+pw+salt).hexdigest()
    return "%s|%s" % (h,salt)

def valid_pw(name, pw, h):
    salt=h.split('|')[1]
    return make_pw_hash(name, pw, salt)==h

def escape_html(s):
    return cgi.escape(s, quote= True)

def check_valid_signup(username,pasw,verify,email):
    have_error=False

    params=dict(username=username,
                email=email)

    if not check_valid_entry(username,user_re):
        params["user_error"]="That's not a valid username."
        have_error=True
    
    if not check_valid_entry(pasw,pass_re):
        params["verify_error"]="That's not a valid password."
        have_error=True
    elif pasw!=verify:
        params["verify_error"]="Your passwords didn't match."
        have_error=True

    if not check_valid_entry(email,email_re):
        params["email_error"]="That's not a valid email."
        have_error=True

    return have_error,params

def send_email(sender,to,subject,body):
    try:
      message = mail.EmailMessage(sender=sender,
                                  to=to,
                                  subject=subject,
                                  body=body)

      message.check_initialized()

    except mail.InvalidEmailError:
      self.handle_error('Invalid email recipient.')
      return
    except mail.MissingRecipientsError:
      self.handle_error('You must provide a recipient.')
      return
    except mail.MissingBodyError:
      self.handle_error('You must provide a mail format.')
      return

    message.send()
