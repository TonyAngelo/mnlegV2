import hmac
import hashlib
import string
import random
import cgi
import re
import urllib2
from xml.dom import minidom
from google.appengine.api import memcache

user_re=re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
pass_re=re.compile(r"^.{3,20}$")
email_re=re.compile(r"^[\S]+@[\S]+\.[\S]+$")

SECRET = 'somesecretshityo'

IP_URL="http://api.hostip.info/?ip="
GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false"

def clear_cache(key):
    memcache.delete(key)

def getFromCache(key):
    result=memcache.get(key)
    return result

def putInCache(key,data):
    memcache.set(key,data)

def get_contents_of_url(url):
    try:
        content=urllib2.urlopen(url).read()
        return content
    except URLError:
        return None

def google_maps_img(points):
    if points:
        markers='&'.join('markers=%s,%s' % (p.lat,p.lon) for p in points)
        return GMAPS_URL+markers

def get_coords(ip):
    url=IP_URL+ip
    content=get_contents_of_url(url)

    if content:
        results=minidom.parseString(content)
        coords=results.getElementsByTagName("gml:coordinates")
        if coords and coords[0].childNodes[0].nodeValue:
            lon,lat=coords[0].childNodes[0].nodeValue.split(',')
            return db.GeoPt(lat,lon)

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
