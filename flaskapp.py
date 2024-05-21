from flask import Flask, render_template, session, redirect, jsonify, request, redirect, url_for
from user.models import User # Imports user class created in models.py
from functools import wraps
import pymongo, os, subprocess, sys, string
from pathlib import Path


app = Flask(__name__)
app.secret_key = 'Dreamteam'

# Database connections
client = pymongo.MongoClient('mongodb://jkretschmer1:aiN4mooheitaez@localhost:27017/?authSource=admin')
loginDB = client['loginInfo']
textDB = client['textStorage']
# connect to the analysis      analysis -> FILENAME_UID + chapnum -> { categories } ... {actors}
analysisDb = client['analysisStorage']


# File for storing uploaded text documents
cwd = '/var/www/html/joyce/'

verbose=False

# example of sending mail
# Working of flask mail and setting it parameters

#app.config['MAIL_SERVER'] = 'smtp.protonmail.ch'
#app.config['MAIL_PORT'] = 587
#app.config['MAIL_USERNAME'] = 'salisburyjoyceproject@proton.me'
#app.config['MAIL_PASSWORD'] = 'Dreamteam'
#app.config['MAIL_USE_TLS'] = True
#app.config['MAIL_USE_SSL'] = False
#mail = Mail(app)

#
##################################################################################################
# Functions and Decorators 

# Login required decorator
def login_required(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs)
    else:
      return redirect('/')
  
  return wrap

# Find sentence function, returns single sentence
def find_sentence(name, chapter, sent_num, verbose=True):

  if verbose:
    print(f'find_sentence called with: \nname: {name}\nchapter: {chapter}\nsent_num: {sent_num}')
    
  # Fixes indexing in dashboard where when clicking the first
  # sentence it was not returning 0, giving referenced before
  # assignment error
  sent_num += 1

  collection = textDB[name]
  #collection = textDB[tableName]
  document = collection.find_one({"_id": name + chapter})

  for paragraph in document["content"]:
    # if a sentence add to text
    if("sentences") in paragraph:
        # iterate accross each paragrah sentence
        for sentenceBlock in paragraph["sentences"]:
            sentenceNum = sentenceBlock["sentenceNum"]

            if(sentenceNum == sent_num):
                sentNum = str(sent_num)
                sentence = sentNum, sentenceBlock["text"]
            # build text list
  return sentence

##################################################################################################

# Find categories function
def find_categories(name, chapter, num, cat):
    collection = analysisDb[name]
    # Find the chapter that is being used
    document = collection.find_one({"_id": name + chapter})

    # Ensure document and its data exist
    if document and 'data' in document:
        categoricalD = document['data']

        # Ensure categoricalD[num] and its categories exist
        if num < len(categoricalD) and 'categories' in categoricalD[num]:
            categories = categoricalD[num]["categories"]

            # Ensure categories is not empty and actors exist
            if categories and categories[0].get(cat):
                catList = categories[0][cat]
                if catList is not None:
                    # Filter out None items and ensure all items are strings
                    catList = [str(item) for item in catList if item is not None]
                    User().log_message(f'find_categories() returning with {len(catList)} elements')

                    return ", ".join(catList)

    # Return a default message if any level of the data structure is missing
    return 'No contents found in database.'



# returns the number of chapters in the given text
def getNumChapters(name):
   
   collection = textDB[name]
   result = collection.find_one({"_id": name })
   retVal = result['chapters']
   return retVal
   

##################################################################################################

# Print chapter, returns sentence and sentence num
def print_chapter(name, chapter):

  collection = textDB[name]
  document = collection.find_one({"_id": name + chapter})
  text = []

  for paragraph in document["content"]:
    # if a sentence add to text
    if("sentences") in paragraph:
        # iterate accross each paragrah sentence
        for sentenceBlock in paragraph["sentences"]:
            sentenceNum = sentenceBlock["sentenceNum"]
            sentence = sentenceBlock["text"]
            wordDict = sentenceBlock["wordList"]
            text.append(wordDict)

  return text

# prints plain text line by line depending on what chapter was input
def output_text(name, chapter):

    collection = textDB[name]
    #collection = textDB[tableName]
    document = collection.find_one({"_id": name + chapter})

    textRet=[]

    for paragraph in document["content"]:
        # if a sentence add to text
        if("sentences") in paragraph:
           textRet.append(paragraph['sentences'])
    
    return textRet
   
