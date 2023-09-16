from math import e
from platform import release
from statistics import mode
from time import sleep
from urllib import response
from urllib.parse import quote, unquote
import multiprocessing
#lock = multiprocessing.Lock()
import scrapy
import time

import json
import pandas as pd
import re
import os
class Ghazzali(scrapy.Spider):
    name = "general_poet"
    f = open("inputname.txt","r")
    poet_name = f.readline().strip()
    f.close()
    store_path = f"../data/{poet_name}"
    if os.path.isdir(store_path) != True:
        os.system(f"mkdir {store_path}")
    ganjoor_page = "https://ganjoor.net"
    list_source = []
    output = ""
    output2 = {}

    def start_requests(self):
        url = self.ganjoor_page+"/"+self.poet_name
        yield scrapy.Request(url=url, callback=self.parse,cb_kwargs = {"mode":1,"file_path":
            f'{self.store_path}/{self.poet_name}'})


    def get_text(self,elems,mode = 1): 
        if mode == 1:
            elems =elems.xpath("//p")
        res = ""
        print(len(elems))
        for i,elem in enumerate(elems):
            res =res+elem.css("::text").get()+"\n"
        return res
        
    def write_to_file(self,file_name,txt):
        file = open(file_name, 'w', encoding='utf-8')
        file.write(txt)
        file.close()

    def parse_mode2(self,response,url,file_path):
        print("mode2 : ",response)
        try:
            print("get_text " ,end="")
            res = self.get_text(response.xpath('//*[(@id = "garticle")]//p'),mode = 0) 
            print("out of get")
            self.output += res
            print("into write")
            self.write_to_file( file_path+".txt",self.output)
            print("out of wite  to file")
            self.output2[url] = res
            print("into write json")
            self.write_to_file( file_path+".json",json.dumps(self.output ,ensure_ascii=False ))
            print("outo write json")
        except:
            print(e)


    def parse(self, response,mode,file_path):
        print(mode,response)
        try:
            if mode == 1:
                res = self.get_text(response.xpath('//*[(@id = "garticle")]//p'),mode = 0)
                file = open(f'{self.store_path}/main_page.txt', 'w', encoding='utf-8')
                file.write(res)
                file.close()
                self.list_source = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "part-title-block", " " ))]//a')
                for url in self.list_source:
                    my_url =self.ganjoor_page+url.css("::attr(href)").extract()[0]
                    print(my_url)
                    yield scrapy.Request(url=my_url,method = "GET", callback=self.parse ,cb_kwargs = {"mode":3,"file_path":
                    file_path})
            else:
                url_str  = str(response.request.url).split("/")
                url_str = url_str[len(url_str)-1]
                numbers = re.findall('[0-9]+', url_str)
                for num in numbers:
                    url_str = url_str.replace(str(num),"")
                if url_str == "sh":
                    self.parse_mode2(response=response,file_path=file_path,url =response.request.url )
                    return
                all = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "poem-excerpt", " " ))]//a')
                if len(all) <= 0:
                    all = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "part-title-block", " " ))]//a')
                if len(all) <= 0:
                    return
                for el in all:
                    url = self.ganjoor_page+el.css("::attr(href)").extract()[0]
                    yield scrapy.Request(url,method= "GET",callback=self.parse,cb_kwargs = {"mode":3,"file_path":
                    file_path})

        except:
            pass


