import json
import re
from bs4 import BeautifulSoup
from utils import (get_contents_of_url,getFromCache,putInCache,cacheDance,substitute_char,
					getDateString,convertSenComMeetDateStringtoDate,
					convertDateToTimeStamp,convertDateStringtoDate,)
from elections import (getHPVIbyChamber,get2012ElectionResultsbyChamber,getHPVIbyDistrict,
                    get2012ElectionResultsbyDistrict,fetchDistrictDemoData)
from parse import Legislator,Committee,District,BillCounts,Event

time_hour_1=3600
time_hour_3=3600
time_hour_24=86400

API_KEY='4a26c19c3cae4f6c843c3e7816475fae'
base_url='http://openstates.org/api/v1/'
apikey_url="apikey="
mn_senate_base='http://www.senate.leg.state.mn.us'

var_re=re.compile(r'<var>[0-9]+\.[0-9]+</var>')
markup_id_re=re.compile(r'<a id="pl\.[0-9]+\.[0-9]+"></a>')
#anchor_re=re.compile(r'<a id="bill[0-9.]+"></a>')

day_of_week={'SUNDAY,':'SUNDAY,',
             'MONDAY,':'MONDAY,',
             'TUESDAY,':'TUESDAY,',
             'WEDNESDAY,':'WEDNESDAY,',
             'THURSDAY,':'THURSDAY,',
             'FRIDAY,':'FRIDAY,',
             'SATURDAY,':'SATURDAY,',}

#########################################################################################
##### sunlight fundation API functions #####                                        #####
#########################################################################################

def getMNLegAllDistricts():
	#http://openstates.org/api/v1/districts/mn/?apikey=4a26c19c3cae4f6c843c3e7816475fae
	url=base_url+'districts/mn/?'+apikey_url+API_KEY
	return sendGetRequest(url)

def getLegislatorByDistrict(district):
	url=base_url+'legislators/?state=mn&district='+district+'&'+apikey_url+API_KEY
	return sendGetRequest(url)

def getMNLegDistrictById(district_id):
	#http://openstates.org/api/v1/districts/boundary/sldu/mn-11/?apikey=4a26c19c3cae4f6c843c3e7816475fae
	url=base_url+'districts/boundary/'+district_id+'/?'+apikey_url+API_KEY
	return sendGetRequest(url)

def getMNLegAllEvents():
	#http://openstates.org/api/v1/events/?state=mn&apikey=4a26c19c3cae4f6c843c3e7816475fae
	url=base_url+'events/?state=mn&'+apikey_url+API_KEY
	return sendGetRequest(url)

def getMNLegEventById(event_id):
	#http://openstates.org/api/v1/events/MNE00000095/?apikey=4a26c19c3cae4f6c843c3e7816475fae
	url=base_url+'events/'+event_id+'/?'+apikey_url+API_KEY
	return sendGetRequest(url)

def getMNLegAllCommittees():
	#http://openstates.org/api/v1/committees/?state=mn&apikey=4a26c19c3cae4f6c843c3e7816475fae
	url=base_url+'committees/?state=mn&'+apikey_url+API_KEY
	return sendGetRequest(url)

def getMNLegCommitteesByChamber(chamber):
	#http://openstates.org/api/v1/committees/?state=mn&chamber=upper&apikey=4a26c19c3cae4f6c843c3e7816475fae
	url=base_url+'committees/?state=mn&chamber='+chamber+'&'+apikey_url+API_KEY
	return sendGetRequest(url)

def getMNLegCommitteeById(com_id):
	#http://openstates.org/api/v1/committees/MNC000038/?apikey=4a26c19c3cae4f6c843c3e7816475fae
	url=base_url+'committees/'+com_id+'/?'+apikey_url+API_KEY
	return sendGetRequest(url)

def getMNLegislatorById(leg_id):
	#http://openstates.org/api/v1/legislators/MNL000105/?apikey=4a26c19c3cae4f6c843c3e7816475fae
	url=base_url+'legislators/'+leg_id+'/?'+apikey_url+API_KEY
	return sendGetRequest(url)

