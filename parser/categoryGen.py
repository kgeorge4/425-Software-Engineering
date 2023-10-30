import spacy
from pymongo import MongoClient
import json

# the goal of this file is to create a JSON file that contains a list of default categories
# with the future goal to edit and add categories
# user will be able to specify what type of data the category will store, being singe entity or multiple(list)


#   '@' = one entity
#   '#' = multiple entity list
defaultList = {
    "@text_meaning",
    "@text_type",
    "@narrator",
    "#indications", 
    "#involves",
    "@spoken_by", 
    "@spoken_to", 
    "#spoken_modifiers", 
    "#action_types",
    "@action_initiator", 
    "@action_recipient", 
    "@action_modifier",
    "@text_modifier",
}


client = MongoClient("mongodb://localhost:27017/") 

db = client["textStorage"]

collection = db["analysis"]


jsonContent = {}
toDb = []

# initializes the json data structure with key/value pairs
for text in defaultList:
    type = text[0]

    if(type == '@'):
        jsonContent[text[1:]] = None
    elif(type == '#'):
        jsonContent[text[1:]] = []

json_data = json.dumps(jsonContent)

toDb.append(json_data)

with open("categoryList.json", "w") as file:
    json.dump(json_data, file)

toDb = {"categories: ": jsonContent}


categories = db["categories"]
categories.insert_one(toDb)