# returns the number of sentences that are in the given paragraph
def findParagraphLen(paragraph):
   return len(paragraph)

# denotes paragraphs by the ¶ sign to print them correctly on the website
def returnText_originalParagraphs(name, chapter, verbose=False):

  retVal = []
  ret = output_text(name, chapter)
  size = findParagraphLen(ret)


  if verbose:
    print("returnText_originalParagraphs() called in app.py\n")
    #print("Ret: ", ret)
    #print(ret[0][0]['text'])
    print('retsize: ', size)

  for i in range(findParagraphLen(ret)):
    for j in range(findParagraphLen(ret[i])):
      retVal.append(ret[i][j]['text'])
    if(i < size-1):
      retVal.append("¶")

  return retVal

def removeUID(fileName):
    return fileName.split("_")[0]

def convert_to_rgb(hex):
  hex = hex.strip('#')
  rgb = []
  opacity = 0.3

  for i in (0, 2, 4):
    decimal = int(hex[i:i+2], 16)
    rgb.append(decimal)
  
  rgb.append(opacity)
  return 'rgba' + str(tuple(rgb))

#
##################################################################################################
# App routes for HTML Webpages

# Default page
@app.route('/')
def home():
  return render_template('index.html')

# Loading page for uploading or selecting text files
@app.route('/loader/')
@login_required
def loader():
    
    uid = User().get_Uid()
    fileName, chapter = User().get_file_chapter()
    globalTables = textDB.list_collection_names()
    tables = []

    

    for name in globalTables:
        if uid in name:
            tables.append(name)

    if(len(tables) == 0 and fileName == None):

      # initialize the demo text on user access page for first time
      uid = User().get_Uid()

      filepath = cwd + 'loader/demo.txt'
      loaderPath = cwd + 'loader/main.py'

      script_cmd = ['python3', loaderPath, '--fileName', filepath, uid]
      subprocess.run(script_cmd, check=True)

      return redirect(url_for('loader'))
  
  
    return render_template('loader.html', tables=tables)

@app.route('/upload/', methods=['POST'])
@login_required
def upload_file():
    
    uid = User().get_Uid()
    
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    # Run the loader on given file to initialize text
    if file:
        
        filename = cwd + 'files/' + file.filename
        file.save(filename)

        loaderPath = cwd + 'loader/main.py'


        try:
          script_cmd = ['python3', loaderPath, '--fileName', filename, uid]
          subprocess.run(script_cmd, check=True)

        except Exception as e:
          User().log_message('ERROR: upload_file() failed to upload.')
          return f"Error: {str(e)}"
        
        print("Upload successful\n")
        User().log_message(f'upload_file() called successfully with {file}')

        filePath = Path(filename)
        filePath.unlink()
        return redirect(url_for('loader'))
    

# This redirects user to dashboard with file name and the last chapter accessed
# Also sets current_file to collection
@app.route('/collectionInfo/<collection>', methods=['GET'])
@login_required
def collectionInfo(collection):

  # User().log_message('collectionInfo called in app.py')

  # Set current_file to collection name
  User().text_index_info(collection)

  attributes = textDB[collection].find_one({"_id": collection})

  if attributes:
    chapNum = attributes.get("current_chapter")

  if verbose:
    print("Collection: ", collection)
    
  User().log_message(f'collectionInfo() called with {collection}')
  return jsonify({'chapter': chapNum})


# Dashboard page
@app.route('/dashboard/<fileName>/<chapterNum>/')
@login_required
def dashboard(fileName, chapterNum):

  if verbose:
    print('dashboard called with: \nfileName: {fileName}\nchapterNum: {chapterNum}')
    

  numberOfChapters = getNumChapters(fileName)
  paragraphs = returnText_originalParagraphs(fileName, chapterNum)
  chapter = print_chapter(fileName, chapterNum)
  fileNameDisplayed = removeUID(fileName)


  # Modify user class data
  User().modifyLastChapter(fileName, chapterNum)

  attributes = textDB[fileName].find_one({"_id": fileName})

  if(attributes):
    textDB[fileName].update_one(
      {"_id": fileName},
      {
        "$set": {
            "current_chapter": chapterNum
        }
      }
    )


  key_list = attributes.get("key_list")
  user_color = attributes.get("current_color")

  return render_template('dashboard.html', numberOfChapters = numberOfChapters, fileNameDisplayed = fileNameDisplayed, 
    fileName = fileName, chapterNum = chapterNum, paragraphs = paragraphs, chapter = chapter, user_color = user_color, key_list = key_list)


