# -*- coding: utf-8 -*-
import scrapy
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

import re
import json

NAVER_URL = "http://movie.naver.com/movie/bi/mi/basic.nhn?code="
CINE_URL = "http://www.cine21.com/movie/info/movie_id/"
IMDB_URL = "http://www.imdb.com/title/"

class CompactSpider(scrapy.Spider):
    name = "compact"
    allowed_domains = ["watcha.net", "imdb.com", "naver.com", "cine21.com"]
    start_urls = (
        'http://google.com',
    )
    movie_dict = {}

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        pass

    def parse(self, response):
        data = json.loads(open('compact.json').read())
    
        for d in data[:20]:
            mid = d['mid']
            self.movie_dict[mid] = {}
            yield scrapy.Request(CINE_URL + str(mid),
                                 callback=self.parse_cine,
                                 meta={'mid': mid})
            yield scrapy.Request(IMDB_URL + str(d['imdb_mid']),
                                 callback=self.parse_imdb,
                                 meta={'mid': mid})
            yield scrapy.Request(NAVER_URL + str(d['naver_mid']),
                                 callback=self.parse_naver,
                                 meta={'mid': mid})

    def parse_cine(self, response):
        movie = self.movie_dict[response.meta['mid']]

        scores = response.xpath("//div[@class='number']/text()").extract()
        movie['cine_user'] = float(scores[0].strip())
        movie['cine_critic'] = float(scores[1].strip())

        scrapy.log.msg(movie)

    def parse_imdb(self, response):
        movie = self.movie_dict[response.meta['mid']]

        try:
            movie['imdb_user'] = float(response.xpath("//span[@itemprop='ratingValue']/text()")[0].extract())
            count = response.xpath("//span[@itemprop='ratingCount']/text()")[0].extract()
            movie['imdb_user_count'] = int(re.sub("[^\d]", "", count))
        except:
            movie['imdb_user'] = -1
            movie['imdb_user_count'] = -1

        for elem in response.xpath("//div[@class='star-box-details']/a"):
            href = elem.xpath("@href")[0].extract()
            if 'criticreviews' in href:
                movie['metacritic'] = elem.xpath("text()").extract()

        scrapy.log.msg(movie)

    def parse_naver(self, response):
        movie = self.movie_dict[response.meta['mid']]

        counts = response.xpath("//span[@class='user_count']/em/text()").extract()

        movie['naver_user_count'] = int(re.sub("[^\d]", "", counts[0]))
        movie['naver_critic_count'] = int(re.sub("[^\d]", "", counts[1]))

        try:
            style = response.xpath("//a[@class='spc']/div[@class='star_score']/span/span/@style")[0].extract()
            movie['naver_critic'] = float(re.sub("[^\d\.]", "", style))
        except:
            movie['naver_critic'] = -1

        try:
            style = response.xpath("//a[@id='pointNetizenPersentBasic']/span/span/@style")[0].extract()
            movie['naver_user'] = float(re.sub("[^\d\.]", "", style))
        except:
            movie['naver_user'] = -1

        movie['poster'] = response.xpath("//div[@class='poster']/a/img/@src").extract()[-1]

        infos = response.xpath("//dl[@class='info_spec']/dd/p/span/a/@href").extract()

        movie['genre'] = []
        for info in infos:
            if 'genre=' in info:
                movie['genre'].append(int(re.sub("[^\d]", "", infos[0])))
            elif 'nation=' in info:
                movie['nation'] = info[3][-2:]

        scrapy.log.msg(movie)

    def spider_closed(self, spider):
        with open('result.json','w') as f:
            json.dump(self.movie_dict, f)
