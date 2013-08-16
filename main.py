#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import webapp2
import os
import jinja2
from google.appengine.api import mail
from utils import (check_secure_val,make_secure_val,check_valid_signup,escape_html,
                    clear_cache,getFromCache,putInCache,get_contents_of_url,)
from mnleg import (getSessionNames,getSessionDisplayFromName,getBillNames,getBillById,getBillText,
                    getAllLegislators,getLegislatorsByChamber,getLegislatorByID,
                    getLegislatorByDistrict,getAllDistrictsByID,
                    getAllCommittees,getCommitteeById,getCommitteesByChamber,
                    getAllEvents,getEventById,getCurrentBills,
                    getAllDistricts,getDistrictById,cronEvents,
                    getBillsbyAuthor,getBillsbyKeyword,getBillCounts,addEventsToParse,
                    addLegislatorToParse,addCommitteeToParse,addDistrictToParse,addBillCountsToParse,)
from elections import (getHPVIbyChamber,get2012ElectionResultsbyChamber,
                    get2012ElectionResultsbyDistrict,fetchDistrictDemoData)
from feeds import getMNHouseSessionDaily,getTownhallFeed
from models import User
from boto.s3.key import Key
import boto
import ConfigParser

# define template pages
main_page="front.html"
sessions_page="mnleg-sessions.html"
bills_page="mnleg-bills.html"
bills_search_page="mnleg-bills-search.html"
bills_search_results_page="mnleg-bills-search-results.html"
bill_info_page="mnleg-bill-info.html"
current_legislators_page="mnleg-current-legislators.html"
all_committees_page="mnleg-current-committees.html"
committee_page="mnleg-committee.html"
all_events_page="mnleg-events-page-calender-gcal.html"
event_page="mnleg-event.html"
parse_legislators_page="parse-leg.html"
legislator_info_page="mnleg-legislator-info.html"
districts_page="mnleg-districts-page.html"
all_districts_page="mnleg-districts-gmap-page.html"
district_page="mnleg-district-gmap.html"
signup_page="signup.html"
login_page="login.html"
thankyou_page="thankyou.html"

# misc strings
sign_up_subject="Email from mnleg info site"
sign_up_body="A new person has signed up for the site, their information is "

event_types={
    'senate':'senate',
    'house':'house',
    'other':'other',
    'all':'all',
}

# environment loader, load template from aws
class MyLoader(jinja2.BaseLoader):
    def __init__(self, path):
        self.path = path

    def get_source(self, environment, template):
        path = self.path+template
        page=get_contents_of_url(path)
        if not page:
            raise jinja2.TemplateNotFound(template)
        #mtime = os.path.getmtime(path)
        #with file(path) as f:
        source = page.decode('utf-8')
        return source, path, lambda: False #lambda: mtime == os.path.getmtime(path)

# set up jinja templates
aws_templates='https://s3.amazonaws.com/mnleginfo/templates/' # aws template location
aws_output='https://s3.amazonaws.com/mnleginfo/output/' # aws 'cache' location
jinja_env = jinja2.Environment(loader = MyLoader(aws_templates),
                               autoescape = True,
                               extensions=['jinja2.ext.autoescape'])

# misc functions
def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def connectToAWS():
    try:
        config = ConfigParser.ConfigParser()
        config.read(["etc/boto.cfg"])
        k=config.get('Credentials','aws_access_key_id')
        s=config.get('Credentials','aws_secret_access_key')
        c=boto.connect_s3(k,s)
        return c
    except:
        pass

def getAWSKey(key):
    c=connectToAWS()
    if c:
        b=c.get_bucket('mnleginfo')
        k=Key(b)
        k.key=key
        return k
    return None

def getKeyFromAWS(key):
    c=connectToAWS()
    if c:
        b=c.get_bucket('mnleginfo')
        k=b.get_key(key)
        if k:
            return k
    return None

def render_signup_email_body(user,email,user_ip):
    return sign_up_body+"\n"+"Username: "+user+"\n"+"Email: "+email+"/n"+"IP: "+user_ip

def updateBillInfoPageParams(params,bill,session,text_view):
    params['bill_info']=getBillById(bill,session)
    if text_view=='y':
        params['bill_info']['text_view']=text_view
        url=params['bill_info']['versions'][-1]['url']
        params['bill_text']=getBillText(url)
    else:
        params['bill_info']['text_view']='n'

