import requests
from bs4 import BeautifulSoup
import pandas as pd

get_movie = lambda movies, mid: [movie for movie in movies if movie.mid == mid]
get_soup = lambda url: BeautifulSoup(requests.get(url).text)

CINE = "http://www.cine21.com"
NAVER_INFO = "http://movie.naver.com/movie/bi/mi/basic.nhn?code="
NAVER_AUTO = "http://auto.movie.naver.com/ac?q_enc=UTF-8&st=1&r_lt=1&n_ext=1&t_koreng=1&r_format=json&r_enc=UTF-8&r_unicode=0&r_escape=1&"

class Critic(object):
    def __init__(self, name, link):
        self.name = name
        self.link = link
        self.reviews = []
    
    def __repr__(self):
        msg = '<Critic %s (%s): %s>' % (self.name, self.link, len(self.reviews))
        return msg.encode('utf8')

class Review(object):
    def __init__(self, movie, text, rating):
        self.movie = movie
        self.text = text
        self.rating = rating
    
    def __repr__(self):
        msg = '<Review %s (%s)>' % (self.movie.title, self.rating)
        return msg.encode('utf8')

class Movie(object):
    def __init__(self, mid, title):
        self.mid = mid
        self.title = title

def get_critics():
    r = requests.get("http://www.cine21.com/review/review20")
    soup = BeautifulSoup(r.text)

    div = soup.find('div','author_review')

    critics = [( ul.text, CINE + ul.a['href']) for ul in div.select("li")]
    critic_tbl = pd.DataFrame(critics, columns=['Name', 'URL'])

    critics = []
    movies = []

    for data in critic_tbl.iterrows():
        critic = Critic(data[1].Name, data[1].URL)
        critics.append(critic)
        soup = get_soup(data[1].URL)
        
        print critic
        
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
                    movie = Movie(mid, title)
                    
                    movies.append(movie)
                
                tr.th.a.extract()
                tr.th.span.extract()
                
                content = tr.th.text
                rating = int(tr.td.find("strong").text)
                
                review = Review(movie, content, rating)
                critic.reviews.append(review)

    return critics, movies
