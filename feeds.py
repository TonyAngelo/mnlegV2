import feedparser
from utils import getFromCache,putInCache

mn_house_session_daily='http://www.house.leg.state.mn.us/rss/sdaily.asp'

mn_townhalls={
	'dfl':['http://www.house.leg.state.mn.us/rss/townhalldfl.asp','DFL town hall meetings - Minnesota House of Representatives'],
	'gop':['http://www.house.leg.state.mn.us/rss/townhallgop.asp','GOP town hall meetings - Minnesota House of Representatives'],
}

def getFeed(link):
	return feedparser.parse(link)

def getMNHouseSessionDaily(n=10):
	results=[]
	f = getFeed(mn_house_session_daily)
	for i in range(n):
		if f['entries']:
			results.append(f['entries'].pop(0))
	putInCache('Session Daily',results)

def getTownhallFeed(party,n=5):
	global mn_townhalls
	results=[]
	f=getFromCache(mn_townhalls[party][1])
	if not f:
		f=getFeed(mn_townhalls[party][0])
		for i in range(n):
			if f['entries']:
				results.append(f['entries'].pop(0))
		mn_townhalls[party][1]=f['feed']['title']
		putInCache(mn_townhalls[party][1],results,86400)
		return mn_townhalls[party][1],results
	else:
		return mn_townhalls[party][1],f