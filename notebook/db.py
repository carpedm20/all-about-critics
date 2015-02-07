from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Date, Integer, String, Text, Boolean, Date

import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

engine = create_engine('sqlite:///movie.db', echo=True)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

class Movie_DB(Base):
    __tablename__ = 'movie'
    mid = Column(Integer, primary_key=True)
    year = Column(String(50))
    time = Column(Date)
    director = Column(String(100))
    director_en = Column(String(100))
    naver_mid = Column(Integer, unique=True)
    imdb_mid = Column(Integer)

    def __init__(self, mid, year, time, director, director_en, naver_mid, imdb_mid):
        self.mid = mid
        self.year = year
        self.time = time
        self.director = director
        self.director_en = director_en
        self.naver_mid = naver_mid
        self.imdb_mid = imdb_mid

    def __repr__(self):
        msg = '<Movie %s <%s> ( %s )>' % (self.title, self.mid, "http://www.cine21.com/movie/info/movie_id/" + self.mid)
        return msg.encode('utf8')

Base.metadata.create_all(bind=engine)
