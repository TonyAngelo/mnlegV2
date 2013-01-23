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
                    clear_cache,getFromCache,putInCache,getBillText)
from mnleg import (getSessionNames,getBillNames,getBillById,
                    getCurrentLegislators,getLegislatorByID,
                    getLegislatorByDistrict,getAllDistrictsByID,
                    getAllCommittees,getCommitteeById,
                    getAllEvents,getEventById,getCurrentBills,
                    getAllDistricts,getDistrictById,
                    getBillsbyAuthor,getBillsbyKeyword,
                    getMNHouseSessionDaily,getTownhallFeed,)
from elections import (getHPVIbyChamber,get2012ElectionResultsbyChamber,
                    get2012ElectionResultsbyDistrict,)
from models import User

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True,
                               extensions=['jinja2.ext.autoescape'])

main_page="front.html"
sessions_page="mnleg-sessions.html"
bills_page="mnleg-bills.html"
bills_search_page="mnleg-bills-search.html"
bills_search_results_page="mnleg-bills-search-results.html"
bill_info_page="mnleg-bill-info.html"
current_legislators_page="mnleg-current-legislators.html"
all_committees_page="mnleg-current-committees.html"
committee_page="mnleg-committee.html"
all_events_page="mnleg-events-page.html"
event_page="mnleg-event.html"
legislator_info_page="mnleg-legislator-info.html"
all_districts_page="mnleg-districts-gmap-page.html"
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

def get_chamber_name(chamber):
    if chamber=="House":
        body='lower'
    else:
        body='upper'
    return body

def getSortValue(string):
    result=True
    if string=='asc':
        result=False
    return result

class GenericHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def districts_render(self, chamber, **kw):
        page=self.render_str(all_districts_page, **kw)
        if chamber=='house':
            putInCache(chamber+'_districts_page1',page[:len(page)/2])
            putInCache(chamber+'_districts_page2',page[len(page)/2:])
        else:
            putInCache(chamber+'_districts_page',page)
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
    	if self.user:
    		params['loggedin_user']=self.user.name
        else:
            params['loggedin_user']="Guest"
    	return params

    def initialize(self,*a,**kw):
        webapp2.RequestHandler.initialize(self,*a,**kw)
        uid=self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

# class JPEGHandler(webapp2.RequestHandler):
#     def write_image(self,image):
#         self.response.headers['Content-Type'] = 'image/jpeg'
#         self.response.out.write(image)

# class Image(JPEGHandler):
#     def get(self,img_id):
#         p = getFromCache('leg_photo_'+img_id)
#         if p:
#             self.write_image(p.photo)
#         else:
#             p = LegislatorPhoto.by_leg_id(img_id)
#             if p:
#                 putInCache('leg_photo_'+img_id,p,0)
#                 self.write_image(p.photo)
#             else:
#                 l=getLegislatorByID(img_id)
#                 if l:
#                     url=l['photo_url']
#                     p=LegislatorPhoto.create_photo(img_id,url)
#                     p.put()
#                     putInCache('leg_photo_'+img_id,p,0)
#                     self.write_image(p.photo)
#                 else:
#                     self.error(404)

# class Thumbnail(JPEGHandler):
#     def get(self,img_id):
#         t = getFromCache('leg_photo_thumb_'+img_id)
#         if t:
#             self.write_image(t)
#         else:
#             t = LegislatorPhoto.get_thumbnail(img_id)
#             if t:
#                 putInCache('leg_photo_thumb_'+img_id,t,0)
#                 self.write_image(t)
#             else:
#                 l=getLegislatorByID(img_id)
#                 if l:
#                     url=l['photo_url']
#                     p=LegislatorPhoto.create_photo(img_id,url)
#                     p.put()
#                     putInCache('leg_photo_'+img_id,p,0)
#                     t = p.get_thumbnail(img_id)
#                     putInCache('leg_photo_thumb_'+img_id,t,0)
#                     self.write_image(t)
#                 else:
#                     self.error(404)

class MainHandler(GenericHandler):
    def get(self):
        params=self.check_login("/")
        params['house_daily_title'],params['house_daily_items'] = getMNHouseSessionDaily()
        params['current_bills']=getCurrentBills()
        params['gop_townhalls_title'],params['gop_townhalls'] = getTownhallFeed('gop')
        params['dfl_townhalls_title'],params['dfl_townhalls'] = getTownhallFeed('dfl')
        self.render(main_page, **params)

class SessionsHandler(GenericHandler):
    def get(self):
        params=self.check_login('/bills')
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            keyword=self.request.get("k")
            if keyword:
                sort=self.request.get("s")
                s=getSortValue(sort)
                params['keyword']=self.request.get("keyword")
                params['bills']=getBillsbyKeyword(keyword,s)
                self.render(bills_search_results_page, **params)
            else:
                params["sessions"],params["details"]=getSessionNames()
                params['legislators']=getCurrentLegislators()
                params['search_page']="True"
                self.render(bills_search_page, **params)

    def post(self):
        params={}
        submit=self.request.get("submit")
        if submit=='Search by Bill':
            bill=self.request.get("bill")
            session=self.request.get("session")
            params['bill_info']=getBillById(bill,session)
            self.render(bill_info_page, **params)
        elif submit=='Search by Keyword':
            params['keyword']=self.request.get("keyword")
            params['bills']=getBillsbyKeyword(params['keyword'])
            self.render(bills_search_results_page, **params)
        else:
            params['author']=self.request.get("leg")
            params['bills']=getBillsbyAuthor(params['author'])
            self.render(bills_search_results_page, **params)
        