def getMNLegislatorByActive():
	#http://openstates.org/api/v1/legislators/?state=mn&apikey=4a26c19c3cae4f6c843c3e7816475fae
	url=base_url+'legislators/?state=mn&'+apikey_url+API_KEY
	return sendGetRequest(url)

def getMNLegMetaData():
	#http://openstates.org/api/v1/metadata/mn/?apikey=4a26c19c3cae4f6c843c3e7816475fae
	url=base_url+'metadata/mn/?'+apikey_url+API_KEY
	return sendGetRequest(url)

def getMNLegBillsbyQuery(query):
	url=base_url+'bills/?state=mn&'+query+apikey_url+API_KEY
	return sendGetRequest(url)

def getMNLegBillsbyAuthor(author,session='session'):
	#http://openstates.org/api/v1/bills/?sponsor_id=MNL000044&state=mn&search_window=session&apikey=4a26c19c3cae4f6c843c3e7816475fae
	url=base_url+'bills/?state=mn&search_window='+session+'&sponsor_id='+author+'&'+apikey_url+API_KEY
	return sendGetRequest(url)

def getMNLegBillsCurrent(n=10):
	#http://openstates.org/api/v1/bills/?per_page=5&page=1&updated_since=2013-1-15&state=mn&search_window=session&apikey=4a26c19c3cae4f6c843c3e7816475fae
	d=getDateString()
	url=base_url+'bills/?per_page='+str(n)+'&page=1&updated_since='+d+'&state=mn&search_window=session&apikey=4a26c19c3cae4f6c843c3e7816475fae'
	return sendGetRequest(url)

def getMNLegBillsbyKeyword(keyword):
	#http://openstates.org/api/v1/bills/?q=smoking&apikey=4a26c19c3cae4f6c843c3e7816475fae
	url=base_url+'bills/?state=mn&q='+keyword+'&'+apikey_url+API_KEY
	return sendGetRequest(url)

def getMNLegBillsbySession(session,per_page=2000,page=1):
	#http://openstates.org/api/v1/bills/?state=mn&search_window=session&apikey=4a26c19c3cae4f6c843c3e7816475fae
	session_url='state=mn&search_window=session:'+session+'&'
	url=base_url+'bills/?'+session_url+'&per_page='+str(per_page)+'&page='+str(page)+'&'+apikey_url+API_KEY
	return sendGetRequest(url)

def getMNLegBillInfobyId(bill,session):
	#http://openstates.org/api/v1/bills/mn/2013-2014/SF 18?apikey=4a26c19c3cae4f6c843c3e7816475fae
	url=base_url+'bills/mn/'+session+'/'+bill+'?'+apikey_url+API_KEY
	return sendGetRequest(url)

def sendGetRequest(url):
	url=substitute_char(url,' ','%20')
	response = get_contents_of_url(url)
	if response:
		data=json.loads(response)
		return data
	else:
		return None

#########################################################################################
##### misc helper functions #####                                                   #####
#########################################################################################

def getBillCountsByLegislator():
	bill_counts=[]
	data=cacheDance('legislators',getMNLegislatorByActive, None)
	for d in data:
		b=getMNLegBillsbyAuthor(d['leg_id'])
		bill_counts.append((len(b),(d['leg_id'],d['first_name'],d['last_name'],d['party'])))
	bills=sorted(bill_counts, key=lambda tup: tup[0],reverse=True)
	return bills

def sortBillsByDate(data,sort):
	bills=[]
	if data:
		for d in data:
			bills.append(d)
		b=sorted(bills, key=lambda bills: bills['updated_at'] ,reverse=sort)
		return b
	return bills

def bill_text_remove_markup(text):
    text=substitute_char(text,var_re,'')
    return text

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

def getAllEventsAsEvents(data):
	events=[]
	if data:
		for d in data:
			event={
			'start':d['when'][:4]+'-'+d['when'][5:7]+'-'+d['when'][8:10]+' '+d['when'][11:13]+':'+d['when'][14:16]+':00',
	 		'type':d['type'],
	 		'title':d['description'],
	 		'description':d['description'],
	 		'url':'/events/'+d['id']}
			events.append(event)
	return events

def getSenateCommitteeSchedule(url):
    pass

