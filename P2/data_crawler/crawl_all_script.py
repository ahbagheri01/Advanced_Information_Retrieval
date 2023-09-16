import os
import json
from datetime import datetime
poems = json.load(open("../data/all_poets.json","r"))
for poem in poems:
    poem = poem.replace("/","")
    print(f"crawling {poem} started at {datetime.now()}")
    f = open("inputname.txt","w")
    f.write(poem)
    f.close()
    os.system(f"scrapy crawl -s LOG_FILE=log_{poem}.txt general_poet")
    print(f"crawling {poem} ended at {datetime.now()}")