class BillsHandler(GenericHandler):
    def get(self,path):
        params=self.check_login(path)
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            sort=self.request.get('s')
            d=getSortValue(sort)
            params['bills']=getBillNames(path,d)
            self.render(bills_page, **params)

class BillInfoHandler(GenericHandler):
    def get(self,session,bill):
        params=self.check_login(session+'/'+bill)
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            params['bill_info']=getBillById(bill,session)
            url=params['bill_info']['versions'][-1]['url']
            params['bill_text']=getBillText(url)
            self.render(bill_info_page, **params)

class LegislatureHandler(GenericHandler):
    def get(self):
        params=self.check_login('legislators')
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            params['chamber']='upper'
            params['chamber_name']="Senate"
            if self.request.get("q")=="house":
                params['chamber']='lower'
                params['chamber_name']='House'
            params['legislators']=getCurrentLegislators()
            params['search_page']="True"
            self.render(current_legislators_page, **params)

    def post(self): # for handling leg searches
        params={}
        leg_id=self.request.get("leg")
        params['legislator']=getLegislatorByID(leg_id)
        params['bills']=getBillsbyAuthor(leg_id)
        districts=getAllDistricts()
        for d in districts:
            if d['name']==params['legislator']['district']:
                params['boundary_id']=d['boundary_id']
        self.render(legislator_info_page, **params)

class LegislatorHandler(GenericHandler):
    def get(self,leg_id):
        params=self.check_login('legislators/'+leg_id)
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            params['legislator']=getLegislatorByID(leg_id)
            districts=getAllDistricts()
            if params['legislator']['active']:
                params['bills']=getBillsbyAuthor(leg_id)
                for d in districts:
                    if d['name']==params['legislator']['district']:
                        params['boundary_id']=d['boundary_id']
            else:
                params['bills']=getBillsbyAuthor(leg_id,'all')
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
            params['committee'],params['meetings']=getCommitteeById(com_id)
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
        page=''
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            chamber=self.request.get("q")
            if chamber=="house":
                params['district_map']='lower'
                p1=getFromCache(chamber+'_districts_page1')
                p2=getFromCache(chamber+'_districts_page2')
                if p1 and p2:
                    page=p1+p2
            else:
                params['district_map']='upper'
                page=getFromCache(chamber+'_districts_page')
            if not page:
                params['districts']=getAllDistrictsByID(params['district_map'])
                params['hpvi']=getHPVIbyChamber(params['district_map'])
                self.districts_render(chamber, **params)
            else:
                self.write(page)

class DistrictHandler(GenericHandler):
    def get(self,district_id):
        params=self.check_login('districts/'+district_id)
        if 'loggedin_user' not in params:
            self.redirect('/signup')
        else:
            data=getDistrictById(district_id)
            params['data']=data
            params['district_map']='True'
            params['leg_results']=get2012ElectionResultsbyDistrict(data['name'],data['chamber'])
            params['hpvi']=getHPVIbyChamber(data['chamber'])
            self.render(district_page, **params)

# class ElectionsHandler(GenericHandler):
#     def get(self):
#         #r=get2012ElectionResultsbyChamber('upper')
#         r=get2012ElectionResultsbyDistrict('49','upper')
#         self.write(r[0][1])
#         self.write('<br>')
#         self.write('Precincts: '+r[0][2])
#         self.write('<br>')
#         self.write("Total Votes: "+r[0][3])
#         self.write('<br>')
#         self.write('<br>')
#         for i in r:
#             self.write(i[4]+" ("+i[5]+") "+i[6]+'%')
#             self.write('<br>')


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
    # ('/photos/(MNL[0-9]+)/?', Image),
    # ('/thumbs/(MNL[0-9]+)/?', Thumbnail),
    # ('/elections/?', ElectionsHandler),
    ('/bills/([0-9A-Za-z- %]+)/?', BillsHandler),
    ('/bills/([0-9A-Za-z- %]+)/([H|S][A-Z][ |%][0-9]+)/?', BillInfoHandler),
    # ('/legislators/?((?:senators/?)|(?:representatives/?))?', LegislatureHandler),
    # ('/legislators/((?:senators)|(?:representatives))/(MNL[0-9]+)/?', LegislatorHandler),
    ('/legislators/?', LegislatureHandler),
    ('/legislators/(MNL[0-9]+)/?', LegislatorHandler),
    ('/committees/?', AllCommitteesHandler),
    ('/committees/(MNC[0-9]+)/?', CommitteeHandler),
    ('/events/?', AllEventsHandler),
    ('/events/(MNE[0-9]+)/?', EventHandler),
    ('/districts/?', AllDistrictsHandler),
    ('/districts/(sld[l|u]/mn-[0-9]+[a|b]?)/?', DistrictHandler),
    # ('/districts/?((?:senate/?)|(?:house/?))?', AllDistrictsHandler),
    # ('/districts/((?:senate)|(?:house))/(sld[l|u]/mn-[0-9]+[a|b]?)/?', DistrictHandler),
    ('/thankyou/?', ThankYouPage),
    ('/signup/?', SignupPage),
    ('/login/?', LoginPage),
    ('/logout/?', LogoutPage),
    ('/clearcache/?', ClearCachePage),
], debug=True)
