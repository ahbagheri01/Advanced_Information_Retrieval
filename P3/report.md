
## Amirhossein Bagheri 98105621
## Mohammad Sadegh majidi Yazdi  98106004
## Amirmahdi kousheshi 98171053

# you can download all files and model (if you don't want to run pre_process.ipynb and clone fasttes from <a href="https://drive.google.com/file/d/1W_ciumGSAkB8cPoYK5KNJXTKqxNo-SME/view?usp=sharing" title="MODELS">here</a>)

# data 

All data are crawled from api given to us code is in path = ./DATA/crawler

about 8k article is crawled with 4 fields

1. abstract
2. title
3. authors
4. hash data from website

data are crawed with api 
```py

 def collect(self):
        size_all = 0
        for subject in self.subjects:
            print(subject)
            all_papers = []
            for i in range(self.n):
                print(f"{subject} offset = {i*self.LIM}")
                basic_papers = self.collect_basic_info(subject,offset=i*self.LIM,limit=self.LIM)
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
```
and here is basic headers and parameters for this crawling part:

```py
params = {
            "query": subject,
            "offset": offset,
            "limit": limit,
            "fields": 'paperId,abstract,title,authors'
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
```
code above shows how we crawl data from api




# PreProcess
+ we use spacy lemmatization for our purpose

then we create files needed for next stages
we create some mapping from hash data to number from number to article and authors for convenience of process.


# 1.Boolean

Two kinds of query for titles and authors 
distance is lemmatized words occurrences 

for names we didn't use lemma or any kind of preprocess.

we use nltk tokenizer as preprocess for names
and we use spacy lemma for titles

first we load some basic files that we need.
## for all models this part is done so we won't repeat this again for all parts
```py
class Boolean_IR:
    def __init__(self):
        self.author_to_id = json.load(open("DATA/Module_data/author_to_id.json","r"))
        self.author_to_doc = json.load(open("DATA/Module_data/author_to_doc.json","r"))
        self.authorid_to_num_id = json.load(open("DATA/Module_data/authorid_to_num_id.json","r"))
        self.documents = json.load(open("DATA/crawler/data/NLP.json","r"))
        self.lemma_title = json.load(open("DATA/Module_data/title_lemma.json","r"))
        self.bool_dic_title = json.load(open("DATA/Module_data/bool_dic_title.json","r"))
        self.nlp = spacy.load("en_core_web_sm")
        self.title_tokenizer = lambda s : [token.lemma_ for token in self.nlp(s) if token.lemma_ not in self.nlp.Defaults.stop_words ]
```
then we have preprocess function which will do some work on jsons and also creates mapping for authors name.
```py
    def pre_process_authors(self) -> None:
        self.all_names = list(set(self.flatten([self.word_tokenize_authoe(key) for key in self.author_to_id if not is_int(key)])))
        i = iter(range(1,len(self.all_names)+1))
        self.w_mapping = defaultdict(lambda : next(i))
        self.bool_dic_author = defaultdict(lambda : [])
        list(map(lambda x : self.w_mapping[x],self.all_names))
        removed_key = []
        for key in self.author_to_id:
            if not is_int(key) and is_int(self.author_to_id[key]) and key:
                i = self.author_to_id[key]
                self.bool_dic_author[i] = np.array([self.w_mapping[w] for w in self.word_tokenize_authoe(key)])
            else:
                removed_key.append(key)
        for x in removed_key:
            del self.author_to_id[x]
    def pre_process_title(self) -> None:
        for key in self.bool_dic_title:
            self.bool_dic_title[key] = np.array(self.bool_dic_title[key])
```
for title we first find indexed words of query then we loop over all datas and see how much overlap they have with query and sort them then return first k.
```py       
    def title_ir(self,wk:str , k : int = 10):
        words = np.array([self.lemma_title.get(w,0) for w in wk])
        titles = [(key,np.sum([np.sum([item == self.bool_dic_title[key] for item in words ])])) for key in self.documents if type(self.documents[key]["title"]) == str]
        return sorted(titles , key = lambda x : x[1],reverse=True)[:k]
```
for author is ssame process as title
```py

    def author_ir(self,input_wk:str,k) -> List:
        names_map = np.array([self.w_mapping.get(w,0) for w in input_wk])
        authors = [(key,np.sum([np.sum([name == self.bool_dic_author[self.author_to_id[key]] for name in names_map ])])) for key in self.author_to_id]
        return sorted(authors , key = lambda x : x[1],reverse=True)[:k]
```

# 2.TF IDF RAW  
representation of every sentence is tf-idf matrix row
for every query after lemmatization here is how score is calculated and will be shown sorted from highest score to lowest
$$ score(q,d)  = \sum_{w \in (d \cap q)} {log(1+tf(w,d) * log(\frac{|D|}{df(w)}))} $$ 
we use spacy lemma as preprocess

