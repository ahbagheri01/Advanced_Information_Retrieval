from __future__ import unicode_literals
import pandas as pd
from hazm import *
import pandas as pd
import re
from termcolor import colored
import pandas as pd
from hazm import *
import pandas as pd
import re
from termcolor import colored
class Vehicle_detector:
    def __init__(self):
        self.mode = True
        print(colored("loading model ... ","blue"))
        self.normalizer = Normalizer()
        self.lemmatizer = Lemmatizer()
        self.stemmer = Stemmer()
        print(colored("loading tagger ... ","blue"))
        self.tagger = POSTagger(model='./resources/postagger.model')
        print(colored("loading chuncker ... ","blue"))
        self.chunker = Chunker(model='resources/chunker.model')
        print(colored("reading dataset ... ","blue"))
        self.vehicles = {s : True  for s in pd.read_csv("resources/vehicles_final.csv")["vehicles"].unique()}
        self.places = {s : True  for s in pd.read_csv("resources/places.csv")["place"].unique()}
        f = open("resources/dest_verbs.txt","r",encoding = "utf-8")
        self.dest_verbs = [l.strip() for l in f.readlines()]
        f.close()
        print(colored("loading regex ... ","blue"))
        self.NP_regex = "\[[^\[]* NP\]"
        self.VP_regex = "\[[^\[]* VP\]"
        self.After_ba = "(\\S+)?" + "( |\u200c)"
        self.BA = "با"
        self.SPAN_finder = "(\\S+)?" + "(" + " " + "|" + "‌" + ")"
        self.AZ_source = "از (\\S+)( )?"
        self.BE_dest = "به (\\S+)( )?"
        self.FIND_BY_verb = "("
        size = len(self.dest_verbs)-1
        for verb in range(size):
            v = self.dest_verbs[verb].strip()
            self.FIND_BY_verb = self.FIND_BY_verb+ v+"|"
        self.FIND_BY_verb = self.FIND_BY_verb+self.dest_verbs[size]+") "+"(\\S+)"
        self.VEHICLE_REGEX = "( )?("
        for key in self.vehicles:
            self.VEHICLE_REGEX = self.VEHICLE_REGEX + key+"|"
        self.VEHICLE_REGEX = self.VEHICLE_REGEX[0:-1]+")( |شان|تان|مان|اش|ام|ت|م|ش)?"
        print(colored("loading completed","blue"))

    def get_analysis(self,token, mode = 0):
        assert 0 <= mode < 5 ,"0  <= mode < 5"
        if mode == 0:
            return self.lemmatizer.lemmatize(token)
        if mode == 1:
            return self.stemmer.stem(token)
        if mode == 2:
            return self.normalizer.normalize(token)
        if mode == 3:
            return sent_tokenize(self.normalizer.normalize(token))
        if mode == 4:
            return word_tokenize(token)
    def ste_lem(self,sentence , mode = 0):
        assert 0 <= mode <= 1 ,"mode 1 or 0"
        return [self.get_analysis(s,1-mode) for s in sentence]

    def find_NP(self,chunked_tree):
        res = re.findall(self.NP_regex, chunked_tree)
        return [" ".join([self.get_analysis(w) for w in word[1:-4].strip().replace("\u200c", " ").split()]).strip() for word in res]

    def find_VP(self,chunked_tree):
        res = re.findall(self.VP_regex, chunked_tree)
        return [" ".join([self.get_analysis(w) for w in word[1:-4].strip().replace("\u200c", " ").split()]).strip() for word in res]

    def find_vehicles_each(self,word):
        if self.vehicles.get(word):
            return word
        else:
            False
    def set_mode(self,mode):
        self.mode = mode

    def take_apart_words(self,sen):
        candidate_words = []
        for i in sen:
            if len(i.split()) >= 1:
                strr = ""
                splitted_words = i.split()
                longest_accepted_word = ""
                for j in splitted_words:
                    strr += j
                    if self.find_vehicles_each(strr):
                        longest_accepted_word = strr
                    strr += " "
                if longest_accepted_word:
                    candidate_words.append(longest_accepted_word.strip())
        return candidate_words

    def check_is_vehicle_after_ba(self,vehicles, sen):
        checked_vehicles = []
        spans = []
        possible = []
        for vehicle in vehicles:
            vehicle_parts = vehicle.split()
            regex = self.BA+" "
            size = len(vehicle_parts)-1
            for index,part in enumerate(vehicle_parts):
                regex += (part + self.After_ba) if  index != size else part
            regex = regex.strip()
            x = re.search(regex, sen)
            if x:
                start, end = x.span()
                checked_vehicles.append(vehicle)
                spans.append((start+3,end))
            x = re.search(regex[3:], sen)
            if x:
                start, end = x.span()
            possible.append((vehicle,start,end))
            
        return checked_vehicles,spans,possible 

    def find_vehicles(self,sen):
        words = self.take_apart_words(sen)
        if len(words) == 0:
            pass
        return words

    def find_spans(self,NP_Ws, sen: str):
        copy_sen = sen
        base = 0
        spans = []
        for NP_W in NP_Ws:
            NP_W_parts = NP_W.split(" ")
            regex = ""
            size = len(NP_W_parts)-1
            for index,part in enumerate(NP_W_parts):# "(\\S+)?" + "(" + " " + "|" + "‌" + ")"
                regex += (part + self.SPAN_finder) if index != size else part
            
            regex = regex.strip()
            x = re.search(regex, copy_sen)
            start, end = x.span()
            spans.append((NP_W, start + base, end + base))
            copy_sen=copy_sen[end:]
            base = base + end
        return(spans)    

    def check_places(self,sen, NP_W_span):
        sources = []
        destinations = []
        source = re.search(self.AZ_source, sen)
        if source:
            posibble_source_start, posibble_source_end = source.span(1)
            for NP_W in NP_W_span:
                if (NP_W[1] <= posibble_source_start <= posibble_source_end <= NP_W[2] or NP_W[1] == posibble_source_start):
                    sources.append(NP_W)
                    break

        destination = re.search(self.BE_dest, sen)
        if destination:
            posibble_destination_start, posibble_destination_end = destination.span(1)
            for NP_W in NP_W_span:
                if (NP_W[1] <= posibble_destination_start <= posibble_destination_end <= NP_W[2] or NP_W[1] == posibble_destination_start):
                    destinations.append(NP_W)
                    break
        if len(destinations) == 0:
            destination = re.search(self.FIND_BY_verb, sen)
            if destination:
                s, e = destination.span(2)
                if sen[e-1] == ".":
                    e = e-1
                destinations.append((sen[s:e],s,e)) #TODO check by amirmahdi
        if len(destinations) == 0:
            destinations = [("",-1,-1)]
        if len(sources) == 0:
            sources = [("",-1,-1)]
        return sources[0], destinations[0] 
    def create_output(self,source = "",s_span = (-1,-1),dest = "",dest_span = (-1,-1),vehicle = "",vehicle_span = (-1,-1)):
        return {
            "from":source,
            "from_span":s_span,
            "to":dest,
            "to_span":dest_span,
            "vehicle":vehicle,
            "vehicle_span":vehicle_span
        }

    def run(self,input:str):
        outputs = []
        for ind, sen in enumerate(self.get_analysis(input, 3)): 
            output = {} 
            try:
                sentence = self.get_analysis(sen, 4)  
                chunked = self.chunker.parse(self.tagger.tag(sentence))
                tree = tree2brackets(chunked)
                NP_W = self.find_NP(tree)
                NP_W_span=self.find_spans(NP_W,sen)
                posibble_vehicles = self.find_vehicles(NP_W)
                checked_vehicles,spans,posibble_vehicles = self.check_is_vehicle_after_ba(posibble_vehicles, sen)
                if len(checked_vehicles) > 0: #TODO check by amir mahdi 
                    v = checked_vehicles[0]
                    v_s = spans[0]
                    source, destination =self.check_places(sen,NP_W_span)
                    output = self.create_output(
                        source=source[0],
                        s_span=(source[1],source[2]),
                        dest=destination[0],
                        dest_span=(destination[1],destination[2]),
                        vehicle=v,
                        vehicle_span=v_s
                    )
                elif len(posibble_vehicles) > 0:
                    v = posibble_vehicles[0][0]
                    v_s = (posibble_vehicles[0][1],posibble_vehicles[0][2])
                    if self.mode:
                        source, destination =self.check_places(sen,NP_W_span)
                        output = self.create_output(
                            source=source[0],
                            s_span=(source[1],source[2]),
                            dest=destination[0],
                            dest_span=(destination[1],destination[2]),
                            vehicle=v,
                            vehicle_span=v_s
                        )
                    else:
                        output = self.create_output(
                            vehicle=v,
                            vehicle_span=v_s
                        )
                else:
                    output = self.create_output()
                    v = re.search(self.VEHICLE_REGEX, sen) #TODO
                    if v:
                        s, e = v.span(2)
                        if s > 2 and sen[s-3:s-1] == self.BA and e-s > 2:
                            source, destination =self.check_places(sen,NP_W_span)
                            output = self.create_output(
                            source=source[0],
                            s_span=(source[1],source[2]),
                            dest=destination[0],
                            dest_span=(destination[1],destination[2]),
                            vehicle=sen[s:e],
                            vehicle_span=(s,e)
                            )
                        elif e-s > 1:
                            if self.mode:
                                source, destination =self.check_places(sen,NP_W_span)
                                output = self.create_output(
                                source=source[0],
                                s_span=(source[1],source[2]),
                                dest=destination[0],
                                dest_span=(destination[1],destination[2]),
                                vehicle=sen[s:e],
                                vehicle_span=(s,e)
                                )
                            else:
                                output = self.create_output(
                                vehicle=sen[s:e],
                                vehicle_span=(s,e)
                                )
            except:
                output = self.create_output()
            outputs.append(output)

        return outputs
