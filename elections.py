import csv
import cStringIO
import json
from utils import get_contents_of_url,getFromCache,putInCache

senate_hpvi_feed_url='https://docs.google.com/spreadsheet/tq?range=A1%3AB68&key=0Ao3iZjz2mPXEdE15b2JvWmRzdXp3d05YLW9BN3IzMXc&gid=0&headers=1'
house_hpvi_feed_url='https://docs.google.com/spreadsheet/tq?range=A1%3AB135&key=0Ao3iZjz2mPXEdE15b2JvWmRzdXp3d05YLW9BN3IzMXc&gid=1&headers=1'
senate_raw_hpvi_feed_url='https://docs.google.com/spreadsheet/tq?range=C2%3AC68&key=0Ao3iZjz2mPXEdE15b2JvWmRzdXp3d05YLW9BN3IzMXc&gid=0&headers=0'
house_raw_hpvi_feed_url='https://docs.google.com/spreadsheet/tq?range=C2%3AC135&key=0Ao3iZjz2mPXEdE15b2JvWmRzdXp3d05YLW9BN3IzMXc&gid=1&headers=0'
senate_2012_election_results='http://electionresults.sos.state.mn.us/ENR/Results/MediaResult/1?mediafileid=30'
house_2012_election_results='http://electionresults.sos.state.mn.us/ENR/Results/MediaResult/1?mediafileid=20'
mnleg_district_demo_info='http://www.gis.leg.mn/redist2010/Legislative/L2012/text/'

def fetchDistrictDemoData(district):
	if district.find('u')>0: # senate district
		district=district[-2:]
	else: # house district
		district=district[-3:].upper()
	url=mnleg_district_demo_info+district+'.txt'
	page = get_contents_of_url(url)
	demographics={}
	if page:
		loop=True
		while loop:
			w,page=page[:page.find('\n')],page[page.find('\n')+1:]
			v,page=page[:page.find('\n')],page[page.find('\n')+1:]
			# y,page=page[:page.find('\n')],page[page.find('\n')+1:]
			# z,page=page[:page.find('\n')],page[page.find('\n')+1:]
			# results.append((w+': '+v,y+': '+z))
			demographics[w]=v
			if len(page)<=0:
				loop=False
	return demographics

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

def fetchRawSenatehPVIfeed():
	response = get_contents_of_url(senate_raw_hpvi_feed_url)
	data=json.loads(response[62:-2])
	hpvi=[]
	for r in data['table']['rows']:
		hpvi.append(r['c'][0]['v'])
	return sorted(hpvi)

def fetchRawHousehPVIfeed():
	response = get_contents_of_url(house_raw_hpvi_feed_url)
	data=json.loads(response[62:-2])
	hpvi=[]
	for r in data['table']['rows']:
		hpvi.append(r['c'][0]['v'])
	return sorted(hpvi)

def getHPVIbyChamber(chamber,raw=False):
	if raw:
		if chamber=='upper':
			hpvi=fetchRawSenatehPVIfeed()
		else:
			hpvi=fetchRawHousehPVIfeed()
	else:
		if chamber=='upper':
			hpvi=fetchSenatehPVIfeed()
		else:
			hpvi=fetchHousehPVIfeed()
	return hpvi

def getHPVIbyDistrict(district):
	if district.isdigit(): #senate
		data=getHPVIbyChamber('upper')
	else:
		data=getHPVIbyChamber('lower')
	return data[district]

def parseCSVfromURL(page,delimiter):
	csvio = cStringIO.StringIO(page)
	data = csv.reader(csvio, delimiter=delimiter)
	return data

def fetchSenateElectionResults():
	response=getFromCache('senate2012elections')
	if not response:
		response = get_contents_of_url(senate_2012_election_results)
		if response and response!=None:
			putInCache('senate2012elections',response)
		else:
			return None
	response = parseCSVfromURL(response,';')
	results=[]
	for r in response:
		results.append([r[5],r[4],r[12],r[15]," ".join([x.capitalize() for x in r[7].split(" ")]),r[10],r[14],r[13]])
	return results

def fetchHouseElectionResults():
	response=getFromCache('house2012elections')
	if not response:
		response = get_contents_of_url(house_2012_election_results)
		if response and response!=None:
			putInCache('house2012elections',response)
		else:
			return None
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
	if results and results!=None:
		for r in results:
			if r[0]==district:
				d.append(r)
		return d
	else:
		return None