def getSenateCommitteeAV(url):
    pass

def getSenateCommittees():
    response=get_contents_of_url(mn_senate_base+'/committees/')
    if response!=None:
        soup=BeautifulSoup(response)
        info = soup.find_all('div','HRDFlyer')
        links = links=info[0].find_all('a')
        name=''
        committees=[]
        count=0
        for l in links:
            if l.text.find('Members')>=0:
                members=l['href']
            elif l.text.find('Schedule')>=0:
                schedule=l['href']
            elif l.text.find('Audio/Video')>=0:
                av=l['href']
                committee={'committee':name,
                            'chamber':'upper',
                            'id': getCommitteeIDFromURL(l['href']),
                            'members_url':members,
                            'meetings_url':schedule,
                            'media_url':av,}
                committees.append(committee)
            else:
                if l.text[1:].find('     ')>0:
                    name=l.text[1:l.text[1:].find('     ')]
                else:
                    name=l.text[1:]
        return committees
    else:
        return None

def makeCommitteeDict(title,members,meetings,chamber):
	committee={'committee':title,
                'members':members,
                'meetings':meetings,
                'chamber':chamber,}
	return committee

def getSenateCommitteeByID(com_id):
	url=mn_senate_base+'/committees/committee_members.php?ls=&cmte_id='+com_id
	title,members,meetings=getSenateCommitteeMembers(url)
	return makeCommitteeDict(title,members,meetings)

def getSenateCommitteeMeetingsByID(com_id):
	url=mn_senate_base+'/committees/committee_members.php?cmte_id='+com_id
	response=get_contents_of_url(url)
	if response!=None:
		soup=BeautifulSoup(response)
		meetings = soup.find('div','leg_Col1of4-Last HRDFlyer')
		return meetings
	return None

def getLegislatorIDByName(name):
    legs=getCurrentLegislators()
    for l in legs:
        if name.find(l['first_name'][0])>=0 and name.find(l['last_name'])>=0:
            return l['id']

def getSenateCommitteeMembers(url):
    response=get_contents_of_url(url)
    if response!=None:
        soup=BeautifulSoup(response)
        title = soup.find('div','leg_PageContent').h2.text
        title = title[:title.find('Membership')-1]
        info = soup.find_all('div','leg_Col3of4-First HRDFlyer')
        meetings = soup.find('div','leg_Col1of4-Last HRDFlyer')
        items=info[0].find_all('td')
        results=[]
        for i in items:
            t = [text for text in i.stripped_strings]
            if t:
                if t[0].find(':')>0:
                    m={'name': t[1][:t[1].find(' (')],
                        'role': t[0][:-1],
                        'leg_id': getLegislatorIDByName(t[1][:t[1].find(' (')]),}
                else:
                    m={'name': t[0][:t[0].find(' (')],
                        'role': 'member',
                        'leg_id': getLegislatorIDByName(t[0][:t[0].find(' (')]),}
                results.append(m)
        return title, results, meetings

def getCommitteeDictByID(com_id):
	# data=getMNLegCommitteeById(com_id)
	com=Committee.get_by_id(com_id)
	for c in com:
		if c.chamber=='lower':
			meetings=getHouseCommitteeMeetings(c.com_url[0]['url'])
		elif c.chamber=='upper':
			meetings=getSenateCommitteeMeetingsByID(getCommitteeIDFromURL(c.com_url[0]['url']))
		return makeCommitteeDict(c.name,c.members,meetings,c.chamber)

	# if data['chamber']=='lower':
	# 	meetings=getHouseCommitteeMeetings(data['sources'][0]['url'])
	# elif data['chamber']=='upper':
	# 	meetings=getSenateCommitteeMeetingsByID(getCommitteeIDFromURL(data['sources'][0]['url']))
	# return makeCommitteeDict(data['committee'],data['members'],meetings,data['chamber'])

def getHouseMeetingByID(com_id):
	data=getMNLegCommitteeById(com_id)
	meetings=parseHouseCommitteeMeetings(data['sources'][0]['url'])
	return meetings

