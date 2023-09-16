import os
from pathlib import Path
from sys import argv
from time import sleep

import requests
import json

class DataCollector:

    MORE_INFO_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9,fa-IR;q=0.8,fa;q=0.7',
        'Referer': 'https://www.semanticscholar.org/search?q=lstm&sort=relevance',
        'Content-Type': 'application/json',
        'Origin': 'https://www.semanticscholar.org',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin'
    }

    BASIC_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,fa-IR;q=0.8,fa;q=0.7',
        'Referer': 'https://www.semanticscholar.org/search?q=lstm&sort=relevance&pdf=true',
        'Content-Type': 'application/json',
        'Origin': 'https://www.semanticscholar.org',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin'
    }

    def __init__(self, subjects: list , n = 90 , lim = 100) -> None:
        self.subjects = subjects
        self.api_url = 'https://api.semanticscholar.org/graph/v1/paper/'
        self.n = n
        self.LIM = lim

    def collect_basic_info(self, subject , offset = 0,limit = 100) -> list:
        params = {
            "query": subject,
            "offset": offset,
            "limit": limit,
            "fields": 'paperId,abstract,title,authors,fieldsOfStudy,s2FieldsOfStudy'
        }

        url = self.api_url + 'search'
        response = requests.get(url=url, headers=self.BASIC_HEADERS, params=params)
        if not response.ok:
            print('failed to connect to %s with status %s' % (url, response.status_code))
            #raise ConnectionError('failed to connect to %s with status %s' % (url, response.status_code))
            return []
        try:
            papers = response.json()['data']
        except:
            return []
        sleep(5)
        return papers

    def collect_more_info(self, papers: list) -> list:
        all_fields = ['paperId', 'externalIds', 'url', 'title', 'abstract', 'venue', 'year', 'isOpenAccess', 'tldr',
         'referenceCount', 'citationCount', 'influentialCitationCount', 'fieldsOfStudy', 's2FieldsOfStudy',
         'embedding', 'citations.authors', 'citations.title', 'citations.url', 'citations.year', 'citations.fieldsOfStudy',
         'references.authors', 'references.title', 'references.url', 'references.year', 'references.fieldsOfStudy',
         'authors.authorId', 'authors.externalIds', 'authors.url', 'authors.name', 'authors.aliases', 'authors.affiliations',
         'authors.homepage', 'authors.paperCount', 'authors.citationCount', 'authors.hIndex']

        # recommended field set
        minimal_fields = ['paperId', 'title', 'abstract', 'venue', 'year', 'referenceCount', 'citationCount', 
        'influentialCitationCount', 'fieldsOfStudy', 's2FieldsOfStudy','citations', 'references', 'authors']

        minimal_fields_phase1 = ['paperId', 'title', 'abstract',
        'fieldsOfStudy', 's2FieldsOfStudy', 'authors']

        params = {
            "fields": ','.join(all_fields)
        }
        
        result_papers = []
        for paper in papers:
            url = self.api_url + str(paper['paperId'])
            response = requests.get(url, headers=self.MORE_INFO_HEADERS, params=params)
            if not response.ok:
                print('failed to connect to %s with status %s' % (url, response.status_code))
                sleep(20)
                #raise ConnectionError('failed to connect to %s with status %s' % (url, response.status_code))
            else:
                result = response.json()
                result_papers.append(result)
            sleep(4)
            
        return result_papers

    def collect(self):
        size_all = 0
        for subject in self.subjects:
            print(subject)
            all_papers = []
            for i in range(self.n):
                print(f"{subject} offset = {i*self.LIM}")
                basic_papers = self.collect_basic_info(subject,offset=i*self.LIM,limit=self.LIM)
                papers = self.collect_more_info(basic_papers)
                basic_papers = papers
                all_papers += basic_papers
                if len(basic_papers) <= 0:
                    break
                papers_dict = {item["paperId"]: item for item in all_papers}
                print(f"{subject} len in this query = {len(basic_papers)} len all = {size_all + len(papers_dict)}")
                print(f"{subject} sum = {len(basic_papers)} ")
                path = os.path.join(os.getcwd(), './data')
                Path(path).mkdir(parents=True, exist_ok=True)
                print(f"saving in {os.path.join(path, f'{subject}.json')}")
                with open(os.path.join(path, f'{"_".join(subject.strip().split(" "))}.json'), 'w') as f:
                    json.dump(papers_dict, f)
            papers_dict = {item["paperId"]: item for item in all_papers}
            path = os.path.join(os.getcwd(), './data')
            Path(path).mkdir(parents=True, exist_ok=True)
            print(f"saving end in {os.path.join(path, f'{subject}.json')}")
            with open(os.path.join(path, f'{"_".join(subject.strip().split(" "))}.json'), 'w') as f:
                json.dump(papers_dict, f)
            size_all += len(papers_dict)


if __name__ == "__main__":
    lim = 100
    n = int(10000/lim)-1
    data_collector = DataCollector(['transformers','Language Models','natural language processing transformers','NLP'], n = n , lim = lim)
    data_collector.collect()
    
