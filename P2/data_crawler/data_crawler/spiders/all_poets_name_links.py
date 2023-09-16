from math import e
from platform import release
from statistics import mode
from time import sleep
from urllib import response
from urllib.parse import quote, unquote

import scrapy
import time

import json
import pandas as pd
import re
import os
class Ghazzali(scrapy.Spider):
    name = "all_poets"
    start_urls = ["https://ganjoor.net/"]
    id = 1
    authors = {}
    def write_to_file(self,file_name,txt):
        file = open(file_name, 'w', encoding='utf-8')
        file.write(txt)
        file.close()
    def parse(self, response):
        all_div_cols = response.css('div.poet').css("a")
        for quote in all_div_cols:
            title = quote.xpath('@title').extract()
            if (len(title)) <= 0:
                continue
            title = title[0]
            author= quote.xpath('@href').extract()[0]
            items = {}
            items["title"] = title
            items["author"] = author
            items["link"] = self.start_urls[0] + author
            items["id"] = self.id
            self.authors[author] = items
            self.id +=1
            self.write_to_file( "../data/all_poets"+".json",json.dumps(self.authors ,ensure_ascii=False ))
  