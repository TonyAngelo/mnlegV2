from google.appengine.ext import db

from utils import make_pw_hash,valid_pw,get_coords,resize_image,get_contents_of_url

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

def legislator_photo_key(name = 'default'):
    return db.Key.from_path('legislator_photo', name)

class LegislatorPhoto(db.Model):
    leg_id=db.StringProperty(required=True)
    created=db.DateTimeProperty(auto_now_add=True)
    photo=db.BlobProperty(required=True)
    # thumb=db.BlobProperty(required=True)

    @classmethod
    def create_photo(cls,leg_id,photo):
        image=get_contents_of_url(photo)
        # thumb=resize_image(image,50)
        #images.resize(self.request.get('img'), 32, 32)
        return LegislatorPhoto(parent=legislator_photo_key(),
            leg_id=leg_id,
            photo=image,)
            # thumb=thumb,)

    @classmethod
    def get_thumbnail(cls,leg_id):
        p=cls.by_leg_id(leg_id)
        return resize_image(p.photo,50)

    @classmethod
    def by_leg_id(cls,leg_id):
        p = LegislatorPhoto.all().filter('leg_id =',leg_id).get()
        return p
