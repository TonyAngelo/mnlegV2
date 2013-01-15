from google.appengine.ext import db

from utils import make_pw_hash,valid_pw,get_coords

def users_key(name = 'default'):
    return db.Key.from_path('users', name)

class User(db.Model):
    name=db.StringProperty(required=True)
    code=db.TextProperty(required=True)
    created=db.DateTimeProperty(auto_now_add=True)
    email=db.StringProperty(required=True)
    valid=db.StringProperty(required=True)
    user_ip=db.StringProperty()
    #coords=db.GeoPtProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls,name):
        u = User.all().filter('name =',name).get()
        return u

    @classmethod
    def register(cls,name,pw,email,user_ip,valid="True"):
        code=make_pw_hash(name,pw)
        #coords=get_coords(user_ip)
        return User(parent = users_key(),
        			name=name,
                    code=code,
                    email=email,
                    user_ip=user_ip,
                    #coords=coords,
                    valid=valid)

    @classmethod
    def login(cls,name,pw):
        u=cls.by_name(name)
        if u and valid_pw(name,pw,u.code) and u.valid=="True":
            return u