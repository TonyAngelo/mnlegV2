import parse_rest

parse_rest.APPLICATION_ID = "KrJK8EyTIZ2lVVsNbMVwptH3kFC5tjqaLyCbGCf0"
parse_rest.REST_API_KEY = "7WI13QT8MyCz3oPrzNJFqmP12yAsehE5ZHjW2FeQ"

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

    def get_by_chamber(cls,chamber):
        com = Committee.Query.all().eq(chamber=chamber)
        return com

class District(parse_rest.Object):
    @classmethod
    def get_by_id(cls,dist_id):
    	dist = District.Query.all().eq(dist_id=dist_id)
    	return dist

class Event(parse_rest.Object):
    @classmethod
    def get_by_key(cls,key):
        event = Event.Query.all().eq(key=key)
        return event

class BillCounts(parse_rest.Object):
    pass
