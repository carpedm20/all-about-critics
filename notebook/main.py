from IPython.display import HTML

import requests
import json
import pandas as pd
from bs4 import BeautifulSoup

from .models import *

pd.set_option('display.max_colwidth', -1)

def dataframe_with_link(df, col):
    tmp = df.copy()
    tmp[col] = tmp[col].apply(lambda x: '<a href="{0}" target="_blank">{0}</a>'.format(x))
    return HTML(tmp.to_html(escape=False))

CINE = "http://www.cine21.com"

r = requests.get("http://www.cine21.com/review/review20")
soup = BeautifulSoup(r.text)

div = soup.find('div','author_review')

critics = [( ul.text, CINE + ul.a['href']) for ul in div.select("li")]

#critic_tbl = pd.DataFrame(critics, columns=['Name', 'URL'])
critic_tbl = pd.DataFrame(critics, columns=['Name', 'URL'])[:10]

dataframe_with_link(critic_tbl.head(), 'URL')

critics = []
movies = []

get_movie = lambda movies, mid: [movie for movie in movies if movie.mid == mid]
get_soup = lambda url: BeautifulSoup(requests.get(url).text)
        
for data in critic_tbl.iterrows():
    critic = Critic(data[1].Name, data[1].URL)
    critics.append(critic)
    soup = get_soup(data[1].URL)
    
    print " [*] %s %s" % (critic.name, critic.link)
    
    pagination = soup.find('div','pagination')
    last_page = int(pagination.select('a')[-1]['href'].split('/')[-1])
    
    for idx in xrange(1, last_page+1):
        tmp_url = data[1].URL + "/p/" + str(idx)
        soup = get_soup(tmp_url)
        
        for tr in soup.find("table", "tbl_basic4_3 td_st").select("tr"):
            href = CINE + tr.th.a['href']
            
            mid = int(href.split('/')[-1])
            movie = get_movie(movies, mid)
            
            if not movie:
                title = tr.th.a.text[2:]
                movie = Movie(mid, href, title)
                
                movies.append(movie)
            
            tr.th.a.extract()
            tr.th.span.extract()
            
            content = tr.th.text
            rating = int(tr.td.find("strong").text)
            
            review = Review(movie, content, rating)
            critic.reviews.append(review)

from time import mktime
from datetime import datetime

for critic in critics:
    print "~~~~~~~~~~~~~~~~~~~~"
    for i in critic.reviews:
        instance = Movie_DB.query.filter_by(mid=i.movie.mid).first()
        if instance:
            pass
        else:
            # mid, year, time, director, director_en, naver_mid, imdb_mid):
            i.movie.get_imdb()

            dt = datetime.fromtimestamp(mktime(i.movie.time))

            print i.movie.naver_mid,i.movie.imdb_mid
            movie = Movie_DB(i.movie.mid,
                          i.movie.year,
                          dt.date(),
                          i.movie.director,
                          i.movie.director_en,
                          i.movie.naver_mid,
                          i.movie.imdb_mid)
            db_session.add(movie)
            db_session.commit()