def getHouseCommitteeMeetings(url):
    response=get_contents_of_url(url)
    if response!=None:
        soup=BeautifulSoup(response)
        meeting_text = soup.find_all('div','leg_col1of3-Last')
        if meeting_text[0]:
            return meeting_text[0]
    return None

def parseHouseCommitteeMeetings(url):
    response=get_contents_of_url(url)
    if response!=None:
        soup=BeautifulSoup(response)
        meeting_text = soup.find_all('div','leg_col1of3-Last')
        if meeting_text:
            if meeting_text[0].p.p:
                m=meeting_text[0].p.p
                return [text for text in m.stripped_strings]
    return None

def getCommitteeIDFromURL(url):
    #http://www.senate.mn/committees/committee_media_list.php?cmte_id=1002
    if url.find('cmte_id=')>0:
    	url=url[url.find('cmte_id=')+len('cmte_id='):]
    return url

def getSenComNameFromID(com_id):
	url=mn_senate_base+'/committees/committee_members.php?cmte_id='+com_id
	title,members,meetings=getSenateCommitteeMembers(url)
	return title

def createEventDateString(f):
	month=checkDateLength(str(f.tm_mon))
	day=checkDateLength(str(f.tm_mday))
	minute=checkDateLength(str(f.tm_min))
	dateString=str(f.tm_year)+'-'+month+'-'+day+' '+str(f.tm_hour)+':'+minute+':00'
	return dateString

def getHouseMeetingAsEvent(title,date,com_id):
	event={}
	f=convertDateStringtoDate(date)
	#dateString=createEventDateString(f)
	if f!=None:
		month=checkDateLength(str(f.tm_mon))
		day=checkDateLength(str(f.tm_mday))
		minute=checkDateLength(str(f.tm_min))
		dateString=str(f.tm_year)+'-'+month+'-'+day+' '+str(f.tm_hour)+':'+minute+':00'
		event['title']=title
		event['start']=dateString
		event['type']='house meeting'
		event['url']='/committees/'+com_id
		#event['key']=title+dateString
		return event
	else:
		return None

def checkDateLength(date):
	if len(date)==1:
		date='0'+date
	return date

def getSenateCommitteeMeetingInfo(url):
	results=[]
	response=get_contents_of_url(url)
	if response!=None:
		soup=BeautifulSoup(response)
		meetings = soup.find('div','leg_Col3of4')
		meet=meetings.table
		m=meet.find_all('table')
		for i in m:
			results.append([text for text in i.stripped_strings])
	return results

def getSenateMeetingAsEvent(title,date,com_id):
	event={}
	f=convertSenComMeetDateStringtoDate(date.text)
	if f!=None:
		month=checkDateLength(str(f.tm_mon))
		day=checkDateLength(str(f.tm_mday))
		minute=checkDateLength(str(f.tm_min))
		dateString=str(f.tm_year)+'-'+month+'-'+day+' '+str(f.tm_hour)+':'+minute+':00'
		event['title']=title
		event['start']=dateString
		event['type']='senate meeting'
		event['url']='committees/'+com_id
		#event['key']=title+date
		#event['agenda']=info[-1][-1]
		return event
	else:
		return None

def getAllSenateCommitteeMeetings():
	meetings=[]
	coms=getSenateCommittees()
	if coms:
		for c in coms:
			meet = getSenateCommitteeMeetingsByID(c['id'])
			meetings.append((c['id'],meet))
	return meetings

def getAllHouseCommitteeMeetings():
	meetings=[]
	coms=getMNLegAllCommittees()
	if coms:
		for c in coms:
			meet=getHouseMeetingByID(c['id'])
			meetings.append((c['id'],meet))
	return meetings

def getAllOtherEventsAsEvents():
	# events=getFromCache('all_other_events')
	# if not events:
	data=getMNLegAllEvents()
	events=getAllEventsAsEvents(data)
		#putInCache('all_other_events',events,time_hour_24)
	return events

