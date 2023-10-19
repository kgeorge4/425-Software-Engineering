import spacy
import pymongo
from pymongo import MongoClient
from spacy import displacy
from spacy_langdetect import LanguageDetector
from spacy.language import Language
from langdetect import detect
import json

langList = {
    "en": "English",
    "ro": "Romainian",
    "it": "Italian",
    "lt": "Latin",
    "" : "Uknown"
}


def codetoString(code):
    return langList.get(code)


# setup for spacy
spacy.prefer_gpu()
nlp = spacy.load("en_core_web_sm")

# connection for mongoDB
client = MongoClient("mongodb://localhost:27017/") 
db = client["textStorage"]
collection = db["ulyssesChap1"]

# find document
document = collection.find_one({"_id": "chap1"})

# initialize categorized data to return to database
categorized = []

# stores paragraph num
paragraphCtr = 1

# iterate over content
for paragraph in document["content"]:

    paragraphBlock = {
        "num": paragraphCtr,
        "sentences": []
    }
    # if a sentence add to text
    if("sentences") in paragraph:
        # iterate accross each paragrah sentence
        for sentenceBlock in paragraph["sentences"]:
            # tag sentence to find what language it is
            sentence = sentenceBlock["text"]

            language = detect(sentence)
            lang = codetoString(language)

            paragraphBlock["sentences"].append({
                "text": sentence,
                "text_meaning": None,
                "language": lang,
                "text_type": None,
                "narrator": None,
                "indications": [],
                "involves":[],
                "spoken_by": None,
                "spoken_to": None
            })

    # append the paragraph block to the categorized data
    categorized.append(paragraphBlock)

    paragraphCtr += 1

categorizedData = {"data: ": categorized}

# creates new analysis collection
analysis_collection = db["analysis"]
analysis_collection.insert_one(categorizedData)


with open("categories.json", "w") as file:
    json.dump(categorized, file)


print("categorized data.")


client.close()




