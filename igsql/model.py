from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from igsql.database import Base, db_session, engine

location_media = Table('location_media', Base.metadata,
    Column('location_id', Integer, ForeignKey('location.id'), nullable=False),
    Column('media_id', Integer, ForeignKey('media.id'), nullable=False))

media_tag = Table('media_tag', Base.metadata,
    Column('media_id', Integer, ForeignKey('media.id'), nullable=False),
    Column('tag_id', Integer, ForeignKey('tag.id'), nullable=False))

# stores likes
media_user = Table('media_user', Base.metadata,
    Column('media_id', Integer, ForeignKey('media.id'), nullable=False),
    Column('user_id', Integer, ForeignKey('user.id'), nullable=False))

class Location(Base):
    __tablename__ = 'location'
    id = Column(Integer, primary_key=True)
    lid = Column(String(100), nullable = True) # some locations have no id
    name = Column(String(100), nullable = True) # and no name
    latitude = Column(Float, nullable = True)
    longitude = Column(Float, nullable = True)

    def __repr__(self):
        return '<Location {} {}>'.format(self.latitude, self.longitude)

class Media(Base):
    __tablename__ = 'media'
    id = Column(Integer, primary_key=True)
    mid = Column(String(100), nullable=False, unique=True)
    link = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship('User', backref='media')
    caption = Column(Text, nullable=True)
    location_id = Column(Integer, ForeignKey('location.id'), nullable=True)
    location = relationship('Location', backref='media', secondary=location_media)
    likes = relationship('User', backref='likes', secondary=media_user)
    tags = relationship('Tag', backref='media', secondary=media_tag)
    mtype = Column(String(25), nullable=True)
    standard_resolution = Column(String(200), nullable=True)
    data = Column(Text, nullable=True)
    created_time = Column(DateTime, nullable=False)

    def __repr__(self):
        return '<Media {}>'.format(self.mid)

class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)

    def __repr__(self):
        return '<Tag {}>'.format(self.name)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    #first_name = Column(String(100), nullable=False)
    #last_name = Column(String(100), nullable=False)
    uid = Column(String(50), nullable=False, unique=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)
