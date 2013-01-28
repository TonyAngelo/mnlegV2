import json
from utils import (get_contents_of_url,getFromCache,putInCache,substitute_char,
					bill_text_remove_markup,getCurrentBillsDateString,getCommitteeMeetings,
					convertDateToTimeStamp,parseCommitteeMeetings,convertCommitteeDateStringtoDate,)
from elections import (getHPVIbyChamber,get2012ElectionResultsbyChamber,
                    get2012ElectionResultsbyDistrict,fetchDistrictDemoData)

API_KEY='4a26c19c3cae4f6c843c3e7816475fae'
base_url='http://openstates.org/api/v1/'
apikey_url="apikey="

day_of_week={'SUNDAY,':'SUNDAY,',
             'MONDAY,':'MONDAY,',
             'TUESDAY,':'TUESDAY,',
             'WEDNESDAY,':'WEDNESDAY,',
             'THURSDAY,':'THURSDAY,',
             'FRIDAY,':'FRIDAY,',
             'SATURDAY,':'SATURDAY,',}

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

def getMNLegCommitteeById(com_id):
	#http://openstates.org/api/v1/committees/MNC000038/?apikey=4a26c19c3cae4f6c843c3e7816475fae
	url=base_url+'committees/'+com_id+'/?'+apikey_url+API_KEY
	return sendGetRequest(url)

def getMNLegislatorById(leg_id):
	#http://openstates.org/api/v1/legislators/MNL000105/?apikey=4a26c19c3cae4f6c843c3e7816475fae
	url=base_url+'legislators/'+leg_id+'/?'+apikey_url+API_KEY
	return sendGetRequest(url)

def getMNLegislatorByActive():
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
	url=base_url+'bills/?state=mn&search_window='+session+'&sponsor_id='+author+'&'+apikey_url+API_KEY
	return sendGetRequest(url)

def getMNLegBillsCurrent(n=10):
	#http://openstates.org/api/v1/bills/?per_page=5&page=1&updated_since=2013-1-15&state=mn&search_window=session&apikey=4a26c19c3cae4f6c843c3e7816475fae
	d=getCurrentBillsDateString()
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

def getCurrentBills(n=10):
	data=getFromCache('Current Bills')
	if not data:
		data = getMNLegBillsCurrent(n)
		if data:
			putInCache('Current Bills',data)
		else:
			return None
	return data

def getAllDistricts():
	data=getFromCache('districts')
	if not data:
		data=getMNLegAllDistricts()
		if data:
	 		putInCache('districts',data)
		else:
			return None
	return data

def getDistrictById(district_id):
	data=getFromCache(district_id)
	if not data:
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

		 	demo=fetchDistrictDemoData(data['boundary_id'])
		 	if demo!=None:
		 		data['district_demo']=demo

		 	election=get2012ElectionResultsbyDistrict(data['name'],data['chamber'])
		 	if election!=None:
		 		data['leg_results']=election

		 	hpvi=getHPVIbyChamber(data['chamber'])
		 	if hpvi!=None:
		 		data['hpvi']=hpvi

	 		putInCache(district_id,data)
		else:
			return None
	return data

def getAllDistrictsByID(chamber):
	all_data=[]
	if chamber=='lower':
		data1=getFromCache(chamber+'_districts1')
		data2=getFromCache(chamber+'_districts2')
		if data1 and data2:
			all_data=data1+data2
	else:
		all_data=getFromCache(chamber+'_districts')
	if not all_data:
		data=getAllDistricts()
		all_data=[]
		for d in data:
			if d['chamber']==chamber:
				all_data.append(getDistrictById(d['boundary_id']))
		if chamber=='lower':
			putInCache(chamber+'_districts1',all_data[:len(all_data)/2])
			putInCache(chamber+'_districts2',all_data[len(all_data)/2:])
		else:
			putInCache(chamber+'_districts',all_data)
	hpvi=getHPVIbyChamber(chamber)
	return all_data,hpvi

def getAllEvents():
	events=getFromCache('events')
	if not events:
		events=[]
		data=getMNLegAllEvents()
		if data:
	 		for d in data:
		 		event={
		 		'day':int(d['when'][8:10]),
		 		'month':int(d['when'][5:7]),
		 		'year':int(d['when'][:4]),
		 		'hour':int(d['when'][11:13]),
		 		'min':int(d['when'][14:16]),
		 		'type':d['type'],
		 		'title':d['description'],
		 		'description':d['description'],
		 		'url':'/events/'+d['id']}
		 		events.append(event)
		meetings=getAllCommitteeMeetingsAsEvents()
		if meetings:
			for m in meetings:
				events.append(m)
	 	putInCache('events',events)
		# else:
		# 	return None
	return events