def getAllSenateCommitteeMeetingsAsEvents():
	meetings=[]
	coms=Committee.Query.all().eq(chamber='upper')
	if coms:
		for c in coms:
			url=c.com_url[0]['url']
			meet = getSenateCommitteeMeetingsByID(getCommitteeIDFromURL(url))
			links = meet.find_all('a')
			if links:
				for l in links:
					params = getSenateMeetingAsEvent(c.name,l,c.com_id)
					if params:
						key=c.name+l.text
						event = Event.get_by_key(key)
						if event.count()>0:
							for e in event:
								e.title=params['title']
								e.start=params['start']
								e.type=params['type']
								e.url=params['url']
								e.save()
						else:
							# params = getSenateMeetingAsEvent(c.name,l,c.com_id)
							params['key']=key
							event = Event(**params)
							event.save()

def getAllHouseCommitteeMeetingsAsEvents():
	meetings=[]
	count=0
	title_count=-1
	room_count=-1
	chair_count=-1
	coms=Committee.Query.all().eq(chamber='lower')
	if coms:
		for c in coms:
			url=c.com_url[0]['url']
			meet = getHouseMeetingByID(c.com_id)
			if meet:
				for m in meet:
					if m in day_of_week:
						count=0
						date=''
			 			time=''
			 			# title_count=-1
			 			# room_count=-1
			 			# chair_count=-1
			 			# room=''
			 			# chair=''
			 			event={}
			 		else:
			 			count+=1

			 		if count==1:
			 			date=m
			 		elif count==2:
			 			time=m
			 			params = getHouseMeetingAsEvent(c.name,date+' '+time,c.com_id)
			 			if params:
				 			key=c.name+date+' '+time
							event = Event.get_by_key(key)
							if event.count()>0:
								for e in event:
									e.title=params['title']
									e.start=params['start']
									e.type=params['type']
									e.url=params['url']
									e.save()
							else:
								params['key']=key
								event = Event(**params)
							# params = getHouseMeetingAsEvent(c.name,date+' '+time,c.com_id)
							#params['key']=key
							#event = Event(**params)
								event.save()

					# elif l=='Room:':
					# 	room_count=count+1
					# elif room_count==count:
					# 	room=l
					# elif l=='Chair:' or l=='Chairs':
					# 	chair_count=count+1
					# elif chair_count==count:
					# 	chair=l
					# elif l=='Agenda:':
					# 	title_count=count+1
					# elif title_count==count:
					# 	l=substitute_char(l,"'",'')
					# 	l=substitute_char(l,"&",'and')
					# 	if len(l)>50:
					# 		event['title']=l[:50]+'...'
					# 	else:
					# 		event['title']=l
					# 	event['description'] = 'Location: '+room+' Chair: '+chair
					# 	meetings.append(event)

#########################################################################################
##### requests from event handlers #####                                            #####
#########################################################################################

def getCurrentBills(n=10): # front page recent bills
	data = getMNLegBillsCurrent(n)
	return data
	# if data:
	# 	putInCache('Current Bills',data)

def getBillsbyKeyword(keyword,sort=True): # bills search page 
	# params={'keyword':keyword}
	# data=cacheDance('query='+keyword,getMNLegBillsbyKeyword, time_hour_24, **params)
	data=getMNLegBillsbyKeyword(keyword)
	return sortBillsByDate(data,sort)

def getBillsbyAuthor(author,session='session',sort=True): # bills search page
	# params={'author':author,
	# 		'session':session}
	#data=cacheDance('bills='+author+'_'+session,getMNLegBillsbyAuthor, time_hour_24, **params)
	data=getMNLegBillsbyAuthor(author,session)
	return sortBillsByDate(data,sort)

def getBillById(bill,session): # bills search page
	# params={'bill':bill,
	# 		'session':session}
	# data=cacheDance(session+bill,getMNLegBillInfobyId, time_hour_24, **params)
	data=getMNLegBillInfobyId(bill,session)
	return data

def getBillNames(session,sort=True): # bills by session
	params={'session':session}
	# if not current session leave in cache forever
	#data=cacheDance(session,getMNLegBillsbySession, time_hour_24, **params)
	data=getMNLegBillsbySession(session)
	bills=[]
	for d in data:
		n=int(d['bill_id'][3:])
		bills.append((d,n))
	b=sorted(bills, key=lambda tup: tup[1],reverse=sort)
	return b

