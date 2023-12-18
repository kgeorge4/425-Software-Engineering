# Jeff Kretschmer and Burke Landon

import spacy
import pymongo
from nltk.tokenize import TreebankWordTokenizer as twt
from pymongo import MongoClient
from spacy import displacy
from spacy_langdetect import LanguageDetector
from spacy.language import Language
from googletrans import Translator, constants
import json
import nltk, re
from nltk.tokenize import word_tokenize, sent_tokenize, blankline_tokenize
import sys, os



# main file to take in the text from user input, load into database with chapter separators and then create analysis categories
# the name of text file will be used to denote where it is stored in the database

def removeFileExtension(file_name):
    # Split the file name and extension
    base_name, extension = os.path.splitext(file_name)

    # Check if the extension is ".txt" (case insensitive) and remove it
    if extension.lower() == ".txt":
        new_file_name = base_name
        return new_file_name
    else:
        # If the extension is not ".txt", return the original file name
        return file_name
    

######## Global text name #########
TEXT_PATH = sys.argv[2]         # will be modified based on file upload
TEXT_NAME = removeFileExtension(TEXT_PATH.split("/")[-1])



#################################################################################
# first step is to break apart the text into chapters

def split_into_chapters_with_content(text):
    # Define regular expression patterns for chapter identifiers
    chapter_patterns = [
        r'\[ [IVXLCDM]+ \]',  # e.g., [ I ], [ II ], [ III ], etc.
        r'\[ [0-9]+ \]',      # e.g., [ 1 ], [ 2 ], [ 3 ], etc. (numbers within square brackets)
        r'[IVXLCDM]+(?=\s)',  # e.g., I, II, III, etc. (Roman numerals)
        r'[A-Z]+(?=\s)+\n',      # e.g., CHAPTER, SECTION, PART, etc. (all caps)
    ]

    # Combine patterns into a single regular expression
    combined_pattern = '|'.join(f'({pattern})' for pattern in chapter_patterns)

    # Split the text into chapters using the regular expression
    chapters = re.split(combined_pattern, text)

    # Filter out empty strings and remove leading/trailing whitespace
    chapters = [chapter.strip() for chapter in chapters if chapter is not None and chapter.strip()]

    # Create a list of tuples with chapter titles and their corresponding content
    chapter_list = []
    i = 0
    while i < len(chapters):
        title = chapters[i].strip()

        i += 1
        content = []

        while i < len(chapters) and not re.match(combined_pattern, chapters[i]):
            content.append(chapters[i].strip())
            i += 1

        if title and content:  # Ignore empty titles and empty content
            chapter_tuple = (title, ', '.join(content))
            chapter_list.append(chapter_tuple)

    return chapter_list


# gets number of chapters from the text
def getChapters(fileName):

    # open chapter1 and read the text file to be parsed
    # requires the text to be split into chapters
    with open(fileName, "r", encoding="utf-8") as file:
        plainText = file.read()

    #print(plainText)

    result = split_into_chapters_with_content(plainText)

    #close text file
    file.close()

    if(result):
        return result
    else:
        return [("",plainText)]



# first index is the chapter name
# second index is the chapter content
# len(TEXT_CONTENT) gives number of chapters
TEXT_CONTENT = getChapters(TEXT_PATH)

numberOfChapters = (len(TEXT_CONTENT))



######################################################################################
# next step is to load into database under the textStorage database
# the collection name comes from the file
# each document in that collection will be named "TEXT_NAME + chapterNum" (no spaces)


# must be retrieved from file upload, and passed into this file
# name of file upload will denote where the document is stored inside the database
collection_name = TEXT_NAME
docID = TEXT_NAME
# GLOBAL

# determines if line is a quote using regular expression search
def is_quote(line):
  quote = re.search('—([^"]*)', line)
  if(quote):
      return True
  else: 
      return False

# connecting to MongoDB server
# all files are stored in the textStorage db
client = MongoClient("mongodb://127.0.0.1:27017/") 
db = client["textStorage"]
collection = db[TEXT_NAME]



# will drop and rewrite if the file exists already
# Check if the collection exists before dropping it
if collection_name in db.list_collection_names():
    db[collection_name].drop()
    print(f"Text collection '{collection_name}' has been dropped.")
    print("Rebuilding ...")
else:
    print(f"Creating new collection for {collection_name}.")