# On page load the last index of current chapter needs to be retreived
@app.route('/getIndex/', methods=['GET'])
@login_required
def getIndex():

  fileName, chapter = User().get_file_chapter()

  chapterNum = int(chapter) - 1  # fix the indexing and chapter number error

  attributes = textDB[fileName].find_one({"_id": fileName})

  if attributes:
    lastIndex = attributes.get("current_index")[chapterNum]

  return jsonify({'lastIndex': lastIndex})


# Dashboard index route, calls find_sentence with passed index
@app.route('/dashboard/<fileName>/<chapterNum>/<int:index>')
@login_required
def selected_sentence(fileName, chapterNum, index):

  # User().log_message('selected_sentence() called in app.py')

  sentenceIndex, sentence = find_sentence(fileName, chapterNum, index)

  if verbose:
    print("sentenceIndex: ", sentenceIndex, "\n")
    print("sentence: ", sentence)

  # modify user class data
  User().modifyLastChapterIndex(fileName, chapterNum, index, sentence)

  chapterNum = int(chapterNum) - 1 

  attributes = textDB[fileName].find_one({"_id": fileName})

  if(attributes):
    textDB[fileName].update_one(
      {"_id": fileName},
      {
        "$set": {
            f"current_index.{chapterNum}": index
        }
      }
    )


  User().log_message(f'selected_sentence returning sentenceIndex, sentence, and fileName')
  return jsonify({'index':sentenceIndex, 'sentence':sentence, 'fileName':fileName})

# Sign up route
@app.route('/user/signup/', methods=['POST'])
def signup():
  return User().signup()

# Sign out route
@app.route('/user/signout')
def signout():
  return User().signout()

# Login route
@app.route('/user/login', methods=['POST'])
def login():
  return User().login()


@app.route("/addCategory/", methods = ['POST'])
@login_required
def addCategory():
   name, chapter, index = User().find_argument_info()
   text_value = request.form.get('text')
   print("Received text:", text_value)
   collection = analysisDb[name]
   document = collection.find_one({"_id": name + chapter})

   update_query = {
    "$push": {
        f"data.$[].categories.0.{text_value}": None
    }
    } 

   result = collection.update_many(
    {}, 
    update_query
    )


   if result.modified_count > 0:
        # Successfully added the phrase to the database
        return jsonify({"message": "Phrase added successfully"}), 200
   else:
        # Failed to add the phrase
        return jsonify({"error": "Failed to add phrase to database"}), 500
   
@app.route("/removeCategory/", methods = ['POST'])
@login_required
def removeCategory():
   name, chapter, index = User().find_argument_info()
   text_value = request.form.get('text')
   print("Received text:", text_value)
   collection = analysisDb[name]
   document = collection.find_one({"_id": name + chapter})

   update_query = {
        "$unset": {f"data.$[].categories.0.{text_value}": ""}
    }

   result = collection.update_many(
    {}, 
    update_query
    )


   if result.modified_count > 0:
        # Successfully added the phrase to the database
        return jsonify({"message": "Phrase added successfully"}), 200
   else:
        # Failed to add the phrase
        return jsonify({"error": "Failed to add phrase to database"}), 500


@app.route('/updateCategories/<int:index>/<string:currCat>/', methods=['GET'])
@login_required
def update_categories(index, currCat):


  file_name, chapter = User().get_file_chapter()
  category_list = find_categories(file_name, chapter, index, currCat)

  if verbose:
    print("file: ", file_name)
    print("chapter: ", chapter)
    print("index: ", index)
    print("category list: ", category_list)

  User().log_message(f'update_categories called successfully with {len(category_list.split())} elements in character_list.')
  return jsonify({'categories': category_list})



@app.route('/updateCharacters/<int:index>/', methods=['GET'])
@login_required
def update_characters(index):

  # User().log_message('update_characters() called in app.py')

  file_name, chapter = User().get_file_chapter()

  character_list = find_characters(file_name, chapter, index)

  if verbose:
    print("file: ", file_name)
    print("chapter: ", chapter)
    print("index: ", index)
    print("character list: ", character_list)

  User().log_message(f'update_characters called successfully with {len(character_list.split())} elements in character_list.')
  return jsonify({'characters': character_list})