def get_chamber_name(chamber):
    if chamber=="house":
        body='lower'
    else:
        body='upper'
    return body

def getSortValue(string):
    result=True
    if string=='asc':
        result=False
    return result

# generic page handler
class GenericHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def cache_render(self,key,template, **kw):
        page=self.render_str(template, **kw)
        putInCache(key,page)
        self.write(page)

    def districts_render(self, chamber, **kw):
        page=self.render_str(all_districts_page, **kw)
        self.write(page)

    def set_secure_cookie(self,name,val):
        cookie_val=make_secure_val(val)
        self.response.set_cookie(name, cookie_val, path="/")

    def read_secure_cookie(self,name):
        cookie_val=self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
    	user_id=str(user.key().id())
        self.set_secure_cookie('user_id',user_id)
        return user_id

    def logout(self):
        self.response.set_cookie('user_id', '', path="/")

    def check_login(self,path):
    	params=dict(path=path)
        params['loggedin_user']="Guest"
    	return params

    # def initialize(self,*a,**kw):
    #     webapp2.RequestHandler.initialize(self,*a,**kw)
    #     uid=self.read_secure_cookie('user_id')
    #     self.user = uid and User.by_id(int(uid))

# page handlers
class MainHandler(GenericHandler):
    def get(self):
        params=self.check_login("/")
        page=getFromCache('front_page')
        if not page:
            params['house_daily_items']=getMNHouseSessionDaily(5)
            params['current_bills']=getCurrentBills(5)
            bill_counts=getBillCounts()
            params['top']=bill_counts[:10]
            self.cache_render('front_page',main_page, **params)
        else:
            self.write(page)

class CronMainHandler(GenericHandler):
    def get(self):
        params=self.check_login("/cron/front")
        params['house_daily_items']=getMNHouseSessionDaily(5)
        params['current_bills']=getCurrentBills(5)
        bill_counts=getBillCounts()
        params['top']=bill_counts[:10]
        self.cache_render('front_page',main_page, **params)

class AWSMainHandler(GenericHandler):
    def get(self):
        params=self.check_login("/aws")
        c=connectToAWS()
        if c:
            self.write('<b>Connected</b><br><br>')
            buckets=c.get_all_buckets()
            self.write('Searching AWS Buckets...<br>')
            for b in buckets:
                if b.name=='mnleginfo':
                    self.write('Found "'+b.name+'" bucket!')
        else:
            self.write('<b>Not connected</b>')

class SessionsHandler(GenericHandler):
    def get(self):
        params=self.check_login('/bills')
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            keyword=self.request.get("k")
            leg=self.request.get("l")
            if keyword:
                sort=self.request.get("s")
                s=getSortValue(sort)
                params['keyword']=keyword
                params['bills']=getBillsbyKeyword(keyword,s)
                self.render(bills_search_results_page, **params)
            elif leg:
                params['goodstring']='no'
                legs=getAllLegislators()
                for l in legs:
                    if leg==l.name:
                        leg=l.leg_id
                        sort=self.request.get("s")
                        s=getSortValue(sort)
                        params['goodstring']='yes'
                        params['author']=leg
                        params['bills']=getBillsbyAuthor(params['author'],sort=s)
                        params['author_data']=getLegislatorByID(leg)
                        break
                if params['goodstring']=='no':
                    params['string']=leg
                self.render(bills_search_results_page, **params)

            else:
                page=get_contents_of_url(aws_output+'bills/front')
                if page:
                    self.write(page)
                else:
                    params["sessions"],params["details"]=getSessionNames()
                    params['legislators']=getAllLegislators()
                    params['search_page']="True"
                    self.render(bills_search_page, **params)

    def post(self):
        params={}
        submit=self.request.get("submit")
        if submit=='Search by Bill':
            bill=self.request.get("bill")
            session=self.request.get("session")
            bill=bill.upper()
            if bill.find(' ')==-1:
                bill=bill[:2]+' '+bill[2:]
            self.redirect('/bills/'+session+'/'+bill)
        elif submit=='Search by Keyword':
            keyword=self.request.get("keyword")
            self.redirect('/bills?k='+keyword)
        else:
            author=self.request.get("leg")
            self.redirect('/bills?l='+author)

