from math import e
from platform import release
from statistics import mode
from urllib import response
from urllib.parse import quote, unquote

import scrapy
import json
import pandas as pd

class Ghazzali(scrapy.Spider):
    name = "machine_name"
    first_page = "https://ganjoor.net/ghazzali"
    kimia_saadat_page = "https://ganjoor.net/ghazzali/kimia"
    list_kimia = ["onvan","arkan"]
    store_path = "../data/ghazzali"
    output = ""
    not_crawled = {}
    def get_text(self,elems,mode = 1):
        if mode == 1:
            elems =elems.xpath("//p")
        res = ""
        for i,elem in enumerate(elems):
            res =res+elem.css("::text").get()+"\n"
        return res


    def start_requests(self):
        url = self.first_page
        yield scrapy.Request(url=url, callback=self.parse,cb_kwargs = {"mode":1,"file_path":
            f'{self.store_path}/ghazzali.txt'}) 
        dibache = self.kimia_saadat_page+"/"+"dibache"
        print(dibache)
        for i in range(1,4):
            yield scrapy.Request(dibache+"/sh"+str(i),method= "GET",callback=self.parse,cb_kwargs = {"mode":2,"file_path":
            f'{self.store_path}/ghazzali.txt'
            })

        for kim in self.list_kimia:
            url = self.kimia_saadat_page+"/"+kim
            print("url 2 level ",url)
            yield scrapy.Request(url,method= "GET",callback=self.parse,cb_kwargs = {"mode":3,"file_path":
            f'{self.store_path}/ghazzali.txt'
            })
        print("end")
        #self.write_to_file( f'{self.store_path}/ghazzali.txt',self.output)
            

        
    def parse_first_page(self, response):
        output = {}
        res = ""
        res = self.get_text(response.xpath('//*[(@id = "garticle")]//p'),mode = 0)
        output["introduction"] = res
        file = open(f'{self.store_path}/main_page.txt', 'w', encoding='utf-8')
        to_write = res
        file.write(to_write)
        file.close()
    
    def write_to_file(self,file_name,txt):
        file = open(file_name, 'w', encoding='utf-8')
        to_write =txt
        file.write(to_write)
        file.close()
    
    # def parse_mode3(self,response):
    #     print("mode3 , ",response,self.output)
    #     all = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "part-title-block", " " ))]//a')
    #     print(len(all))
    #     for el in all:
    #         url = "https://ganjoor.net"+el.css("::attr(href)").extract()[0]
    #         print(url)
    #         yield scrapy.Request(url,method= "GET",callback=self.parse,cb_kwargs = {"mode":4,"file_path":
    #         f'{self.store_path}/ghazzali.txt'
    #         })

    # def parse_mode4(self,response):
    #     print("mode4")
    #     all = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "poem-excerpt", " " ))]//a')
    #     print(len(all))
    #     for el in all:
    #         url = "https://ganjoor.net"+el.css("::attr(href)").extract()[0]
    #         print(url)

    #         scrapy.Request(url,method= "GET",callback=self.parse,cb_kwargs = {"mode":5,"file_path":
    #         f'{self.store_path}/ghazzali.txt'
    #         })

    # def parse_mode5(self,response):
    #     print("mode5")
    #     all = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "poem-excerpt", " " ))]//a')
    #     print(len(all))
    #     for el in all:
    #         url = "https://ganjoor.net"+el.css("::attr(href)").extract()[0]
    #         print(url)

    #         scrapy.Request(url,method= "GET",callback=self.parse,cb_kwargs = {"mode":2,"file_path":
    #         f'{self.store_path}/ghazzali.txt'
    #         })

    def parse_mode2(self,response,file_path):
        print("mode2 : ",response)
        try:
            res = self.get_text(response.xpath('//*[(@id = "garticle")]//p'),mode = 0) 
            self.output += res
            self.write_to_file( file_path,self.output)
        except:
            print(e)
    
    def parse(self, response,mode,file_path):
        try:
            if mode == 1:
                print(mode,response)
                self.parse_first_page(response=response)
            elif mode == 2:
                print(mode,response)
                self.parse_mode2(response=response,file_path=file_path )
            elif mode == 3:
                print(mode,response)
                all = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "part-title-block", " " ))]//a')
                
                for el in all:
                    url = "https://ganjoor.net"+el.css("::attr(href)").extract()[0]
                    yield scrapy.Request(url,method= "GET",callback=self.parse,cb_kwargs = {"mode":4,"file_path":
                    f'{self.store_path}/ghazzali.txt'
                    })
                #self.parse_mode3(response=response)
                #self.logger.info(f"loglog : {response}")
                print(mode,response)
            elif mode == 4:
                print(mode,response)
                all = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "poem-excerpt", " " ))]//a')
                print(len(all))
                for el in all:
                    url = "https://ganjoor.net"+el.css("::attr(href)").extract()[0]
                    print(url)
                    yield scrapy.Request(url,method= "GET",callback=self.parse,cb_kwargs = {"mode":2,"file_path":
                    f'{self.store_path}/ghazzali.txt'
                    })

                #self.parse_mode4(response=response)
            elif mode == 5:
                print(mode,response)
                #self.parse_mode5(response=response)
                self.parse_mode2(response=response,file_path=file_path)
        except:
            print(e)