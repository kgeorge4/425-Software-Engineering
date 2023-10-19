import nltk, re
from nltk.tokenize import word_tokenize, sent_tokenize, blankline_tokenize
import pymongo
import json
from pymongo import MongoClient

TEXT_FILE = "chap1"

# determines if line is a quote using regular expression search
def is_quote(line):
  quote = re.search('—([^"]*)', line)
  if(quote):
      return True
  else: 
      return False

collection_name = "ulyssesChap1"
docID = "chap1"

# connecting to MongoDB server
client = MongoClient("mongodb://127.0.0.1:27017/") 
db = client["textStorage"]
collection = db[collection_name]


# Check if the collection exists before dropping it
if collection_name in db.list_collection_names():
    db[collection_name].drop()
    print(f"Collection '{collection_name}' has been dropped.")
else:
    print(f"Collection '{collection_name}' does not exist.")


# open chapter1 and read the text file to be parsed
with open(TEXT_FILE, "r", encoding="utf-8") as file:
    results = file.read()

# split the text into paragraphs
paragraphs = blankline_tokenize(results)

# initialize return document 
doc = {
    "_id": docID,
    "content": []
}


sentenceCtr = 1
paragraphCtr = 1


# iterate over paragraphs
for paragraph in paragraphs:

    paragraphList = []

    # break each paragraph into sentences
    sentences = sent_tokenize(paragraph)

    # pass over each sentence in paragraph
    for sentence in sentences:

        # tags quotes
        if(is_quote(sentence)):
            sentence = sentence.replace('—', '')
            sentence = '"' + sentence + '"'

        paragraphList.append({        
                                "sentenceNum": sentenceCtr,
                                "text": sentence
                            })
        #print(numberedSentence)
        sentenceCtr+=1

    # add to current nested block
    documentData = {
        "paragraphNum" : paragraphCtr,
        "sentences" : paragraphList
    }

    # increment paragraph counter
    paragraphCtr += 1

    # add to current content
    doc["content"].append(documentData)

# inserts into mongoDB
collection.insert_one(doc)

with open("organizedParagraphs.json", "w") as file:
    json.dump(doc, file)

print(f"Collection '{collection_name}' has been rebuilt.")

# close client
client.close()