def getEventById(event_id):
	data=getFromCache(event_id)
	if not data:
		data=getMNLegEventById(event_id)
		if data:
	 		putInCache(event_id,data)
		else:
			return None
	return data

def getAllCommittees():
	data=getFromCache('committees')
	if not data:
		data=getMNLegAllCommittees()
		if data:
	 		putInCache('committees',data)
		else:
			return None
	return data

def getCommitteeById(com_id,parsed=False):
	data=getFromCache(com_id)
	if not data:
		data=getMNLegCommitteeById(com_id)
		putInCache(com_id,data)
		if not data:
			return None
	if parsed:
		meetings=parseCommitteeMeetings(data['sources'][0]['url'])
	else:
		meetings=getCommitteeMeetings(data['sources'][0]['url'])
	return data,meetings

def getAllCommitteeMeetings(parsed=False):
	coms=getAllCommittees()
	meetings=[]
	for c in coms:
		data,meet=getCommitteeById(c['id'],parsed)
		meetings.append((c['id'],meet))
	return meetings

def getAllCommitteeMeetingsAsEvents():
	meetings=getFromCache('all_committee_meetings')
	if not meetings:
		data=getAllCommitteeMeetings(True)
		meetings=[]
		for com in data:
 			for l in com[1]:
 				if l in day_of_week:
 					count=0
 					date=''
		 			time=''
		 			title_count=-1
		 			room_count=-1
		 			chair_count=-1
		 			room=''
		 			chair=''
		 			event={}
		 		else:
		 			count+=1

		 		if count==1:
		 			date=l
		 		elif count==2:
		 			time=l
		 			f=convertCommitteeDateStringtoDate(date+' '+time)
		 			if f!=None:
		 				event['day']=f.tm_mday
	 					event['month']=f.tm_mon
	 					event['year']=f.tm_year
	 					event['hour']=f.tm_hour
	 					event['min']=f.tm_min
	 					event['type']='committee meeting'
	 					event['url']='/committees/'+com[0]
	 			elif l=='Room:':
	 				room_count=count+1
	 			elif room_count==count:
	 				room=l
	 			elif l=='Chair:' or l=='Chairs':
	 				chair_count=count+1
	 			elif chair_count==count:
	 				chair=l
	 			elif l=='Agenda:':
	 				title_count=count+1
	 			elif title_count==count:
	 				event['title']=l
	 				event['description'] = 'Location: '+room+' Chair: '+chair
	 				meetings.append(event)
 		putInCache('all_committee_meetings',meetings)
	return meetings

def getCurrentLegislators():
	data=getFromCache('legislators')
	if not data:
		data=getMNLegislatorByActive()
		if data:
	 		putInCache('legislators',data)
		else:
			return None
	return data

def getLegislatorByID(leg_id):
	data=getFromCache(leg_id)
	if not data:
		data=getMNLegislatorById(leg_id)
		if data:
	 		putInCache(leg_id,data)
		else:
			return None
	return data

def sortBillsByDate(data,sort):
	bills=[]
	for d in data:
		bills.append(d)
	b=sorted(bills, key=lambda bills: bills['updated_at'] ,reverse=sort)
	return b

def getBillsbyKeyword(keyword,sort=True):
	data=getFromCache('query='+keyword)
	if not data:
		data = getMNLegBillsbyKeyword(keyword)
		if data:
			putInCache('query='+keyword,data)
		else:
			return None
	return sortBillsByDate(data,sort)

def getBillsbyAuthor(author,session='session',sort=True):
	data=getFromCache('bills='+author+'_'+session)
	if not data:
		data = getMNLegBillsbyAuthor(author,session)
		if data:
			putInCache('bills='+author+'_'+session,data)
		else:
			return None
	return sortBillsByDate(data,sort)

def getBillById(bill,session):
	path=session+bill
	data=getFromCache(path)
	if not data:
		data=getMNLegBillInfobyId(bill,session)
		if data:
	 		putInCache(path,data)
		else:
			return None
	return data

def getBillNames(session,sort=True):
	data=getFromCache(session)
	if not data:
		data=getMNLegBillsbySession(session)
		if data:
			putInCache(session,data)
		else:
			return None
	bills=[]
	for d in data:
		n=int(d['bill_id'][3:])
		bills.append((d,n))
	b=sorted(bills, key=lambda tup: tup[1],reverse=sort)
	return b

def getSessionNames():
	data=getFromCache("sessions")
	if not data:
		data=getMNLegMetaData()
		if data:
			putInCache("sessions",data)
		else:
			return None
	session_details=data["session_details"]
	sessions=[]
	for s in session_details:
		sessions.append(s)
	sessions.sort(reverse=True)
	return sessions,session_details