here is all code you need. we calculate $$ score(q,d)  = \sum_{w \in (d \cap q)} {log(1+tf(w,d) * log(\frac{|D|}{df(w)}))} $$ 
and then just sort.
```py
    def process_q(self,q : List , tf , idf , k) -> List[Tuple]:
        return sorted([(key,sum([tf[key].get(wq,0) * idf.get(wq,0) for wq in q])) for key in tf], key = lambda x : x[1] , reverse=True)[:k]
```
# 3.Transformers
for this purpose we use sentence transformer
models are based on bert structure but are trained on differrent dataset we use all-MiniLM-L12-v2 this model is trained on all data over 1 billion.
we also store representation

we use spacy lemma as preprocess

after loading pretrained model here is all code you need 
we encode input with model. then just calculate distance.cosine for each doc vector and then output is sorted and k first are what we want.  
```py
def query(self,input_str:str , k = 10):
q = self.model.encode(input_str)
article_id = sorted([(key,np.abs(distance.cosine(q,self.representation[key]))) for key in self.representation],key = lambda x : x[1])[:k]
article =  [self.documents[id[0]] for id in article_id]
return (article_id,article)
```

# ft_idf coef for representation

we use fasttext and train it on all data you can set parameters dim, epoch, lr , ws
then we calculate each representation for docs with idf of each words multiple to vector of that word but notice that we use softmax before applying coefs.

then each query will be converted to vector space and cosine_distance will decide wether it is revelant or not and how much. then we sort them based on cosine dist and show results.


we use spacy lemma as preprocess


after we load all model requirements like fasttext embedded vectors and docs vectors here is all you need.
first you should calculate matrix for each word in query.
then you will have matrix with shape $ (\#words,dim) $  then multiply softmax coef of each to this matrix 
$$ coef_{1,\#word} * embed\_matrix_{\#words,dim} = vec_{1,dim} $$
then find k nearest vector to this vector as result.
```py
def process_q(self,q : np.array) -> List[Tuple]:
    return sorted([(key,np.abs(distance.cosine(q,self.doc_emb[key]))) for key in self.doc_emb],key = lambda x : x[1])
    

def query(self, input_string:str , k : int = 10) -> List:
    word = self.tokenizer(input_string.strip().lower())
    matrix = np.array([self.emmbeding[w] for w in word if self.is_c_(w)]).reshape(-1,self.dim)
    c = self.c_soft(np.array([self.idf.get(self.mapping.get(w,0),0) for w in word if self.is_c_(w)]).reshape(1,-1))
    q = np.matmul(c,matrix)[0]
    article_id = self.process_q(q)[:k]
    articles = [self.documents[id[0]] for id in article_id]
    return (article_id,articles)
```
each member of group have done task independently 
+ notice that only two models are capable of comparison because their type of queries are the same trasnformer and tf_idf_feature_vec so here are result.

for results in doc we have set hash id of article 

# MRR evaluation
xlsx link is <a href="https://docs.google.com/spreadsheets/d/1DIDnzW32bWdCsABWgd4-LD00E8e5C8ubHq3REmE-kis/edit?usp=sharing" title="MRR">MRR Link</a>

if you want to see article by hash go to 
```c
/DATA/pre_process.ipynb
```
then run these cell.
```py
import json
import os
import pandas as pd
source = "./crawler/data"
from collections import defaultdict
lang_data = json.load(open(f"{source}/NLP.json"))
all_artcile_data = lang_data
article = all_artcile_data["hash id"]
print(article["title"])
print()
print(article["abstract"])
print()
print(article["authors"])
```


### boolean
for boolean 3 authors and 7 titles are tested  note that for names the accuracy is great because 
if name exist we will find it if not we won't and contexual meaning and any other deeper level of meaning. that's why average for this part is 0.699 
+ note that queries here are very easy because we are not searching on meaning or contexual area or any deeper level.

### tf_idf
for this part queries are again easy because it is still in similarity in appearance (visible likeness)

so here are result 0.803 this is best results in all of our result but note that queries are not as complicated as part 3 and 4

### trasnformer 
here first 5 queries are from data set abtracts but <b> other 5</b>
are from internet for subjects and they are not in data set but what they are talking is in the data set

so you can see that they are complicated 

here is result 0.597

### ft_idf coef for representation 
here first 5 queries are from data set abtracts but <b> other 5</b>
are from internet for subjects and they are not in data set but what they are talking is in the data set

so you can see that they are complicated <b>queries are same as previous models </b> 

here is result 0.593

+ note that first of all. transformer is not fine tuned that's probably why it is not better than fourth method if we tune this model on our data that obvoius that result would be better (that's   the goal for using transformer) but TA said it is not needed to fine tune this model so just used this.


