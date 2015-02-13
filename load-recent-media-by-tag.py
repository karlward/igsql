#!/usr/bin/env python

import json
from instagram.client import InstagramAPI
from igsql.database import Base, db_session, engine
from igsql.model import Location, Media, Tag, User
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from urlparse import urlparse

client_id = 'secret'
client_secret = 'secret'

# documentation here - https://github.com/Instagram/python-instagram
access_token = 'secret'

api = InstagramAPI(client_id=client_id, client_secret=client_secret)
#api = InstagramAPI(access_token=access_token)

search_tag = 'aiweiwei'

max_id = 0
i = 0

while True:
    print('iteration {}, max_id {}'.format(i, max_id))
    i += 1
    ans = api.tag_recent_media(500, max_id, search_tag)
    parsed = urlparse(ans[1])
    params = {a:b for a,b in [x.split('=') for x in parsed.query.split('&')]}
    max_id = int(params['max_tag_id']) - 1
    for m in ans[0]:
        try:
            u = db_session.query(User).filter_by(uid=str(m.user.id)).one()
        except NoResultFound:
            u = User(username=m.user.username, uid=m.user.id)
            db_session.add(u)
            db_session.commit()
    
        mo = Media(mid=m.id, link=m.link, user_id=u.id, mtype=m.type, created_time=m.created_time)
        if m.type == 'image':
            mo.standard_resolution = m.images['standard_resolution'].url
        elif m.type == 'video':
            mo.standard_resolution = m.videos['standard_resolution'].url
    
        if hasattr(m, 'location') and hasattr(m.location, 'point') and hasattr(m.location.point, 'latitude') and hasattr(m.location.point, 'longitude'):
            try:
                l = db_session.query(Location).filter_by(lid=m.location.id).one()
            except NoResultFound:
                l = Location(lid=m.location.id, name=m.location.name,
                             latitude=m.location.point.latitude,
                             longitude=m.location.point.longitude)
                db_session.add(l)
                db_session.commit()
            mo.location_id = l.id
    
        if hasattr(m, 'tags'):
            for t in m.tags:
                try:
                    to = db_session.query(Tag).filter_by(name=t.name).one()
                except NoResultFound:
                    to = Tag(name=t.name)
                    db_session.add(to)
                    db_session.commit()
                mo.tags.append(to)
    
        try:
            db_session.add(mo)
            db_session.commit()
            if hasattr(m, 'likes'):
                for d in m.likes:
                    try:
                        do = db_session.query(User).filter_by(uid=str(d.id)).one()
                    except NoResultFound:
                        do = User(uid=str(d.id), username=d.username)
                        db_session.add(do)
                        db_session.commit()
                    mo.likes.append(do)
                    db_session.add(mo)
                    db_session.commit() 
                
        except (OperationalError, IntegrityError):
            db_session.rollback()