class AWSSessionsHandler(GenericHandler):
    def get(self):
        params=self.check_login('/aws/bills')
        k=getKeyFromAWS('output/bills/front')
        if k==None:
            params["sessions"],params["details"]=getSessionNames()
            params['legislators']=getAllLegislators()
            params['search_page']="True"
            k = getAWSKey('output/bills/front')
            k.set_contents_from_string(render_str(bills_search_page, **params))
            k.set_acl('public-read')
        self.write(k.get_contents_as_string())
        
class BillsHandler(GenericHandler):
    def get(self,path):
        params=self.check_login(path)
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            params['chamber']='senate'
            params['chamber_name']="Senate"
            if self.request.get("q")=="house":
                params['chamber']='house'
                params['chamber_name']='House'
            sort=self.request.get('s')
            d=getSortValue(sort)
            params['bills']=getBillNames(path,d)
            params['session']=getSessionDisplayFromName(path)
            self.render(bills_page, **params)

class BillInfoHandler(GenericHandler):
    def get(self,session,bill):
        params=self.check_login(session+'/'+bill)
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            text_view=self.request.get("t")
            if bill.find(' ')==-1:
                bill=bill[:2]+' '+bill[2:]
            updateBillInfoPageParams(params,bill,session,text_view)
            self.render(bill_info_page, **params)

class ParseMainHandler(GenericHandler):
    def get(self):
        params=self.check_login('/')
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            addBillCountsToParse()

class ParseLegislatorHandler(GenericHandler):
    def get(self):
        params=self.check_login('legislators')
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            legs=getAllLegislators()
            for l in legs:
                addLegislatorToParse(l['leg_id'])

class ParseAddLegislator(GenericHandler):
    def get(self,leg_id):
        addLegislatorToParse(leg_id)
        self.redirect('/parse/legislators')

class ParseCommitteesHandler(GenericHandler):
    def get(self):
        params=self.check_login('committees')
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            coms=getAllCommittees()
            for c in coms:
                addCommitteeToParse(c['id'])

class ParseCommitteeHandler(GenericHandler):
    def get(self,com_id):
        params=self.check_login('committees')
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            addCommitteeToParse(com_id)

class ParseDistrictsHandler(GenericHandler):
    def get(self):
        params=self.check_login('districts')
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            dists=getAllDistricts()
            house_hpvi=getHPVIbyChamber('lower')
            senate_hpvi=getHPVIbyChamber('upper')
            for d in dists:
                if d['chamber']=='upper':
                    hpvi=senate_hpvi.get(d['name'])
                elif d['chamber']=='lower':
                    hpvi=house_hpvi.get(d['name'])
                addDistrictToParse(d['boundary_id'],hpvi)

class ParseEventsHandler(GenericHandler):
    def get(self,chamber):
        params=self.check_login('events')
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            addEventsToParse(chamber)

class LegislatureHandler(GenericHandler):
    def get(self):
        params=self.check_login('legislators')
        chamber=self.request.get("q")
        if chamber!="house" and chamber!="senate" and chamber:
            self.redirect('/')
        else:
            params['chamber']='upper'
            params['chamber_name']="Senate"
            if self.request.get("q")=="house":
                params['chamber']='lower'
                params['chamber_name']='House'
            page=get_contents_of_url(aws_output+'legislators/'+params['chamber'])
            if page:
                self.write(page)
            else:
                params['legislators']=getLegislatorsByChamber(params['chamber'])
                params['search_page']="True"
                self.render(current_legislators_page, **params)

    def post(self): # for handling leg searches
        params={}
        params['goodstring']='no'
        submit=self.request.get("submit")
        if submit=='Search':
            leg=self.request.get("leg")
            legs=getAllLegislators()
            for l in legs:
                if leg==l.name:
                    params['goodstring']='yes'
                    self.redirect('/legislators/'+l.leg_id)
                    break
        if params['goodstring']=='no':
            self.redirect('/legislators')