def getSessionNames(): # session names for bills search page
	#data=cacheDance("sessions",getMNLegMetaData, None)
	data=getMNLegMetaData()
	if data:
		session_details=data["session_details"]
		sessions=[]
		for s in session_details:
			sessions.append(s)
		sessions.sort(reverse=True)
		return sessions,session_details
	else:
		return None

def getAllDistricts(): # districts front
	# data=getFromCache('districts')
	# if not data:
	data = getMNLegAllDistricts()
	if data:
		data=sorted(data)
		#putInCache('districts',data)
	else:
		return None
	return data

def getDistrictById(district_id): # individual district
	# data=getFromCache(district_id)
	# if not data:
	data=getMNLegDistrictById(district_id)
	if data: 
		if 'shape' in data:
			new_shape=[]
			data['district_map']='True'
	 		for p in data['shape'][0][0]:
	 			new_shape.append([p[1],p[0]])
	 		data['shape'][0][0]=new_shape

 		legislator=getLegislatorByDistrict(data['name'])
 		if legislator!=None:
	 		data['legislator']=legislator

	 	demo,url=fetchDistrictDemoData(data['boundary_id'])
	 	if demo!=None:
	 		data['district_demo']=demo
	 		data['district_demo_url']=url

	 	election=get2012ElectionResultsbyDistrict(data['name'],data['chamber'])
	 	if election!=None:
	 		data['leg_results']=election

	 	hpvi=getHPVIbyChamber(data['chamber'])
	 	if hpvi!=None:
	 		data['hpvi']=hpvi

 		#putInCache(district_id,data)
	# else:
	# 	return None
	return data

def getAllDistrictsByID(chamber): # for full senate/house map pages
	# all_data=[]
	# if chamber=='lower':
	# 	data1=getFromCache(chamber+'_districts1')
	# 	data2=getFromCache(chamber+'_districts2')
	# 	if data1 and data2:
	# 		all_data=data1+data2
	# else:
	# 	all_data=getFromCache(chamber+'_districts')
	# if not all_data:
	data=getAllDistricts()
	all_data=[]
	for d in data:
		if d['chamber']==chamber:
			all_data.append(getDistrictById(d['boundary_id']))
	# if chamber=='lower':
	# 	putInCache(chamber+'_districts1',all_data[:len(all_data)/2])
	# 	putInCache(chamber+'_districts2',all_data[len(all_data)/2:])
	# else:
	# 	putInCache(chamber+'_districts',all_data)
	hpvi=getHPVIbyChamber(chamber)
	return all_data,hpvi

def cronEvents(which):
	events=[]
	if which=='senate' or which=='house':
		events=addEventsToParse(which)
	return events

def getAllEvents(which='all'): # events calendar page
	events=[]
	# if which=='senate':
	# 	events=getFromCache('senate_committee_meetings')
	# elif which=='house':
	# 	events=getFromCache('house_committee_meetings')
	# elif which=='other':
	# 	events=getAllOtherEventsAsEvents()
	# elif which=='all':
		# house=getFromCache('house_committee_meetings')
		# senate=getFromCache('senate_committee_meetings')
	leg=Event.Query.all()
	for l in leg:
		events.append(l)
	other=getAllOtherEventsAsEvents()
	return events+other

def getEventById(event_id): # event page
	#params={'event_id':event_id}
	#data=cacheDance(event_id,getMNLegEventById, time_hour_24, **params)
	data=getMNLegEventById(event_id)
	return data

def getAllCommittees(): # committees front page
	# data=getFromCache('committees')
	# if not data:
		# house=getMNLegAllCommittees()
		# senate=getSenateCommittees()
		# if house and senate:
		# 	data=senate+house
	data=getMNLegAllCommittees()
	return sorted(data)

def getCommitteesByChamber(chamber='upper'):
	data=[]
	com=Committee.Query.all().eq(chamber=chamber)
	for c in com:
		data.append(c)
	return sorted(data, key=lambda data: data.name,reverse=False)

def getCommitteeById(com_id): # committee page
	data=getCommitteeDictByID(com_id)
	return data

def getCurrentLegislators(): # legislators page
	#data=cacheDance('legislators',getMNLegislatorByActive, None)
	data=getMNLegislatorByActive()
	return data

