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
                    clear_cache)
from mnleg import (getSessionNames,getBillNames,getBillInfo,
                    getCurrentLegislators,getLegislatorByID,
                    getLegislatorByDistrict,getAllDistrictsByID,
                    getAllCommittees,getCommitteeById,
                    getAllEvents,getEventById,
                    getAllDistricts,getDistrictById)
from models import User

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

main_page="front.html"
sessions_page="mnleg-sessions.html"
bills_page="mnleg-bills.html"
bill_info_page="mnleg-bill-info.html"
current_legislators_page="mnleg-current-legislators.html"
all_committees_page="mnleg-current-committees.html"
committee_page="mnleg-committee.html"
all_events_page="mnleg-events-page.html"
event_page="mnleg-event.html"
legislator_info_page="mnleg-legislator-info.html"
all_districts_page="mnleg-districts-page.html"
district_page="mnleg-district-gmap.html"
signup_page="signup.html"
login_page="login.html"
thankyou_page="thankyou.html"

sign_up_subject="Email from mnleg info site"
sign_up_body="A new person has signed up for the site, their information is "


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def render_signup_email_body(user,email,user_ip):
	return sign_up_body+"\n"+"Username: "+user+"\n"+"Email: "+email+"/n"+"IP: "+user_ip

class GenericHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

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
    	if self.user:
    		params['loggedin_user']=self.user.name
        else:
            params['loggedin_user']="Guest"
    	return params

    def initialize(self,*a,**kw):
        webapp2.RequestHandler.initialize(self,*a,**kw)
        uid=self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

class MainHandler(GenericHandler):
    def get(self):
        params=self.check_login("/")
        self.render(main_page, **params)

class SessionsHandler(GenericHandler):
    def get(self):
        params=self.check_login('/bills')
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            params["sessions"]=getSessionNames()
            self.render(sessions_page, **params)

class BillsHandler(GenericHandler):
    def get(self,path):
        params=self.check_login(path)
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            params['bills']=getBillNames(path)
            self.render(bills_page, **params)

class BillInfoHandler(GenericHandler):
    def get(self,session,bill):
        params=self.check_login(session+'/'+bill)
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            params['bill_info']=getBillInfo(bill,session)
            self.render(bill_info_page, **params)

class LegislatureHandler(GenericHandler):
    def get(self):
        params=self.check_login('legislators')
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            params['legislators']=getCurrentLegislators()
            self.render(current_legislators_page, **params)

class LegislatorHandler(GenericHandler):
    def get(self,leg_id):
        params=self.check_login('legislators/'+leg_id)
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            params['legislator']=getLegislatorByID(leg_id)
            self.render(legislator_info_page, **params)

class AllCommitteesHandler(GenericHandler):
    def get(self):
        params=self.check_login('committees')
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            params['committees']=getAllCommittees()
            self.render(all_committees_page, **params)

class CommitteeHandler(GenericHandler):
    def get(self,com_id):
        params=self.check_login('committees/'+com_id)
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            params['committee']=getCommitteeById(com_id)
            self.render(committee_page, **params)

class AllEventsHandler(GenericHandler):
    def get(self):
        params=self.check_login('events')
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            params['events']=getAllEvents()
            self.render(all_events_page, **params)

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
            params['districts']=getAllDistricts()
            #params['districts']=getAllDistrictsByID()
            #params['district_map']='True'
            self.render(all_districts_page, **params)

class DistrictHandler(GenericHandler):
    def get(self,district_id):
        params=self.check_login('districts/'+district_id)
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            data=getDistrictById(district_id)
            params['district_num']=data['name']
            params['leg_first']=data['legislator'][0]['first_name']
            params['leg_last']=data['legislator'][0]['last_name']
            params['leg_id']=data['legislator'][0]['leg_id']
            params['img_url']=data['legislator'][0]['photo_url']
            params['party']=data['legislator'][0]['party']
            params['chamber']=data['legislator'][0]['chamber']
            params['district_map']='True'
            params['sw_lat']=data['bbox'][0][0]
            params['sw_lon']=data['bbox'][0][1]
            params['ne_lat']=data['bbox'][1][0]
            params['ne_lon']=data['bbox'][1][1]
            params['lat']=data['region']['center_lat']
            params['lon']=data['region']['center_lon']
            params['coords']=data['shape'][0][0]
            params['district']=data
            self.render(district_page, **params)

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


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/bills/?', SessionsHandler),
    ('/bills/([0-9A-Za-z- %]+)/?', BillsHandler),
    ('/bills/([0-9A-Za-z- %]+)/([H|S][A-Z][ |%][0-9]+)/?', BillInfoHandler),
    ('/legislators/?', LegislatureHandler),
    ('/legislators/(MNL[0-9]+)/?', LegislatorHandler),
    ('/committees/?', AllCommitteesHandler),
    ('/committees/(MNC[0-9]+)/?', CommitteeHandler),
    ('/events/?', AllEventsHandler),
    ('/events/(MNE[0-9]+)/?', EventHandler),
    ('/districts/?', AllDistrictsHandler),
    ('/districts/(sld[l|u]/mn-[0-9]+[a|b]?)/?', DistrictHandler),
    ('/thankyou/?', ThankYouPage),
    ('/signup/?', SignupPage),
    ('/login/?', LoginPage),
    ('/logout/?', LogoutPage),
    ('/clearcache/?', ClearCachePage),
], debug=True)
