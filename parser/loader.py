import nltk, re
from nltk.tokenize import word_tokenize, sent_tokenize, blankline_tokenize
import pymongo
import json
from pymongo import MongoClient

# determines if line is a quote using regular expression search
def is_quote(line):
  quote = re.search('—([^"]*)', line)
  if(quote):
      return True
  else: 
      return False
    
"""
# first num is paragraph, second is sentence number
dataArr = []
"""

collection_name = "ulyssesChap1"
docID = "chap1"

# connecting to MongoDB server
client = MongoClient("mongodb://localhost:27017/") 
db = client["textStorage"]
collection = db[collection_name]


# Check if the collection exists before dropping it
if collection_name in db.list_collection_names():
    db[collection_name].drop()
    print(f"Collection '{collection_name}' has been dropped.")
else:
    print(f"Collection '{collection_name}' does not exist.")


# open chapter1 and read the text file to be parsed
with open("chap1", "r", encoding="utf-8") as file:
    results = file.read()

# tokenize into words with nltk
#words = word_tokenize(results)
# output tokens ( words derived from spaces and newlines )
#print(text_tokens)

"""
# better tokens of sentences after removing newlines
text = results.replace("\n", " ")
sentences = sent_tokenize(text)

"""
# split the text into paragraphs
paragraphs = blankline_tokenize(results)

"""
# print the sentences
for i , sentence in  enumerate (sentences, start=1):
    tagged_sentence = f"Sentence {i}: {sentence}"
    print(tagged_sentence)
"""
doc = {
    "_id": docID,
    "content": []
}

paragraphCtr = 0
sentenceCtr = 0
quoteCtr = 0


# iterate over paragraphs
for paragraph in paragraphs:


    # each paragraph gets numbered
    uniqueParagraph = f"{paragraphCtr}:{paragraph}"
    #print(uniqueParagraph)

    # break each paragraph into sentences
    sentences = sent_tokenize(paragraph)

    # holds sentences for mongoDB
    sentenceList = []

    # pass over each sentence in paragraph
    for sentence in sentences:

        # tags quotes
        if(is_quote(sentence)):
            numberedSentence = ' "'+ sentence + '" '
            quoteCtr += 1
        # tags sentences
        else:
            numberedSentence = sentence
            sentenceCtr += 1


        sentenceList.append(numberedSentence)
        #print(numberedSentence)
    documentData = {
        "paragraph" : paragraphCtr,
        "sentences" : sentenceList
    }

    # increment paragraph counter
    paragraphCtr += 1

    # add to current content
    doc["content"].append(documentData)
# inserts into mongoDB
collection.insert_one(doc)

# close client
client.close()