class AWSLegislatureHandler(GenericHandler):
    def get(self):
        params=self.check_login('/aws/legislators')
        chamber=self.request.get("q")
        if chamber!="house" and chamber!="senate" and chamber:
            self.redirect('/')
        else:
            params['chamber']='upper'
            params['chamber_name']="Senate"
            if self.request.get("q")=="house":
                params['chamber']='lower'
                params['chamber_name']='House'
            k=getKeyFromAWS('output/legislators/'+params['chamber'])
            if k==None:
                params['legislators']=getLegislatorsByChamber(params['chamber'])
                params['search_page']="True"
                k = getAWSKey('output/legislators/'+params['chamber'])
                k.set_contents_from_string(render_str(current_legislators_page, **params))
                k.set_acl('public-read')
            self.write(k.get_contents_as_string())

class LegislatorHandler(GenericHandler):
    def get(self,leg_id):
        params=self.check_login('legislators/'+leg_id)
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            params['legislator']=getLegislatorByID(leg_id)
            #params['legislator'].twitter=['','']
            districts=getAllDistricts()
            if params['legislator'].active:
                params['bills']=getBillsbyAuthor(leg_id)
                for d in districts:
                    if d['name']==params['legislator'].district:
                        params['boundary_id']=d['boundary_id']
            else:
                params['bills']=getBillsbyAuthor(leg_id,'all')
            self.render(legislator_info_page, **params)

class AllCommitteesHandler(GenericHandler):
    def get(self):
        params=self.check_login('committees')
        chamber=self.request.get("q")
        if chamber!="house" and chamber!="senate" and chamber:
            self.redirect('/')
        else:
            params['chamber']='upper'
            if self.request.get("q")=="house":
                params['chamber']='lower'
            page=get_contents_of_url(aws_output+'committees/'+params['chamber'])
            if page:
                self.write(page)
            else:
                params['committees']=getCommitteesByChamber(params['chamber'])
                self.render(all_committees_page, **params)

class AWSAllCommitteesHandler(GenericHandler):
    def get(self):
        params=self.check_login('aws/committees')
        chamber=self.request.get("q")
        if chamber!="house" and chamber!="senate" and chamber:
            self.redirect('/')
        else:
            params['chamber']='upper'
            if self.request.get("q")=="house":
                params['chamber']='lower'   
            k=getKeyFromAWS('output/committees/'+params['chamber'])
            if k==None:
                params['committees']=getCommitteesByChamber(params['chamber'])
                k = getAWSKey('output/committees/'+params['chamber'])
                k.set_contents_from_string(render_str(all_committees_page, **params))
                k.set_acl('public-read')
            self.write(k.get_contents_as_string())

class CommitteeHandler(GenericHandler):
    def get(self,com_id):
        params=self.check_login('committees/'+com_id)
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            params['committee']=getCommitteeById(com_id)
            if params['committee']['chamber']=='upper':
                params['chamber']='Senate'
            else:
                params['chamber']='House'
            self.render(committee_page, **params)

class AllEventsHandler(GenericHandler):
    def get(self):
        params=self.check_login('events')
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            params['events']=getAllEvents()
            self.render(all_events_page, **params)

class EventsHandler(GenericHandler):
    def get(self,events):
        params=self.check_login('events')
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            if events in event_types:
                e=getAllEvents(events)
                self.write(events+' retrived: ')
                self.write(e)
            else:
                self.redirect("/")

class CronEventsHandler(GenericHandler):
    def get(self,events):
        params['events']=getAllEvents()
        self.cache_render('events_page',all_events_page, **params)

class EventHandler(GenericHandler):
    def get(self,event_id):
        params=self.check_login('events/'+event_id)
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            params['event']=getEventById(event_id)
            self.render(event_page, **params)

class AllDistrictsHandler(GenericHandler):
    def get(self):
        params=self.check_login('districts')
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            self.redirect('/districts/senate')
            # page=get_contents_of_url(aws_output+'districts/front')
            # if page:
            #     self.write(page)
            # else:
            #     params['districts']=getAllDistricts()
            #     params['sen_hpvi']=getHPVIbyChamber('upper',True)
            #     params['house_hpvi']=getHPVIbyChamber('lower',True)
            #     params['senate']=[39,28]
            #     params['house']=[73,61]
            #     self.render(districts_page, **params)

    def post(self):
        district_id=self.request.get("districts")
        self.redirect('/districts/'+str(district_id))

