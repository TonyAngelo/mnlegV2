import csv
import cStringIO
import json
from utils import get_contents_of_url,getFromCache,putInCache,substitute_char,bill_text_remove_markup

API_KEY='4a26c19c3cae4f6c843c3e7816475fae'
base_url='http://openstates.org/api/v1/'
apikey_url="apikey="
senate_hpvi_feed_url='https://docs.google.com/spreadsheet/tq?range=A1%3AB68&key=0Ao3iZjz2mPXEdE15b2JvWmRzdXp3d05YLW9BN3IzMXc&gid=0&headers=1'
house_hpvi_feed_url='https://docs.google.com/spreadsheet/tq?range=A1%3AB135&key=0Ao3iZjz2mPXEdE15b2JvWmRzdXp3d05YLW9BN3IzMXc&gid=1&headers=1'
senate_2012_election_results='http://electionresults.sos.state.mn.us/ENR/Results/MediaResult/1?mediafileid=30'
house_2012_election_results='http://electionresults.sos.state.mn.us/ENR/Results/MediaResult/1?mediafileid=20'

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
	url=base_url+'committees/?state=mn&'+apikey_url+API_KEY
	return sendGetRequest(url)

def getMNLegCommitteeById(com_id):
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

def getMNLegBillsbyKeyword(keyword):
	#http://openstates.org/api/v1/bills/?q=smoking&apikey=4a26c19c3cae4f6c843c3e7816475fae
	url=base_url+'bills/?state=mn&q='+keyword+'&'+apikey_url+API_KEY
	return sendGetRequest(url)

def getMNLegBillsbySession(session,per_page='2000',page='1'):
	session_url='state=mn&search_window=session:'+session+'&'
	url=base_url+'bills/?'+session_url+'&per_page='+per_page+'&page='+page+'&'+apikey_url+API_KEY
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

def fetchSenatehPVIfeed():
	response = get_contents_of_url(senate_hpvi_feed_url)
	data=json.loads(response[62:-2])
	hpvi={}
	for r in data['table']['rows']:
		hpvi[r['c'][0]['f']]=r['c'][1]['v']
	return hpvi

def fetchHousehPVIfeed():
	response = get_contents_of_url(house_hpvi_feed_url)
	data=json.loads(response[62:-2])
	hpvi={}
	for r in data['table']['rows']:
		hpvi[r['c'][0]['v']]=r['c'][1]['v']
	return hpvi

def getHPVIbyChamber(chamber):
	if chamber=='upper':
		hpvi=fetchSenatehPVIfeed()
	else:
		hpvi=fetchHousehPVIfeed()
	return hpvi

def parseCSVfromURL(page,delimiter):
	csvio = cStringIO.StringIO(page)
	data = csv.reader(csvio, delimiter=delimiter)
	return data

def addDistrictElectionResults():
	pass

def fetchSenateElectionResults():
	response=getFromCache('senate2012elections')
	if not response:
		response = get_contents_of_url(senate_2012_election_results)
		if response:
			putInCache('senate2012elections',response)
	response = parseCSVfromURL(response,';')
	results=[]
	for r in response:
		results.append([r[5],r[4],r[12],r[15]," ".join([x.capitalize() for x in r[7].split(" ")]),r[10],r[14],r[13]])
	return results

def fetchHouseElectionResults():
	response=getFromCache('house2012elections')
	if not response:
		response = get_contents_of_url(house_2012_election_results)
		if response:
			putInCache('house2012elections',response)
	response = parseCSVfromURL(response,';')
	results=[]
	for r in response:
		results.append([r[5],r[4],r[12],r[15]," ".join([x.capitalize() for x in r[7].split(" ")]),r[10],r[14],r[13]])
	return results

def get2012ElectionResultsbyChamber(chamber):
	if chamber=='upper':
		results=fetchSenateElectionResults()
	else:
		results=fetchHouseElectionResults()
	return results

def get2012ElectionResultsbyDistrict(district,chamber):
	if chamber=='upper':
		results=fetchSenateElectionResults()
	else:
		results=fetchHouseElectionResults()
	d=[]
	for r in results:
		if r[0]==district:
			d.append(r)
	return d

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
			new_shape=[]
	 		for p in data['shape'][0][0]:
	 			new_shape.append([p[1],p[0]])
	 		data['shape'][0][0]=new_shape
	 		legislator=getLegislatorByDistrict(data['name'])
	 		if legislator!=None:
		 		data['legislator']=legislator
	 		putInCache(district_id,data)
		else:
			return None
	return data

def getAllDistrictsByID(chamber):
	data=getFromCache('all_districts')
	if not data:
		data=getAllDistricts()
		all_data=[]
		for d in data:
			if d['chamber']==chamber:
				all_data.append(getDistrictById(d['boundary_id']))
		putInCache(chamber+'_districts',all_data)
	return all_data

def getAllEvents():
	# data=getFromCache('events')
	# if not data:
	data=getMNLegAllEvents()
		# if data:
	 # 		putInCache('events',data)
		# else:
		# 	return None
	return data

def getEventById(event_id):
	# data=getFromCache(event_id)
	# if not data:
	data=getMNLegEventById(event_id)
		# if data:
	 # 		putInCache(event_id,data)
		# else:
		# 	return None
	return data

def getAllCommittees():
	# data=getFromCache('committees')
	# if not data:
	data=getMNLegAllCommittees()
		# if data:
	 # 		putInCache('committees',data)
		# else:
		# 	return None
	return data

def getCommitteeById(com_id):
	# data=getFromCache(com_id)
	# if not data:
	data=getMNLegCommitteeById(com_id)
		# if data:
	 # 		putInCache(com_id,data)
		# else:
		# 	return None
	return data

def getCurrentLegislators():
	# data=getFromCache('legislators')
	# if not data:
	data=getMNLegislatorByActive()
	
		# if data:
	 # 		putInCache('legislators',data)
		# else:
		# 	return None
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

def getBillById(bill,session):
	path=session+bill
	# data=getFromCache(path)
	# if not data:
	data=getMNLegBillInfobyId(bill,session)
		# if data:
	 # 		putInCache(path,data)
		# else:
		# 	return None
	return data

def getBillNames(session):
	# data=getFromCache(session)
	# if not data:
	data=getMNLegBillsbySession(session)
		# if data:
		# 	putInCache(session,data)
		# else:
		# 	return None
	bills=[]
	for d in data:
		bills.append(d)
	return bills

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


