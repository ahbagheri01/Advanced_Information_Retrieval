import os

WAITTIME = 15
import json
import time
import requests
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
baseadd = ""

class sel_crawl:
    def __init__(self):
        self.id = 1
        fireOptions = Options()
        fireOptions.headless = False
        user_agent = 'I LIKE CHOCOLATE'
        fireOptions.add_argument(f'user-agent={user_agent}')
        # self.driver = webdriver.Chrome()
        self.driver = webdriver.Firefox(options=fireOptions)

    class infinite_scroll(object):
        def __init__(self, last):
            self.last = last

        def __call__(self, driver):
            new = driver.execute_script('return document.body.scrollHeight')
            if new > self.last:
                return new
            else:
                return False

    def scroll_until_end(self, mydriver):
        last_height = mydriver.execute_script('return document.body.scrollHeight')
        flag = 1
        while flag == 1:
            #print("scrolling")
            mydriver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
            try:
                wait = WebDriverWait(mydriver, WAITTIME)
                new_height = wait.until(self.infinite_scroll(last_height))
                last_height = new_height
            except:
                print("End of page reached")
                flag = 0
    def parse2(self,driver,address):
        pass



    def parse(self, address, name ,num=0, SCROLL_PAUSE_TIME=0.5):
        data = ""
        driver = self.driver
        for i in range(1,9):
            driver.get(f"{address}?page={i}")
            self.scroll_until_end(driver)
            WebDriverWait(driver, 20)
            print("clicked and scrolled seccoessfully")
            try:
                #element = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, '//*[(@id = "footer-info-lastmod")]')))
                print("founded")
            except:
                pass
            all_el = driver.find_elements_by_xpath('//*[(@id = "app")]//*[contains(concat( " ", @class, " " ), concat( " ", "font__bold", " " ))]//span')
            print(len(all_el))
            for el in all_el:
                #print(el.text)
                data += el.text +"\n"
        f = open(f"../data/{name}.txt","w",encoding="utf-8")
        f.write(f"crawled from {address} \n"+data)
        f.close()

crawl = sel_crawl()
#crawl.parse("https://www.ikco.ir/fa/productlist.aspx",name = "vehicle3.txt")
#crawl.parse("https://fa.wikipedia.org/wiki/%D9%81%D9%87%D8%B1%D8%B3%D8%AA_%D8%B4%D9%87%D8%B1%D9%87%D8%A7%DB%8C_%D8%A7%DB%8C%D8%B1%D8%A7%D9%86",name="iran_cities_better")
crawl.parse("https://car.ir/iran-khodro",name = "vehicle3.txt")