# file opened above and use the tuple called textContent
# requires the text to be split into chapters
# TEXT_CONTENT variable holds the tuple of text that will be used 
# Reminder:
# TEXT_CONTENT[chapter][0] -> chapter title
# TEXT_CONTENT[chapter][1] -> chapter content

# -------------for each chapter of the book --------------
# ------------ each will have unique _id for the chapter consisting of TEXT_NAME + chapterNumber (no spaces)
for i in range(numberOfChapters):
    # split the text into paragraphs        
    paragraphs = blankline_tokenize(TEXT_CONTENT[i][1])
    # initialize return document 
    doc = {
        "_id" : TEXT_NAME + str(i+1),
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

            # tags quotes --> not used since multiple lines are contained within one --
            """
            if(is_quote(sentence)):
                sentence = sentence.replace('—', '')
                #sentence = '"' + sentence + '"'  """

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


    with open(TEXT_NAME+str(i+1)+".json", "w") as file:
        json.dump(doc, file)

docAttributes = {
                    "_id": TEXT_NAME,
                    "chapters": numberOfChapters
                }

collection.insert_one(docAttributes)

print(f"Text collection '{collection_name}' has been rebuilt.")



#######################################################################################
# last step is to create the analysis for each chapter in the file uploaded
# will be contained in one collection called "TEXT_NAME"
# have documents inside of the collection named "TEXT_NAME" + "chapterNum" (no spaces)





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

# textStorage collection
# text = client["textStorage"]
collection = db[TEXT_NAME]

# analysisStorage collection
analysis = client["analysisStorage"]


# will overwrite if the file exists already
# Check if the collection exists before dropping it
if collection_name in analysis.list_collection_names():
    analysis[collection_name].drop()
    print(f"Analysis collection '{collection_name}' has been dropped.")
    print("Rebuilding ...")
else:
    print(f"Creating new analysis for {collection_name}.")


# iterate over content of each chapter
for i in range(numberOfChapters):

    # find document
    document = collection.find_one({"_id": TEXT_NAME + str(i+1)})

    # initialize categorized data to return to database
    categorized = []

    # read the category list from the database analysisStorage -> categoryList
    categories = analysis["categoryList"]

    categoryDB = categories.find_one()
    categoryList = []

    # read from category list and create key value pairs
    for k,v in categoryDB.items():
        if(k == "_id"):
            continue
        else:
            categoryList.append(k)
            categoryList.append(v)


    # stores sentence number
    sentenceCtr = 0

    for paragraph in document["content"]:

        # if a sentence add to text
        if("sentences") in paragraph:
            
            # iterate accross each paragrah sentence
            for sentence in paragraph["sentences"]:

                # sentenceBlocks containing sentence numbers with categories
                sentenceBlock = {
                "num": sentenceCtr,
                "text": None,
                "categories": []
                }

                myDict = {}

                # find language that text is 
                doc = nlp(sentence["text"])
                langTag = doc._.language
                lang = codetoString(langTag["language"])

                # standard text and language categories
                sentenceBlock["text"] = sentence["text"]
                myDict["language"] = lang
                # translate if not english
                if(langTag["language"] != "en"):
                    translation = translator.translate(sentence["text"], dest="en")
                    myDict["translation"] = translation.text


                categoryList[1]["actors"] = []
                categoryList[1]["involves"] = []
                categoryList[1]["action_types"] = []
                categoryList[1]["action_modifier"] = []
                for ent in doc.ents:
                    if(ent.label_ == "PERSON"):
                        categoryList[1]["actors"].append(ent.text)
                        categoryList[1]["involves"].append(ent.text)
                for token in doc:
                    if(token.pos_ == "VERB"):
                        categoryList[1]["action_types"].append(token.text)
                    if(token.pos_ == "NOUN" or token.pos_ == "PRON"):
                        categoryList[1]["involves"].append(token.text)
                    if(token.pos_ == "ADV"):
                        categoryList[1]["action_modifier"].append(token.text)
                myDict.update(categoryList[1])


                sentenceBlock["categories"].append(myDict)

                # Increment senence counter
                sentenceCtr+=1

                categorized.append(sentenceBlock)


    categorizedData = {
                        "_id" : TEXT_NAME + str(i+1),
                        "data": categorized    }

    # use analysis collection
    analysis_collection = analysis[TEXT_NAME]
    analysis_collection.insert_one(categorizedData)


    with open(TEXT_NAME + str(i+1)+".json", "w") as file:
        json.dump(categorized, file)

# initialize the DB with categories
print("Analysis completed.")

# close database
client.close()
