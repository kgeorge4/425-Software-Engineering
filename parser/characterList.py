import spacy

import pymongo

import langdetect

import googletrans

import nltk

import pycountry

from pymongo import MongoClient

from spacy import displacy

from langdetect import detect_langs

from langdetect import DetectorFactory

from googletrans import Translator

from nltk.stem import SnowballStemmer

DetectorFactory.seed = 42

nltk.download('crubadan')

def is_latin(text):
    tc = nltk.classify.textcat.TextCat() 
    guess_one = tc.guess_language(text)


    guess_one_name = pycountry.languages.get(alpha_3=guess_one).name 
    print(guess_one_name)
	#if(langdetect.detect(text) != "en"):
	#	return True
	#return False

spacy.prefer_gpu()

nlp = spacy.load("en_core_web_sm")

#latin_nlp = spacy.load('la_core_web_lg')

client = MongoClient("mongodb://localhost:27017/") 

db = client["textStorage"]

collection = db["ulyssesChap1"]

translator = Translator()

# find document

document = collection.find_one({"_id": "chap1"})



# rebuild sentences

text = []

# iterate over content
for paragraph in document["content"]:
    # if a sentence add to text
    if("sentences") in paragraph:
        # iterate accross each paragrah sentence
        for sentenceBlock in paragraph["sentences"]:
            # tag sentence to find what language it is
            sentence = sentenceBlock["text"]
            # build text list
            text.append(sentence)


combination = '\n'.join(text)



doc = nlp(combination)

for ent in doc.ents:
	if( ent.label_ == "PERSON"):
		 print(ent.text, ent.label_)


client.close()



"""

text2= nlp(doc)

for word in text2.ents:

    print(word.text,word.label_)"""