@app.route('/updateInvolves/<int:index>/', methods=['GET'])
@login_required
def update_involves(index):

  # User().log_message('update_involes called in app.py')

  file_name, chapter = User().get_file_chapter()

  involves_list = findInvolves(file_name, chapter, index)

  if verbose:
    print("file: ", file_name)
    print("chapter: ", chapter)
    print("index: ", index)
    print("involves list: ", involves_list)

  User().log_message(f'update_involves called successfully with {len(involves_list.split())} elements in involves_list.')
  return jsonify({'involves': involves_list})


@app.route('/highlight/', methods=['POST'])
@login_required
def highlight_text():

  # User().log_message('highlight_text() called in app.py')

  highlighted_text = request.json.get('highlightedText', '')
  phrase_length = len(highlighted_text)
  sentence_length = User().find_sentence_length()
  
  if verbose:
    print("Phrase: ", phrase_length)
    print("Sentence: ", sentence_length)
    print("Phrase: ", highlighted_text)

  if (phrase_length <= sentence_length): 

    # Sends phrase to database
    User().send_highlighted_sentence(highlighted_text)
  
    User().log_message(f'highlight_text() called successfully with {highlighted_text}')
    return jsonify({'displayedText': highlighted_text})
  
  User().log_message('ERROR: highlight_text() failed to send to database, phrase longer than sentence.')
  return jsonify({'displayedText': 'Please highlight text only within the sentence, not including the index.'})

@app.route("/sendColor/", methods=['POST'])
def send_color_to_server(verbose=True):
  
  color = request.json.get('color', '')
  fileName, chapter = User().get_file_chapter()

  attributes = textDB[fileName].find_one({"_id": fileName})

  if(attributes):
    textDB[fileName].update_one(
      {"_id": fileName},
      {
        "$set": {
            "current_color": color
        }
      }
    )

  if verbose:
    print("send_color_to_server() called with ", color)

  return User().modify_user_color(color)

@app.route("/updateKeyText/", methods=['POST'])
def update_key_text(verbose=True):

  text = request.json.get('text', '')
  current_id = request.json.get('current_id')
  current_file = User().get_file_chapter()
  
  # Takes in HTML id such as key_name_1 and strips everything but
  # integer and converts string to int, then subtracts one for
  # correct indexing 
  position = int(current_id.strip('key_name_')) - 1

  if verbose:
    print("Position: ", position)

  if verbose:
    print("update_key_text called with ", text, current_id, current_file[0])

  if 'user' in session:
    user = loginDB.users.find_one({"_id": session['user']['_id']})

    if user:
      result = loginDB.users.update_one(
        {
          "_id": user['_id'],
          f"key_list.{position}.1": {"$exists": True},
        },
        {
          "$set": {f"key_list.{position}.1": text }
        },
      )
    
      if result.modified_count > 0 and verbose: 
        print(f'Updated: key_list.{position}.1": {text}')
                
      elif result.modified_count < 1 and verbose:
        print("Update failed.", result.raw_result)

  # find the text attributes at the bottom of the file
  fileName, chapter = User().get_file_chapter()
  attributes = textDB[fileName].find_one({"_id": fileName})

  if(attributes):
    textDB[fileName].update_one(
      {
        "_id": fileName,
        f"key_list.{position}.1": {"$exists": True},
      },
      {
        "$set": {f"key_list.{position}.1": text }
      },
    )

  return jsonify('update_key_text called')

@app.route("/updateKeyColor/", methods=['POST'])
def update_key_color(verbose=True):

  color = request.json.get('color', '')
  current_id = request.json.get('current_id', '')
  current_file = User().get_file_chapter()
  
  # Takes in HTML id such as key_name_1 and strips everything but
  # integer and converts string to int, then subtracts one for
  # correct indexing 
  position = int(current_id.strip('key_color_')) - 1

  if verbose:
    print("Color:    ", color)
    print("Position: ", position)

  if verbose:
    print("update_key_color called with ", color, current_id, current_file[0])

  if 'user' in session:
    user = loginDB.users.find_one({"_id": session['user']['_id']})

    if user:
      result = loginDB.users.update_one(
        {
          "_id": user['_id'],
          f"key_list.{position}.0": {"$exists": True},
        },
        {
          "$set": {f"key_list.{position}.0": color }
        },
      )
    
      if result.modified_count > 0 and verbose: 
        print(f'Updated: key_list.{position}.0": {color}')
                
      elif result.modified_count < 1 and verbose:
        print("Update failed.", result.raw_result)


  # find the text attributes at the bottom of the file
  fileName, chapter = User().get_file_chapter()
  attributes = textDB[fileName].find_one({"_id": fileName})

  if(attributes):
    textDB[fileName].update_one(
      {
        "_id": fileName,
        f"key_list.{position}.0": {"$exists": True},
      },
      {
        "$set": {f"key_list.{position}.0": color }
      },
    )

  return jsonify('update_key_text called')

