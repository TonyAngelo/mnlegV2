import parse_rest
import ConfigParser

config = ConfigParser.ConfigParser()
config.read(["etc/boto.cfg"])
i=config.get('Parse','APPLICATION_ID')
k=config.get('Parse','REST_API_KEY')

parse_rest.APPLICATION_ID = i
parse_rest.REST_API_KEY = k

class Legislator(parse_rest.Object):
    @classmethod
    def get_by_id(cls,leg_id):
    	leg = Legislator.Query.all().eq(leg_id=leg_id)
    	return leg

    @classmethod
    def get_by_district(cls,district):
    	leg = Legislator.Query.all().eq(district=district)
    	return leg

class Committee(parse_rest.Object):
    @classmethod
    def get_by_id(cls,com_id):
    	com = Committee.Query.all().eq(com_id=com_id)
    	return com

    @classmethod
    def get_by_chamber(cls,chamber):
        com = Committee.Query.all().eq(chamber=chamber)
        return com

class District(parse_rest.Object):
    @classmethod
    def get_by_id(cls,dist_id):
    	dist = District.Query.all().eq(dist_id=dist_id)
    	return dist

    @classmethod
    def get_by_chamber(cls,chamber):
        dist = District.Query.all().eq(chamber=chamber).order_by('dist_id').limit(150)
        return dist

class Event(parse_rest.Object):
    @classmethod
    def get_by_key(cls,key):
        event = Event.Query.all().eq(key=key)
        return event

class BillCounts(parse_rest.Object):
    pass
