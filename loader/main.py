# Jeff Kretschmer and Burke Landon

import spacy
import pymongo
from nltk.tokenize import TreebankWordTokenizer as twt
from pymongo import MongoClient
from spacy import displacy
from spacy_langdetect import LanguageDetector
from spacy.language import Language

import json
import nltk, re
from nltk.tokenize import word_tokenize, sent_tokenize, blankline_tokenize
import sys, os
import logging
import threading
import multiprocessing

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

# creates collection name with the userID appended to the file name
def createCollectionName(file_name, uid):
    # remove file extension
    fileName = removeFileExtension(file_name)
    # concatenate filename and user id
    fileName = fileName + "_" + uid

    # return final unique file name
    return fileName

# breaks apart the text into chapters
def split_into_chapters_with_content(text):
    # Define regular expression patterns for chapter identifiers
    chapter_patterns = [
        r'\[ [IVXLCDM]+ \]',  # e.g., [ I ], [ II ], [ III ], etc.
        r'\[ [0-9]+ \]',      # e.g., [ 1 ], [ 2 ], [ 3 ], etc. (numbers within square brackets)
        #r'[IVXLCDM]+(?=\s)',  # e.g., I, II, III, etc. (Roman numerals)
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

# list of all possible languages from the text
langList = {
    "en": "English",
    "ro": "Romainian",
    "it": "Italian / latin",
    "lt": "Latin",
     "" : "Uknown"
}

# determines if line is a quote using regular expression search
def is_quote(line):
  quote = re.search('—([^"]*)', line)
  if(quote):
      return True
  else: 
      return False

# spacy language detectors
def get_lang_detector(nlp, name):
    return LanguageDetector()
def codetoString(code):
    return langList.get(code)

######################################################################################
# First step is to load into database under the textStorage database
# the collection name comes from the file
# each document in that collection will be named "COLLECTION_NAME + chapterNum" (no spaces)

def loadText():


    # will drop and rewrite if the file exists already
    # Check if the collection exists before dropping it
    if COLLECTION_NAME in textDB.list_collection_names():
        textDB[COLLECTION_NAME].drop()
        print(f"Text collection '{COLLECTION_NAME}' has been dropped.")
    else:
        print(f"Creating new collection for {COLLECTION_NAME}.")



    # file opened above and use the tuple called textContent
    # requires the text to be split into chapters
    # TEXT_CONTENT variable holds the tuple of text that will be used 
    # Reminder:
    # TEXT_CONTENT[chapter][0] -> chapter title
    # TEXT_CONTENT[chapter][1] -> chapter content

    # -------------for each chapter of the book --------------
    # ------------ each will have unique _id for the chapter consisting of COLLECTION_NAME + chapterNumber (no spaces)

    for i in range(numberOfChapters):

        # split the text into paragraphs        
        paragraphs = blankline_tokenize(TEXT_CONTENT[i][1])
        # initialize return document 

        doc = {
            "_id" : COLLECTION_NAME + str(i+1),
            "content": []
        }


        sentenceCtr = 1
        paragraphCtr = 1


        # iterate over paragraphs
        for paragraph in paragraphs:

            paragraphList = []

            # break each paragraph into sentences
            sentences = sent_tokenize(paragraph)

            sentenceIndex = 0
            # pass over each sentence in paragraph
            for sentence in sentences:

                # tags quotes --> not used since multiple lines are contained within one --
                """
                if(is_quote(sentence)):
                    sentence = sentence.replace('—', '')
                    #sentence = '"' + sentence + '"'  """
                
                words = sentence.split(" ")
                wordList = []
                for word in words:
                    wordList.append((word, "#000000", "#FBFBFB"))
                
                paragraphList.append({        
                                        "sentenceIndex" : sentenceIndex,
                                        "sentenceNum": sentenceCtr,
                                        "text": sentence,
                                        "wordList": wordList
                                    })
                #print(numberedSentence)
                sentenceCtr+=1
                sentenceIndex+=1

            # add to current nested block
            documentData = {
                "paragraphNum" : paragraphCtr,
                "sentences" : paragraphList
            }

            # increment paragraph counter
            paragraphCtr += 1

            # add to current content
            doc["content"].append(documentData)

            # end of sentences for loop

        # end of paragraphs for loop
            
        # inserts into mongoDB
        text_collection.insert_one(doc)

        """
        with open(COLLECTION_NAME+str(i+1)+".json", "w") as file:
            json.dump(doc, file)
        """

    # end of main for loop

    docAttributes = {
                        "_id": COLLECTION_NAME ,
                        "chapters": numberOfChapters,
                        "current_chapter": 1,
                        "current_color": '',
                        "current_index": [-1.0] * numberOfChapters,
                        "key_list": [('#000000', '+'), ('#000000', '+'), ('#000000', '+'),('#000000', '+'), ('#000000', '+'), ('#000000', '+')],
                        "scroll_progress": [0.0] * numberOfChapters
                    }

    text_collection.insert_one(docAttributes)

    print(f"Text collection '{COLLECTION_NAME}' has been rebuilt.")

###########################################################################################
# last step is to create the analysis for each chapter in the file uploaded
# will be contained in one collection called "COLLECTION_NAME"
# have documents inside of the collection named "COLLECTION_NAME" + "chapterNum" (no spaces)

def analyzeTextChaper(chapter_num, event):

    # wait until triggered
    event.wait()    


    # init the dataset for text type classification
    data = {
    "dialogue": ["—Come up, Kinch! Come up, you fearful jesuit! ",
               "—Back to barracks! he said sternly",
               "—Thanks, old chap, he cried briskly.",
               "—I’ll take a mélange, Haines said to the waitress.",
               "—No, said miss Kennedy. It gets brown after. Did you try the borax with the cherry laurel water?",
                "—Gorgeous, she said. Look at the holy show I am. Lying out on the strand all day."  ],
    "exposition": ["Stately, plump Buck Mulligan came from the stairhead, bearing a bowl of lather on which a mirror and a razor lay crossed. A yellow dressinggown, ungirdled, was sustained gently behind him on the mild morning air.",
                " Solemnly he came forward and mounted the round gunrest. He faced about and blessed gravely thrice the tower, the surrounding land and the awaking mountains. Then, catching sight of Stephen Dedalus, he bent towards him and made rapid crosses in the air, gurgling in his throat and shaking his head. Stephen Dedalus, displeased and sleepy, leaned his arms on the top of the staircase and looked coldly at the shaking gurgling face that blessed him, equine in its length, and at the light untonsured hair, grained and hued like pale oak.",
                "Mr Bloom walked unheeded along his grove by saddened angels, crosses, broken pillars, family vaults, stone hopes praying with upcast eyes, old Ireland’s hearts and hands. More sensible to spend the money on some charity for the living. Pray for the repose of the soul of. Does anybody really? Plant him and have done with him.",
                "Bloowho went by by Moulang’s pipes bearing in his breast the sweets of sin, by Wine’s antiques, in memory bearing sweet sinful words, by Carroll’s dusky battered plate, for Raoul.",
                "How moving the scene there in the gathering twilight, the last glimpse of Erin, the touching chime of those evening bells and at the same time a bat flew forth from the ivied belfry through the dusk, hither, thither, with a tiny lost cry." 
                ]
    }


    # setup for spacy
    spacy.prefer_gpu()
    nlp = spacy.load("en_core_web_sm")
    Language.factory("language_detector", func=get_lang_detector)
    nlp.add_pipe('language_detector', last=True)
    # setup for classification
    #classyNLP = spacy.load('en_core_web_md')
    #classyNLP.add_pipe("classy_classification", config={"data": data,"model": "spacy"})
    # init the Google API translator
    #translator = Translator()

    

    # find document
    document = text_collection.find_one({"_id": COLLECTION_NAME + str(chapter_num+1)})

    # initialize categorized data to return to database
    categorized = []

    # read the category list from the database analysisStorage -> categoryList
    categories = analysis["categoryList"]
    categoryDB = categories.find_one()

    # Category list to be added to database
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
                "text": [],
                "notes": "",
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
                #if(langTag["language"] != "en"):
                #    translation = translator.translate(sentence["text"], dest="en")
                #    myDict["translation"] = translation.text


                categoryList[1]["actors"] = []
                categoryList[1]["involves"] = []
                categoryList[1]["action_types"] = []
                categoryList[1]["action_modifier"] = []
                categoryList[1]["text_type"] = []
                categoryList[1]["spoken_by"] = []
                categoryList[1]["spoken_to"] = []
                categoryList[1]["narrator"] = []
                categoryList[1]["text_meaning"] = []
                categoryList[1]["action_initiator"] = []
                categoryList[1]["action_recipient"] = []
                categoryList[1]["text_modifier"] = []
                #jsonLoader = json.dumps(classyNLP(sentence["text"])._.cats)
                #jsonLoader = json.loads(jsonLoader)

                #if float(jsonLoader["dialogue"]) > .7:
                #    categoryList[1]["text_type"].append("dialogue")
                #elif float(jsonLoader["exposition"]) > .7:
                #    categoryList[1]["text_type"].append("expositon")
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
                            "_id" : COLLECTION_NAME + str(chapter_num+1),
                            "data": categorized    }

    # use analysis collection
    analysis_collection = analysis[COLLECTION_NAME]
    analysis_collection.insert_one(categorizedData)
    
    """
    with open(COLLECTION_NAME + str(chapter_num+1)+".json", "w") as file:
        json.dump(categorized, file)

    """     
    # initialize the DB with categories
    print(f"Analysis chapter {chapter_num+1} completed.")