@app.route("/submitHighlight/", methods=['POST'])
def compare_phrase_to_dict():
  
  # User().log_message('compare_phrase_to_dict() called in app.py')

  name, chapter, index = User().find_argument_info()
  color = User().get_user_color()

  phrase = User().get_phrase()

  if verbose:
    print("phrase: ", phrase)
    print("color: ", color)

  collection = textDB[name]
  document = collection.find_one({"_id": name + chapter})


  word_list = phrase.split()
  first_word = word_list[0]
  last_word = word_list[-1]

  start_position = None
  end_position = None

  # paragraph_num = None
  sentence_index = None

  for paragraph in document["content"]:
    
    if("sentences") in paragraph:
      for sentenceBlock in paragraph["sentences"]:
      
        sentenceNum = sentenceBlock["sentenceNum"]
        sentence_index = sentenceBlock["sentenceIndex"]

        if(sentenceNum == index+1):
          for i, word in enumerate(sentenceBlock["wordList"]):

            if word[0] == first_word:
              if start_position == None:
                start_position = i

              paragraph_num = (paragraph["paragraphNum"])

              if verbose:
                print("first_word: ", first_word)
                print("word[0]   : ", word[0])
                print("Paragraph num: ", paragraph_num)
                print("index: ", index)

            if word[0] == last_word:
              if end_position == None:
                end_position = i

          if verbose:
            print("Range: ", start_position, end_position)
          
          if start_position is not None and end_position is not None and sentence_index is not None:
            for i in range(start_position, end_position+1):
              
              if verbose:
                 print("Iteration in for loop: ", i)

              result = collection.update_one(
                {
                  "_id": name + chapter,
                  f"content.{paragraph['paragraphNum'] - 1}.sentences.{sentence_index}.wordList.{i}.1": {
                  "$exists": True
                  },
                },
                {           
                  "$set": {
                  f"content.{paragraph['paragraphNum'] - 1}.sentences.{sentence_index}.wordList.{i}.1": color
                  
                  }
                }
              )

              if result.modified_count > 0: 
                #print(f'Updated: content.{paragraph["paragraphNum"]-1}.sentences.{sentence_index}.wordList.{i}.1: {color}')
                User().log_message(f'compare_phrase_to_dict(), Updated: content.{paragraph["paragraphNum"]-1}.sentences.{sentence_index}.wordList.{i}.1: {color}')
               
              elif result.modified_count < 1:
                #print("Update failed.", result.raw_result)
                #print(f'content.{paragraph["paragraphNum"]-1}.sentences.{sentence_index}.wordList.{i}.1: {color}')
                User().log_message(f'compare_phrase_to_dict(), Update failed: {result.raw_result}. content.{paragraph["paragraphNum"]-1}.sentences.{sentence_index}.wordList.{i}.1: {color}')
                User().log_message(f'compare_phrase_to_dict(), Highlight failed to update.')
                return jsonify({"error": "Text not highlighted"}), 405

          else:
            # print("error: None type variable in if statement for collection.update.\n")
            User().log_message(f'ERROR: compare_phrase_to_dict(), None type variable in if statement for collection.update.')
            return jsonify({"error": "Text not highlighted"}), 405
  
  User().log_message(f'compare_phrase_to_dict(), Highlight submitted successfully')
  return jsonify({"message": "Highlight submitted successfully"}), 200

@app.route("/addTextCat/", methods =['POST'])
def addTextCategory():
    name, chapter, index = User().find_argument_info()
    phrase = User().get_phrase()
    cat_value = request.form.get('cat')
    
    # Remove punctuation from the phrase
    translator = str.maketrans('', '', string.punctuation) 
    phrase = phrase.translate(translator) 
    
    print("phrase: ", phrase)
    print("index: ", index)

    # Access the collection in the database
    collection = analysisDb[name]
    document = collection.find_one({"_id": name + chapter})

    update_query = {
        "$push": {
            f"data.{index}.categories.0.{cat_value}": phrase
        }
    }

    # Update the document with the phrase at the specified index
    result = collection.update_one(
        {"_id": name + chapter},
        update_query
    )

    if result.modified_count > 0:
        # Successfully added the phrase to the database
        return jsonify({"message": "Phrase added successfully"}), 200
    else:
        # Failed to add the phrase
        return jsonify({"error": "Failed to add phrase to database"}), 500
    

