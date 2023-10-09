import spacy
import pymongo
from pymongo import MongoClient
from spacy import displacy

spacy.prefer_gpu()
nlp = spacy.load("en_core_web_sm")

client = MongoClient("mongodb://localhost:27017/") 
db = client["textStorage"]
collection = db["ulyssesChap1"]

# find document
document = collection.find_one({"_id": "chap1"})

paragraph1 = document["content"][3]
sentence1 = paragraph1["sentences"][0]

print(sentence1)

"""
text2= nlp(doc)
for word in text2.ents:
    print(word.text,word.label_)"""