from math import e
from platform import release
from statistics import mode
from urllib import response
from urllib.parse import quote, unquote

import scrapy
import json
import pandas as pd

class Ghazzali(scrapy.Spider):
    name = "iran_cities"
    first_page = "https://fa.wikipedia.org/wiki/%D9%81%D9%87%D8%B1%D8%B3%D8%AA_%D8%B4%D9%87%D8%B1%D9%87%D8%A7%DB%8C_%D8%A7%DB%8C%D8%B1%D8%A7%D9%86"
    file_id = int(open("../last_site.txt","r").readline())


    def start_requests(self):
        url = quote(self.first_page)
        yield scrapy.Request(url=url, callback=self.parse)

            
    def write_to_file(self,file_name,txt):
        file = open(file_name, 'w', encoding='utf-8')
        to_write =txt
        file.write(to_write)
        file.close()
    
 
    def parse(self, response):
        data = ""
        elems = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "jquery-tablesorter", " " ))]//a')
        for el in elems:
            data += el.css("::text").get()+"\n"
            self.write_to_file(f"vehicles{self.file_id}.txt","crawled from {self.first_page} \n"+data)
            
            
        