@app.route("/addSubmitText/", methods =['POST'])
def addSubmitText() :
   name, chapter, index = User().find_argument_info()
   text_value = request.form.get('text')
   cat_value = request.form.get('cat')
   print("Received text:", text_value)

   collection = analysisDb[name]
   document = collection.find_one({"_id": name + chapter})

   update_query = {
        "$push": {
            f"data.{index}.categories.0.{cat_value}": text_value
        }
    }

    # Update the document with the phrase at the specified index
   result = collection.update_one(
        {"_id": name + chapter},
        update_query
    )

   if result.modified_count > 0:
        # Successfully added the phrase to the database
        return jsonify({"message": "Phrase added successfully"}), 200
   else:
        # Failed to add the phrase
        return jsonify({"error": "Failed to add phrase to database"}), 500
   
@app.route("/removeSubmitText/", methods =['POST'])
def removeSubmitText() :
   name, chapter, index = User().find_argument_info()
   text_value = request.form.get('text')
   cat_value = request.form.get('cat')
   print("Received text:", text_value)

   collection = analysisDb[name]
   document = collection.find_one({"_id": name + chapter})

   update_query = {
        "$pull": {
            f"data.{index}.categories.0.{cat_value}": text_value
        }
    }

    # Update the document with the phrase at the specified index
   result = collection.update_one(
        {"_id": name + chapter},
        update_query
    )

   if result.modified_count > 0:
        # Successfully deleted the phrase to the database
        return jsonify({"message": "Phrase deleted successfully"}), 200
   else:
        # Failed to deleted the phrase
        return jsonify({"error": "Failed to delete phrase to database"}), 500

@app.route("/getMongoData", methods=['GET'])
def get_mongo_data():
    name, c = User().get_file_chapter()
    print(type(name))
    collection = analysisDb[name]
    category_names = set()  # Using a set to ensure unique category names
    for doc in collection.find():
        for category in doc['data'][0]['categories']:  # Assuming there's only one item in the 'data' array
            category_names.update(category.keys())  # Add all keys of the category to the set
    
    # Convert set to list and return as JSON
    return jsonify(list(category_names))


@app.route("/removeTextCat/", methods =['POST'])
def removeTextCat():
    name, chapter, index = User().find_argument_info()
    phrase = User().get_phrase()
    
    # Remove punctuation from the phrase
    translator = str.maketrans('', '', string.punctuation) 
    phrase = phrase.translate(translator) 
    
    print("phrase: ", phrase)
    print("index: ", index)

    # Access the collection in the database
    collection = analysisDb[name]
    document = collection.find_one({"_id": name + chapter})

    update_query = {
        "$pull": {
            f"data.{index}.categories.0.actors": phrase
        }
    }

    # Update the document with the phrase at the specified index
    result = collection.update_one(
        {"_id": name + chapter},
        update_query
    )

    if result.modified_count > 0:
        # Successfully deleted the phrase to the database
        return jsonify({"message": "Phrase deleted successfully"}), 200
    else:
        # Failed to deleted the phrase
        return jsonify({"error": "Failed to delete phrase to database"}), 500