class AWSAllDistrictsHandler(GenericHandler):
    def get(self):
        params=self.check_login('aws/districts')
        k=getKeyFromAWS('output/districts/front')
        if k==None:
            self.write('Page not found, uploading...<br>')
            params['districts']=getAllDistricts()
            params['sen_hpvi']=getHPVIbyChamber('upper',True)
            params['house_hpvi']=getHPVIbyChamber('lower',True)
            params['senate']=[39,28]
            params['house']=[73,61]
            k = Key(b)
            k.key = 'output/districts/front'
            k.set_contents_from_string(render_str(districts_page, **params))
            k.set_acl('public-read')
        self.write(k.get_contents_as_string())

class ChamberDistrictsHandler(GenericHandler):
    def get(self,chamber):
        params=self.check_login('districts/'+chamber)
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            page=get_contents_of_url(aws_output+'districts/'+chamber)
            if page:
                self.write(page)
            else:
                params['district_map']=get_chamber_name(chamber)
                params['districts']=getAllDistrictsByID(params['district_map'])
                self.render(all_districts_page, **params)

    def post(self,chamber):
        district_id=self.request.get("districts")
        self.redirect('/districts/'+str(district_id))

class AWSChamberDistrictsHandler(GenericHandler):
    def get(self,chamber):
        params=self.check_login('aws/districts/'+chamber)
        k=getKeyFromAWS('output/districts/'+chamber)
        if k==None:
            self.write('Page not found, uploading...<br>')
            params['district_map']=get_chamber_name(chamber)
            params['districts']=getAllDistrictsByID(params['district_map'])
            k = getAWSKey('output/districts/'+chamber)
            k.set_contents_from_string(render_str(all_districts_page, **params))
            k.set_acl('public-read')
        self.write(k.get_contents_as_string())

class DistrictHandler(GenericHandler):
    def get(self,district_id):
        params=self.check_login('districts/'+district_id)
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            # page=get_contents_of_url(aws_output+'districts/'+district_id)
            # if page:
            #     self.write(page)
            # else:
            data=getDistrictById(district_id)
            params['data']=data
            params['district_map']='True'
            self.render(district_page, **params)

class AWSDistrictHandler(GenericHandler):
    def get(self,district_id):
        params=self.check_login('aws/districts/'+district_id)
        k=getKeyFromAWS('output/districts/'+district_id)
        if k==None:
            self.write('Page not found, uploading...<br>')
            data=getDistrictById(district_id)
            params['data']=data
            params['district_map']='True'
            k = Key(b)
            k.key = 'output/districts/'+district_id
            k.set_contents_from_string(render_str(district_page, **params))
            k.set_acl('public-read')
        self.write(k.get_contents_as_string())

class AWSGetSenateDistrictsHandler(GenericHandler):
    def get(self):
        params=self.check_login('aws/get_senate_districts')
        c=connectToAWS()
        if c:
            self.write('Connected<br><br>')
            b=c.get_bucket('mnleginfo')
            r=range(67)
            #self.write(r)
            for n in r:
                district_id='sldu/mn-'+str(n+1).zfill(2)
                self.write(district_id)
                k=b.get_key('output/districts/'+district_id)
                if k:
                    self.write(' Page found<br>')
                else:
                    self.write(' Page not found, trying to upload...')
                    data=getDistrictById(district_id)
                    params['data']=data
                    params['district_map']='True'
                    k = Key(b)
                    k.key = 'output/districts/'+district_id
                    k.set_contents_from_string(render_str(district_page, **params))
                    k.set_acl('public-read')
                    self.write('uploaded<br>')

class AWSGetHouseDistrictsHandler(GenericHandler):
    def get(self,l):
        params=self.check_login('aws/get_house_districts/'+l)
        c=connectToAWS()
        if c:
            self.write('Connected<br><br>')
            b=c.get_bucket('mnleginfo')
            r=range(67)
            for n in r:
                district_id='sldl/mn-'+str(n+1).zfill(2)+l
                self.write(district_id)
                k=b.get_key('output/districts/'+district_id)
                if k:
                    self.write(' Page found<br>')
                else:
                    self.write(' Page not found, trying to upload...')
                    data=getDistrictById(district_id)
                    params['data']=data
                    params['district_map']='True'
                    k = Key(b)
                    k.key = 'output/districts/'+district_id
                    k.set_contents_from_string(render_str(district_page, **params))
                    k.set_acl('public-read')
                    self.write('uploaded<br>')

