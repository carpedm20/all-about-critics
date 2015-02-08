# -*- coding: utf-8 -*-
import scrapy
from scrapy import log

import re
import time
import pickle
import requests
import json
import urllib
import pandas as pd
from bs4 import BeautifulSoup
from imdbpie import Imdb

from .utils import *

imdb = Imdb({'cache': True})
imdb = Imdb({'cache': True, 'cache_dir': '/tmp/imdbpie-cache-here'})

get_movie = lambda movies, mid: [movie for movie in movies if movie.mid == mid]
get_soup = lambda url: BeautifulSoup(requests.get(url).text)
        
CINE = "http://www.cine21.com"
CINE_INFO = "http://www.cine21.com/movie/info/movie_id/"
NAVER_INFO = "http://movie.naver.com/movie/bi/mi/basic.nhn?code="
NAVER_AUTO = "http://auto.movie.naver.com/ac?q_enc=UTF-8&st=1&r_lt=1&n_ext=1&t_koreng=1&r_format=json&r_enc=UTF-8&r_unicode=0&r_escape=1&"

class CineSpider(scrapy.Spider):
    name = "cine"
    allowed_domains = ["cine21.com"]
    start_urls = (
        'http://www.cine21.com/',
    )

    def __init__(self):
        try: 
            with open('critics.pkl','rb') as f:
                critics = pickle.load(f)
            with open('movies.pkl','rb') as f:
                movies = pickle.load(f)
        except:
            critics, movies = get_critics()

            with open('critics.pkl', 'wb') as f:
                pickle.dump(critics, f)
            with open('movies.pkl', 'wb') as f:
                pickle.dump(movies, f)

        self.start_urls = [CINE_INFO + str(movie.mid) for movie in movies]

    def parse(self, response):
        try:
            soup = BeautifulSoup(response.body)
            h3 = soup.select(".desc h3")[0].text.strip()
            self._year = int(re.findall(r'\(\d\d\d\d\)$', h3)[-1][1:-1])

            tds = soup.select(".tbl_basic3 tr td")

            self._title_en = tds[0].text.strip()
            self._director = tds[1].text.strip()

            try:
                soup = get_soup(CINE + tds[1].a['href'])
            except:
                soup = get_soup(CINE + tds[2].a['href'])

            try:
                self._director_en = re.findall(r'\(.*\)$', soup.select("span.name")[0].text.strip())[-1][1:-1]
            except:
                return False
            try:
                self._time = time.strptime(tds[-1].text.strip(), "%Y-%M-%d")
            except:
                return False
        except:
            log.msg(" [!] Error %s <%s>" % self.base_url, log.INFO)
            return False

        query = urllib.urlencode({'q' : self.title.encode('utf-8')})
        
        body = requests.get(NAVER_AUTO + query).text
        j = json.loads(body[body.find('{'):body.rfind('}')+1])
        
        ans = None
        
        if len(j['items']) > 2:
            for item in j['items']:
                if item:
                    if not self._time: self.get_info()
                    if self._time == time.strptime(item[0][1][0], "%Y%M%d") and item[0][1][-1] == "movie":
                        ans = item
                        break
        else:
            ans = j['items'][0]
        
        if not ans:
            if self.mid == 27710:
                self._naver_mid = 71424
                return
            elif self.mid == 26369:
                self._naver_mid = 49475
                return
            elif self.mid == 23105:
                self._naver_mid = 64920
                return
            elif self.mid == 3684:
                self._naver_mid = 3470449
                return
            raise Exception(" [!] NAVER Movie not found : %s" % self.mid)
            
        self._naver_mid = ans[0][-2][0]
            
        #soup = get_soup(NAVER_INFO+self._naver_mid)