@app.route("/highlightBackground/", methods=['POST'])
def highlight_background():
  
  # User().log_message('compare_phrase_to_dict() called in app.py')

  name, chapter, index = User().find_argument_info()
  color = User().get_user_color()

  phrase = User().get_phrase()

  if verbose:
    print("phrase: ", phrase)
    print("color: ", color)

  collection = textDB[name]
  document = collection.find_one({"_id": name + chapter})


  word_list = phrase.split()
  first_word = word_list[0]
  last_word = word_list[-1]

  start_position = None
  end_position = None

  # paragraph_num = None
  sentence_index = None

  for paragraph in document["content"]:
    
    if("sentences") in paragraph:
      for sentenceBlock in paragraph["sentences"]:
      
        sentenceNum = sentenceBlock["sentenceNum"]
        sentence_index = sentenceBlock["sentenceIndex"]

        if(sentenceNum == index+1):
          for i, word in enumerate(sentenceBlock["wordList"]):

            if word[0] == first_word:
              if start_position == None:
                start_position = i

              paragraph_num = (paragraph["paragraphNum"])

              if verbose:
                print("first_word: ", first_word)
                print("word[0]   : ", word[0])
                print("Paragraph num: ", paragraph_num)
                print("index: ", index)

            if word[0] == last_word:
              if end_position == None:
                end_position = i

          if verbose:
            print("Range: ", start_position, end_position)
          
          if start_position is not None and end_position is not None and sentence_index is not None:
            for i in range(start_position, end_position+1):
              
              if verbose:
                 print("Iteration in for loop: ", i)

              result = collection.update_one(
                {
                  "_id": name + chapter,
                  f"content.{paragraph['paragraphNum'] - 1}.sentences.{sentence_index}.wordList.{i}.2": {
                  "$exists": True
                  },
                },
                {           
                  "$set": {
                  f"content.{paragraph['paragraphNum'] - 1}.sentences.{sentence_index}.wordList.{i}.2": color
                  
                  }
                }
              )

              if result.modified_count > 0: 
                #print(f'Updated: content.{paragraph["paragraphNum"]-1}.sentences.{sentence_index}.wordList.{i}.1: {color}')
                User().log_message(f'highlight_backround(), Updated: content.{paragraph["paragraphNum"]-1}.sentences.{sentence_index}.wordList.{i}.2: {color}')
               
              elif result.modified_count < 1:
                #print("Update failed.", result.raw_result)
                #print(f'content.{paragraph["paragraphNum"]-1}.sentences.{sentence_index}.wordList.{i}.1: {color}')
                User().log_message(f'highlight_backround(), Update failed: {result.raw_result}. content.{paragraph["paragraphNum"]-1}.sentences.{sentence_index}.wordList.{i}.2: {color}')
                User().log_message(f'highlight_backround(), Highlight failed to update.')
                return jsonify({"error": "Text not highlighted"}), 405

          else:
            # print("error: None type variable in if statement for collection.update.\n")
            User().log_message(f'ERROR: highlight_backround(), None type variable in if statement for collection.update.')
            return jsonify({"error": "Text not highlighted"}), 405
  
  User().log_message(f'highlight_backround(), Highlight submitted successfully')
  return jsonify({"message": "Background highlight submitted successfully"}), 200

def strip_lower_word(value):
  altered_str = value.translate(str.maketrans('','', string.punctuation + '—')).lower()
  word_array = altered_str.split()
  return word_array

# Search the text for selected word or phrase
@app.route('/searchText/<target>', methods=['POST'])
@login_required
def search_text(target):

  name = request.json.get('fileName', '')
  chapter = request.json.get('chapter', '')
  search_results = []
  sentences = []
  collection = textDB[name]

  stripped_word = strip_lower_word(target)
  print('stripped: ', stripped_word, 'len:', len(stripped_word))
  # start = 1
  # stop = 1

  start=int(chapter)
  stop=int(chapter)

  for chapter_num in range(start, stop+1):
    for chapter in collection.find_one():
      if('content') in chapter:
        chapter_block = collection.find_one({"_id": name + str(chapter_num)})
        for paragraph in chapter_block['content']:
          if('sentences') in paragraph:
            for sentence_block in paragraph['sentences']:
              paragraph_num = (paragraph["paragraphNum"])
              sentence_num = sentence_block["sentenceNum"]
              sentence = f'P{paragraph_num}, S{sentence_num}.) '+ sentence_block['text']

              sentence_text = ' '.join([word[0] for word in sentence_block['wordList']]).lower()

              if all(word in sentence_text for word in stripped_word):
                  result = f'Found \'{target}\' in chapter {chapter_num}, paragraph {paragraph_num}, sentence {sentence_num}.\n'
                  search_results.append(result)
                  sentences.append(sentence)

  amount = len(search_results)

  if search_results:
    return jsonify({"results": f'Found, \'{target}\' {amount} times.', "sentences": sentences})
  else:
    return jsonify({"results": "Word(s) not found."})

