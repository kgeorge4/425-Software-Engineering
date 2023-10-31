import spacy
import pymongo
from pymongo import MongoClient
from spacy import displacy
from spacy_langdetect import LanguageDetector
from spacy.language import Language
from googletrans import Translator, constants
import json


# list of all possible languages from the text
langList = {
    "en": "English",
    "ro": "Romainian",
    "it": "Italian / latin",
    "lt": "Latin",
     "" : "Uknown"
}


def get_lang_detector(nlp, name):
    return LanguageDetector()


def codetoString(code):
    return langList.get(code)


# setup for spacy
spacy.prefer_gpu()
nlp = spacy.load("en_core_web_sm")
Language.factory("language_detector", func=get_lang_detector)
nlp.add_pipe('language_detector', last=True)

# init the Google API translator
translator = Translator()


# connection for mongoDB
client = MongoClient("mongodb://localhost:27017/") 
db = client["textStorage"]
collection = db["ulyssesChap1"]

# find document
document = collection.find_one({"_id": "chap1"})

# initialize categorized data to return to database
categorized = []


# read the category list from the database
categories = db["categories"]
categoryDB = categories.find_one()
categoryList = []

# read from category list and create key value pairs
for k,v in categoryDB.items():
    if(k == "_id"):
        continue
    else:
        categoryList.append(k)
        categoryList.append(v)

#print(categoryList[1])

# stores paragraph num
paragraphCtr = 1

# iterate over content
for paragraph in document["content"]:

    # paragraphBlocks containing sentences with categories
    paragraphBlock = {
        "num": paragraphCtr,
        "sentences": []
    }

    # if a sentence add to text
    if("sentences") in paragraph:
        
        # iterate accross each paragrah sentence
        for sentence in paragraph["sentences"]:
            # use catList to create dictionary for each sentence
            myDict = {}

            # find language that text is 
            doc = nlp(sentence["text"])
            langTag = doc._.language
            lang = codetoString(langTag["language"])

            # standard text and language categories
            myDict["text"] = sentence["text"]
            myDict["language"] = lang
            # translate if not english
            if(langTag["language"] != "en"):
                translation = translator.translate(sentence["text"], dest="en")
                myDict["translation"] = translation.text
            categoryList[1]["involves"] = []
            for ent in doc.ents:
                if( ent.label_ == "PERSON"):
                    categoryList[1]["involves"].append(ent.text)
            myDict.update(categoryList[1])

            paragraphBlock["sentences"].append(myDict)

    # append the paragraph block to the categorized data
    categorized.append(paragraphBlock)

    paragraphCtr += 1

categorizedData = {"data: ": categorized}

# use analysis collection
analysis_collection = db["analysis"]
analysis_collection.insert_one(categorizedData)


with open("categories.json", "w") as file:
    json.dump(categorized, file)

# initialize the DB with categories
print("categories generated.")




client.close()