class SignupPage(GenericHandler):
    def get(self):
        self.render(signup_page)

    def post(self):
        username=self.request.get("username")
        pasw=self.request.get("password")
        verify=self.request.get("verify")
        email=escape_html(self.request.get("email"))

        have_error,params=check_valid_signup(username,pasw,verify,email)

        if not have_error:
            u = User.by_name(username)
            if u:
                msg = 'That user already exists.'
                self.render(signup_page, user_error = msg)
            else:
                user_ip=self.request.remote_addr
                u = User.register(username, pasw, email, user_ip)
                u.put()
                # mail.send_mail(sender="tonypetrangelo@gmail.com",
                # 				to="tonypetrangelo@gmail.com",
                # 				subject=sign_up_subject,
                # 				body=render_signup_email_body(username,email,user_ip))
                self.login(u)
                self.redirect('/thankyou?n='+username)
        else:
            self.render(signup_page,**params)

class ThankYouPage(GenericHandler):
    def get(self):
    	params=self.check_login("/thankyou")
        n=self.request.get('n')
        params["user"]=n
        u=User.by_name(n)
        self.render(thankyou_page, **params)

class LoginPage(GenericHandler):
    def get(self):
        self.render(login_page)

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        u = User.login(username, password)
        if u:
            self.login(u)
            path=self.request.get('p')
            if path and path!="/login":
                self.redirect(path)
            else:
                self.redirect("/")
        else:
            msg = 'Invalid login'
            self.render(login_page, user=username,error = msg)

class LogoutPage(GenericHandler):
    def get(self):
        #p=self.request.get('p')
        self.logout()
        self.redirect("/")

class ClearCachePage(GenericHandler):
    def get(self):
        clear_cache(None)
        self.redirect("/")

# paths
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/cron/front/?', CronMainHandler),
    ('/cron/events/?', CronEventsHandler),
    ('/bills/?', SessionsHandler),
    ('/bills/([0-9A-Za-z- %]+)/?', BillsHandler),
    ('/bills/([0-9A-Za-z- %]+)/([H|S][A-Z][ |%]?[0-9]+)/?', BillInfoHandler),
    ('/parse/front/?', ParseMainHandler),
    ('/parse/legislators/?', ParseLegislatorHandler),
    ('/parse/committees/?', ParseCommitteesHandler),
    ('/parse/committees/(MNC[0-9]+|[0-9]+)/?', ParseCommitteeHandler),
    ('/parse/districts/?', ParseDistrictsHandler),
    # ('/parse/events/(house|senate)/?', ParseEventsHandler),
    ('/parse/legislators/(MNL[0-9]+)/?', ParseAddLegislator),
    ('/legislators/?', LegislatureHandler),
    ('/legislators/(MNL[0-9]+)/?', LegislatorHandler),
    ('/committees/?', AllCommitteesHandler),
    ('/committees/(MNC[0-9]+|[0-9]+)/?', CommitteeHandler),
    # ('/events/?', AllEventsHandler),
    # ('/events/(MNE[0-9]+)/?', EventHandler),
    ('/districts/?', AllDistrictsHandler),
    ('/districts/(house|senate)/?', ChamberDistrictsHandler),
    ('/districts/(sld[l|u]/mn-[0-9]+[a|b]?)/?', DistrictHandler),
    ('/thankyou/?', ThankYouPage),
    ('/signup/?', SignupPage),
    ('/login/?', LoginPage),
    ('/logout/?', LogoutPage),
    ('/clearcache/?', ClearCachePage),
    ('/aws/?', AWSMainHandler),
    ('/aws/bills/?', AWSSessionsHandler),
    ('/aws/legislators/?', AWSLegislatureHandler),
    ('/aws/committees/?', AWSAllCommitteesHandler),
    ('/aws/districts/(sld[l|u]/mn-[0-9]+[a|b]?)/?', AWSDistrictHandler),
    ('/aws/get_senate_districts/?', AWSGetSenateDistrictsHandler),
    ('/aws/get_house_districts/([a|b])/?', AWSGetHouseDistrictsHandler),
    ('/aws/districts/(house|senate)/?', AWSChamberDistrictsHandler),
    ('/aws/districts/?', AWSAllDistrictsHandler),
], debug=False)