def getLegislatorByID(leg_id): # individual legislator page
	data=getMNLegislatorById(leg_id)
	return data

def addEventsToParse(which):
	if which=='senate':
		getAllSenateCommitteeMeetingsAsEvents()
	elif which=='house':
		getAllHouseCommitteeMeetingsAsEvents()

def getBillCounts():
	counts=BillCounts.Query.all()
	for c in counts:
		return c.counts

def addBillCountsToParse():
	counts=BillCounts.Query.all()
	if counts.count()>0:
		for c in counts:
			c.counts=getBillCountsByLegislator()
			c.save()
			break
	else:
		c=BillCounts(counts=getBillCountsByLegislator())
		c.save()

def addLegislatorToParse(leg_id):
	leg=Legislator.get_by_id(leg_id)
	if leg.count()==0:
		data=getMNLegislatorById(leg_id)
		if data:
			first,last=data.get('first_name'),data.get('last_name')
			name=first+' '+last
			params={'name': name,
					'full_name': data.get('full_name'),
	    			'chamber': data.get('chamber'),
	    			'party': data.get('party'),
	    			'district': data.get('district'),
	    			'office_phone': data.get('office_phone'),
	    			'leg_id': data.get('leg_id'),
	    			'votesmart_id': data.get('votesmart_id'),
	    			'leg_url': data.get('+leg_url'),
	    			'active': data.get('active'),
	    			'transparencydata_id': data.get('transparencydata_id'),
	    			'photo_url': data.get('photo_url'),
	    			'roles': data.get('roles'),
	    			'old_roles': data.get('old_roles'),
	    			'offices': data.get('offices'),
	    			}
	    	leg=Legislator(**params)
	    	leg.save()

def addEventToParse():
	pass

def addLegislatorsToParseCommittee(com_id):
	com=Committee.get_by_id(com_id)
	if com.count()==1:
		for c in com:
			members=[]
			for m in c.members:
				leg=Legislator.get_by_id(m.get('leg_id'))
				members.append(leg)
			c.members=members
			c.save()

def addLegislatorToParseDistrict(dist_id):
	#leg=Legislator.get_by_district(dist_id)
	pass

def addCommitteeToParse(com_id):
	data=getMNLegCommitteeById(com_id)
	if data:
		members=[]
		for m in data.get('members'):
			leg=getLegislatorByID(m.get('leg_id'))
			leg['role']=m.get('role')
			members.append(leg)
		com=Committee.get_by_id(com_id)
		if com.count()==0:
			params={'name': data.get('committee'),
					'chamber': data.get('chamber'),
					'subcommittee': data.get('subcommittee'),
					'parent_id': data.get('parent_id'),
					'com_id': data.get('id'),
					'com_url': data.get('sources'),
	    			'members': members
	    			}
			com=Committee(**params)
			com.save()
		else:
			for c in com:
				# members=[]
				# for m in data.get('members'):
				# 	members.append(getLegislatorByID(m.leg_id))
				c.name=data.get('committee')
				c.chamber=data.get('chamber')
				c.subcommittee=data.get('subcommittee')
				c.parent_id=data.get('parent_id')
				c.com_id=data.get('id')
				c.com_url=data.get('sources')
				c.members=members
				c.save()

def addDistrictToParse(dist_id,hpvi):
	dist=District.get_by_id(dist_id)
	if dist.count()==0:
		data=getDistrictById(dist_id)
		if data:
			params={'name': data.get('name'),
	    			'chamber': data.get('chamber'),
	    			'lon_delta': data['region']['lon_delta'],
	    			'center_lon': data['region']['center_lon'],
	    			'lat_delta': data['region']['lat_delta'],
	    			'center_lat': data['region']['center_lat'],
	    			'alt_id': data.get('id'),
	    			'dist_id': data.get('boundary_id'),
	    			'bbox': data.get('bbox'),
	    			'shape': data.get('shape'), # add members as parse leg objects
	    			'legislator': data.get('legislator'),
	    			'demographics': data.get('district_demo'),
	    			'leg_elec_results': data.get('leg_results'),
	    			'hpvi': hpvi,
					}
	    	dist=District(**params)
	    	dist.save()

