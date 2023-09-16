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
    name = "all_poets_c"
    start_urls = ["https://ganjoor.net/"]
    id = 1
    centries = {}
    def write_to_file(self,file_name,txt):
        file = open(file_name, 'w', encoding='utf-8')
        file.write(txt)
        file.close()
    def parse(self, response):
        all_div_cols = response.css('#real-centuries .caption a , #real-centuries .century')
        i = 0
        while(i < len(all_div_cols)):
            el = all_div_cols[i]
            i+=1
            if len(el.css(".century")) == 1:
                c = el.css(".century::text").extract()[0].strip()
                self.centries[c] = []
            else:
                print(el.css("a"))
                quote = el
                title = quote.xpath('@title').extract()
                author= quote.xpath('@href').extract()[0].replace("/","")
                items = {}
                items["author"] = author
                items["link"] = self.start_urls[0] + author
                self.centries.get(c).append(items)
        print(self.centries)
        self.write_to_file( "../data/all_poets_centries"+".json",json.dumps(self.centries ,ensure_ascii=False ))
  