# Account info for the user
@app.route('/sendScrollProgress/', methods=['POST'])
@login_required
def scrollProgressUpdate():
  scrolled = request.json.get('scroll', '')
  #print(scrolled)
  fileName, c = User().get_file_chapter()

  attributes = textDB[fileName].find_one({"_id": fileName})

  chapter = attributes.get("current_chapter")

  chapterInt = int(chapter) - 1  # fix the indexing and chapter number error

  if(attributes):
    textDB[fileName].update_one(
      {"_id": fileName},
      {
        "$set": {
            f"scroll_progress.{str(chapterInt)}": scrolled
        }
      }
    )
  return jsonify('Scroll progress called')

# On page load the scroll progress needs to be retreived from the database and sent to JS to display correct position
@app.route('/getScrollProgress/', methods=['GET'])
@login_required
def getScrollProgress():

  fileName, chapter = User().get_file_chapter()

  chapterInt = int(chapter) - 1  # fix the indexing and chapter number error

  attributes = textDB[fileName].find_one({"_id": fileName})

  if attributes:
    scroll_progress = attributes.get("scroll_progress", [])[chapterInt]
  print("Get scroll progress", scroll_progress)
  return jsonify({'scroll': scroll_progress})


@app.route('/getColorList/<int:colorPosition>/', methods=['GET'])
@login_required
def getColorList(colorPosition):

  fileName, chapter = User().get_file_chapter()

  attributes = textDB[fileName].find_one({"_id": fileName})

  if attributes:
    keyList = attributes.get("key_list", [])

  dbColor = keyList[colorPosition][0]

  if(attributes):
    textDB[fileName].update_one(
      {"_id": fileName},
      {
        "$set": {
            f"current_color": str(dbColor)
        }
      }
  )
    

  keyList = attributes.get("key_list", [])
  label = None 

  for key in keyList:
      if dbColor == key[0]:
          label = key[1] 
          break  

  if label is not None:
      print("LABEL: ", label)
  else:
      print("No matching label found for dbColor:", dbColor)

  return jsonify({'dbColor': dbColor, 'label': label})

@app.route('/help')
@login_required
def help():
  return render_template('help.html')


@app.route('/dropText/<string:textName>/', methods=['POST'])
@login_required
def dropText(textName):
  # drop the requested text from the textStorage and analysisStorage DBS

  textDB[textName].drop()
  analysisDb[textName].drop()

  return jsonify({'message': 'Text dropped successfully'})


@app.route('/getNotes/<int:index>/', methods=['GET'])
@login_required
def getNotes(index):

  fileName, chapter = User().get_file_chapter()

  if(index >= 0):

    chapter = analysisDb[fileName].find_one({"_id": fileName + chapter})

    categoricalD = chapter['data']
    if(categoricalD[index]['notes'] != ''):
      notes = categoricalD[index]['notes']
    else:
      return jsonify({'message': 'No notes'})
    
    return jsonify({'notes': notes})
  
  
  return jsonify({'message': 'No sentence selected'})
@app.route('/updateNotes/', methods=['POST'])
@login_required
def updateNotes():
  
    data = request.json
    newNotes = data.get('text') 

    fileName, chapter = User().get_file_chapter()
    attributes = textDB[fileName].find_one({"_id": fileName})
    chapterInt = int(chapter) - 1  # fix the indexing and chapter number error
    lastIndex = attributes.get("current_index")[chapterInt]
    chapter_doc = analysisDb[fileName].find_one({"_id": fileName + chapter})
    categoricalD = chapter_doc['data']

    
    categoricalD[lastIndex]['notes'] = newNotes

    analysisDb[fileName].update_one(
        {"_id": fileName + chapter},
        {"$set": {"data": categoricalD}}
    )

    return jsonify({'message': 'Notes updated successfully'})


# Account info for the user
@app.route('/accountInfo/')
@login_required
def accountInfo():
   
    uid = User().get_Uid()
    globalTables = textDB.list_collection_names()
    tables = []

    for name in globalTables:
        if uid in name:
            tables.append(name)
            
    return render_template('account.html', tables=tables)



#Updating username and password
@app.route("/update_username/", methods=['POST'])
def update_username():
  
  new_username = request.json.get('name', '')
  return User().modify_user_name(new_username)

@app.route("/update_password/", methods=['POST'])
def update_password():
  
  new_password = request.json.get('password', '')
  return User().modify_user_password(new_password)
#
##################################################################################################
# App run
app.jinja_env.globals.update(convert_to_rgb=convert_to_rgb)
if __name__ == '__main__':

  app.jinja_env.auto_reload = True
  app.config['TEMPLATES_AUTO_RELOAD'] = True
  app.run()