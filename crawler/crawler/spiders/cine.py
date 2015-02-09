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

get_movie = lambda movies, mid: [movie for movie in movies if movie['mid'] == mid]
get_soup = lambda url: BeautifulSoup(requests.get(url).text)
        
CINE = "http://www.cine21.com"
CINE_INFO = "http://www.cine21.com/movie/info/movie_id/"
NAVER_INFO = "http://movie.naver.com/movie/bi/mi/basic.nhn?code="
NAVER_AUTO = "http://auto.movie.naver.com/ac?q_enc=UTF-8&st=1&r_lt=1&n_ext=1&t_koreng=1&r_format=json&r_enc=UTF-8&r_unicode=0&r_escape=1&"

movie_dict = {}

from difflib import SequenceMatcher as sm
def is_same_name(a,b):
    for (x,y) in [(a,b),(b,a)]:
        for word in x.split():
            if word in y:
                return True
    if sm(a=list(set(b)), b=list(set(a))).ratio() > 0.7:
        return True
    return False

import linecache
import sys
def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

class Movie(scrapy.Item):
    mid = scrapy.Field()
    year = scrapy.Field()
    title = scrapy.Field()
    title_en = scrapy.Field()
    time = scrapy.Field()
    director = scrapy.Field()
    director_en = scrapy.Field()
    naver_mid = scrapy.Field()
    imdb_mid = scrapy.Field()
    imdb_candidates = scrapy.Field()

    link = scrapy.Field()

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

        movies = movies[:2]

        for movie in movies:
            movie_dict[movie.mid] = Movie(title=movie.title, mid=movie.mid)

        self.start_urls = [CINE_INFO + str(movie.mid) for movie in movies]

    def parse(self, response):
        mid = int(response.url.split("/")[-1])
        movie = movie_dict[mid]

        try:
            soup = BeautifulSoup(response.body)
            h3 = soup.select(".desc h3")[0].text.strip()
            movie['year'] = int(re.findall(r'\(\d\d\d\d\)$', h3)[-1][1:-1])

            tds = soup.select(".tbl_basic3 tr td")

            movie['title_en'] = tds[0].text.strip()
            movie['director'] = tds[1].text.strip()

            try:
                soup = get_soup(CINE + tds[1].a['href'])
            except:
                soup = get_soup(CINE + tds[2].a['href'])

            try:
                movie['director_en'] = re.findall(r'\(.*\)$', soup.select("span.name")[0].text.strip())[-1][1:-1]
            except:
                return 
            try:
                movie['time'] = time.strptime(tds[-1].text.strip(), "%Y-%M-%d")
            except:
                return 
        except:
            PrintException()
            log.msg(" [!] Error <%s>" % movie['mid'], log.INFO)
            return 

        ################
        # Naver 
        ################

        query = urllib.urlencode({'q' : movie['title'].encode('utf-8')})
        
        body = requests.get(NAVER_AUTO + query).text
        j = json.loads(body[body.find('{'):body.rfind('}')+1])
        
        ans = None
        
        if len(j['items']) > 2:
            for item in j['items']:
                if item:
                    if movie['time'] == time.strptime(item[0][1][0], "%Y%M%d") and item[0][1][-1] == "movie":
                        ans = item
                        break
        else:
            ans = j['items'][0]
        
        if not ans:
            if movie['mid'] == 27710:
                movie['naver_mid'] = 71424
            elif self['mid'] == 26369:
                movie['naver_mid'] = 49475
            elif self['mid'] == 23105:
                movie['naver_mid'] = 64920
            elif self['mid'] == 3684:
                movie['naver_mid'] = 3470449
            else:
                log.msg(" [!] NAVER Movie not found : %s" % movie['mid'])
            
        movie['naver_mid'] = ans[0][-2][0]

        ################
        # IMDB
        ################

        try:
            movies = imdb.find_by_title(movie['title_en'])
        except:
            movies = imdb.find_by_title(movie['title_en'].encode('utf-8'))
        ans = None
        
        if len(movies) > 1:
            movie['imdb_candidates'] = []
            candidates = []
            
            for m in movies:
                if movie['year']:
                    year = int(movie['year'])

                    if year == movie['year'] or year == movie['time'].tm_year:
                        candidates.append(m)

            if len(candidates) == 0:
                candidates = movies

            for candidate in candidates:
                info = imdb.find_movie_by_id(candidate['imdb_id'])

                is_possible = False
                for director in info.directors_summary:
                    if is_same_name(director.name, movie['director_en']):
                        movie['imdb_candidates'].append(candidate)
                        break

            if len(movie['imdb_candidates']) > 1:
                ans = movie['imdb_candidates'][0]
                max_gap = movie['year'] - int(ans['year'])
                
                for candidate in movie['imdb_candidates'][1:]:
                    if max_gap > movie['year'] - int(candidate['year']):
                        ans = candidate
                
                movie['imdb_mid'] = ans['imdb_id']
            
            if len(movie['imdb_candidates']) == 1:
                ans = movie['imdb_candidates'][0]
            elif len(movie['imdb_candidates']) == 0:
                movie['imdb_mid'] = -1
            else:
                log.msg(" [!] IMDB Movie not found : %s" % len(movie['imdb_candidates']))
        elif len(movies) == 0:
            log.msg(" [!] IMDB Movie 0 found : %s" % movie['mid'])
            return 
        else:
            ans = movies[0]
        
        if not ans:
            log.msg(" [!] IMDB Movie not found")
        else:
            movie['imdb_mid'] = ans['imdb_id']

        yield movie
