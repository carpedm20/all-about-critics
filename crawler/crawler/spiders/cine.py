# -*- coding: utf-8 -*-
import scrapy

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

        for movie in movies:

    def parse(self, response):
        pass
