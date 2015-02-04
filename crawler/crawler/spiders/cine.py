# -*- coding: utf-8 -*-
import scrapy


class CineSpider(scrapy.Spider):
    name = "cine"
    allowed_domains = ["cine21.com"]
    start_urls = (
        'http://www.cine21.com/',
    )

    def parse(self, response):
        pass