# starts the multiprocess analyzer for each chapter
def analyzeTextMultiprocess():
    # list of current processes running
    processes = []

    # event trigger to start processes
    event = multiprocessing.Event()

    # will overwrite if the file exists already
    # Check if the collection exists before dropping it
    if COLLECTION_NAME in analysis.list_collection_names():
        analysis[COLLECTION_NAME].drop()
        print(f"Analysis collection '{COLLECTION_NAME}' has been dropped.")
    else:
        print(f"Creating new analysis for {COLLECTION_NAME}.")

    for i in range(0, numberOfChapters):
        process = multiprocessing.Process(target=analyzeTextChaper, args=(i, event))
        processes.append(process)
        process.start()

    # start all analysis processes
    event.set()
    print("Processes starting ")

    # wait for all processes to finish
    for process in processes:
        process.join()

    print("All chapters analyzed.")


if __name__ == "__main__":

    ######## Global file attributes #########
    TEXT_PATH = sys.argv[2]         # will be modified based on file upload
    UID = sys.argv[3]               # unqiue user id from user class
    COLLECTION_NAME = createCollectionName(TEXT_PATH.split("/")[-1], UID) # creates final collecion name using the name of the file upload

    # first index is the chapter name
    # second index is the chapter content
    # len(TEXT_CONTENT) gives number of chapters
    TEXT_CONTENT = getChapters(TEXT_PATH)
    numberOfChapters = (len(TEXT_CONTENT))

    # connecting to MongoDB server
    # all files are stored in the textStorage db then analyzed and stored into analyzeStorage
    client = pymongo.MongoClient('mongodb://jkretschmer1:aiN4mooheitaez@localhost:27017/?authSource=admin')
    textDB = client["textStorage"]
    analysis = client['analysisStorage']

    # save the collection of the text in textStorage
    text_collection = textDB[COLLECTION_NAME]

    loadText()
    analyzeTextMultiprocess()

    # close database
    client.close()