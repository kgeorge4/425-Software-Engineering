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

# rebuild sentences
text = []

# iterate over content
for paragraph in document["content"]:

    # if a sentence add to text
    if("sentences") in paragraph:
        # iterate accross each paragrah sentence
        #for sentence in paragraph["sentences"]:
            # if sentence is in latin translate to english to make easier to understand
        text.extend(paragraph["sentences"])
        text.append("-------------------------------")


combination = '\n'.join(text)
#print(combination)

characterList = set([])

doc = nlp(combination)
for ent in doc.ents:
      if(ent.label_ == "PERSON"):
           characterList.add(ent.text)
      #print(ent.text, ent.label_)

print(characterList)

client.close()


"""
text2= nlp(doc)
for word in text2.ents:
    print(word.text,word.label_)"""
