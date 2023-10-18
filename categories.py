import spacy
import pymongo
from pymongo import MongoClient
from spacy import displacy
from spacy.language import Language
from spacy_langdetect import LanguageDetector
from langdetect import detect

langList = {
    "en": "English",
    "ro": "Romainian",
    "it": "Italian",
    "lt": "Latin",
    "" : "Latin"
}


def codetoString(code):
    return langList.get(code)



spacy.prefer_gpu()
nlp = spacy.load("en_core_web_sm")

client = MongoClient("mongodb://localhost:27017/") 
db = client["textStorage"]
collection = db["ulyssesChap1"]

# find document
document = collection.find_one({"_id": "chap1"})

oneDoc = {
    "paragraphs": []
}


# stores paragraph num
paragraphCtr = 0

# iterate over content
for paragraph in document["content"]:

    paragraphBlock = {
        "num": paragraphCtr,
        "sentences": []
    }
    # if a sentence add to text
    if("sentences") in paragraph:
        # iterate accross each paragrah sentence
        for sentence in paragraph["sentences"]:
            # if sentence is in latin translate to english to make easier to understand
            #print(sentence)
            language = detect(sentence)
            lang = codetoString(language)
            sentenceBlock = {
                "text": sentence,
                "text-lang": lang
            }

            paragraphBlock["sentences"].append(sentenceBlock)

        oneDoc["paragraphs"].append(paragraphBlock)

    paragraphCtr += 1

# creates new analysis collection
analysis_collection = db["analysis"]
analysis_collection.insert_one(oneDoc)

print(oneDoc)

client.close()



