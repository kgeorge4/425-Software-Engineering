from flask import Flask, render_template, session, redirect, jsonify, request, redirect, url_for
from user.models import User # Imports user class created in models.py
from functools import wraps
import pymongo, os, subprocess, sys
import sys


app = Flask(__name__, root_path = '/var/www/html/joyce/')
# Should probably change this
app.secret_key = 'Dreamteam'
# Database 'Dreamteam'
client = pymongo.MongoClient('localhost', 27017)
loginDB = client['loginInfo']
textDB = client['textStorage']
# connect to the analysis portion of the textStorage database       analysis -> FILE_NAME -> FILENAME + chapnum -> { categories } ... {actors}
analysisDb = client['analysisStorage']

# File for storing uploaded text documents
UPLOAD_FOLDER = '/home/student/WebsiteVENV/front-end/Kevin/files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
def find_sentence(name, chapter, sent_num):

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

# Find characters function
def find_characters(name, chapter, num):
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
            if categories and categories[0].get('actors'):
                actors = categories[0]["actors"]
                return "\n".join(actors)

    # Return an empty list if any level of the data structure is missing
    return 'No characters found in database.'


# returns the number of chapters in the given text
def getNumChapters(name):
   
   collection = textDB[name]
   result = collection.find_one({"_id": name })
   retVal = result['chapters']
   return retVal
   

# Find characters function
def findInvolves(name, chapter, num, verbose=False):
  
  if verbose:
    print("fileName: ", name)
    print("chapterNum: ", chapter)
    print("num: ", num)

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
      if categories and categories[0].get('involves'):
        involves = categories[0]["involves"]
        return "\n".join(involves)

  # Return an empty list if any level of the data structure is missing
  return 'Nothing found in database.'

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

  if verbose:
    print("returnText_originalParagraphs() called in app.py\n")
    #print("Ret: ", ret)

    #print(ret[0][0]['text'])

    #print(findParagraphLen(ret))

  for i in range(findParagraphLen(ret)):
    for j in range(findParagraphLen(ret[i])):
      retVal.append(ret[i][j]['text'])
    retVal.append("¶")

  if verbose:
    print("retval: ", retVal)

  return retVal

def removeUID(fileName):
    return fileName.split("_")[0]

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
    globalTables = textDB.list_collection_names()
    tables = []

    for name in globalTables:
        if uid in name:
            tables.append(name)
  
    return render_template('loader.html', tables=tables)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    
    uid = User().get_Uid()

    # get the current directory
    cwd = os.getcwd()
    
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file:
        
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)


        try:
          # set execution environment
          venv_dir = os.path.expanduser("~/WebsiteVENV")

          # set path
          script_cmd = [os.path.join(venv_dir, 'bin', 'python3'), os.path.join(cwd + '/loader/', 'main.py'), '--fileName', filename, uid]
          subprocess.run(script_cmd)


        except Exception as e:
          return f"Error: {str(e)}"
        
        print("Upload successful\n")
        
        return redirect(url_for('loader'))
    

@app.route('/collectionInfo/<collection>', methods=['GET'])
@login_required
def collectionInfo(collection, verbose=True):

  if verbose:
    print("App.py: COLLECTION INFO TEXT Function Called")
    print("Collection: ", collection)

  retval = User().text_index_info(collection)

  if retval:
    return retval
  else:
    return jsonify(error='Failed to update collection info')


# Dashboard page
@app.route('/dashboard/<name>/<chapter>/')
@login_required
def dashboard(name, chapter):
  fileName = name
  chapterNum = chapter
  #currentIndex = 0
  currentIndex = User().get_index()
  numberOfChapters = getNumChapters(name)
  paragraphs = returnText_originalParagraphs(fileName, chapterNum)
  chapter = print_chapter(fileName, chapterNum)
  sentenceRet = find_sentence(fileName, chapterNum, currentIndex)
  
  fileNameDisplayed = removeUID(fileName)
  user_color = User().get_user_color()

  # modify user class data
  User().modifyLastChapter(fileName, chapterNum)

  return render_template('dashboard.html', numberOfChapters = numberOfChapters, fileNameDisplayed = fileNameDisplayed, 
    fileName = fileName, chapterNum = chapterNum, paragraphs=paragraphs, chapter=chapter, retval=sentenceRet, 
    currentIndex=currentIndex, user_color=user_color)

# Sign up route
@app.route('/user/signup', methods=['POST'])
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

# Account info for the user
@app.route('/accountInfo/')
@login_required
def accountInfo():
  return render_template('account.html')

# Dashboard index route, calls find_sentence with passed index
@app.route('/dashboard/<name>/<chapter>/<int:index>')
@login_required
def selected_sentence(name, chapter, index, verbose=False):

  fileName = name
  chapterNum = chapter

  sentenceRet,sentence = find_sentence(fileName, chapterNum, index)
  if verbose:
    print("selected_sentence() called in app.py\n")
    print("Selected sentence: ", sentenceRet, "\n")

  # modify user class data
  User().modifyLastChapterIndex(fileName, chapterNum, index, sentence)

  return jsonify({'index': sentenceRet,'sentence':sentence, 'fileName':fileName})

@app.route('/updateCharacters/<int:index>/', methods=['GET'])
@login_required
def update_characters(index, verbose=False):

  file_name, chapter = User().get_file_chapter()

  if verbose:
    print("update_characters() called in app.py\n")

  character_list = find_characters(file_name, chapter, index)
  #character_list = findInvoles(file_name, chapter, index)
  if verbose:
    print("file: ", file_name)
    print("chapter: ", chapter)
    print("index: ", index)
    print("character list: ", character_list)

  return jsonify({'characters': character_list})

@app.route('/updateInvolves/<int:index>/', methods=['GET'])
@login_required
def update_involves(index, verbose=False):

  file_name, chapter = User().get_file_chapter()

  if verbose:
    print("update_involves() called in app.py\n")

  involves_list = findInvolves(file_name, chapter, index)

  if verbose:
    print("file: ", file_name)
    print("chapter: ", chapter)
    print("index: ", index)
    print("involves list: ", involves_list)

  return jsonify({'involves': involves_list})


@app.route('/highlight/', methods=['POST'])
@login_required
def highlight_text(verbose=True):

  highlighted_text = request.json.get('highlightedText', '')
  # color = request.json.get('color', '')
  # User().modify_user_color(color)

  if verbose:
    print("highlight_text() called in app.py")
  
  phrase_length = len(highlighted_text)

  sentence_length = User().find_sentence_length()
  
  if verbose:
    print("Phrase: ", phrase_length)
    print("Sentence: ", sentence_length)

  if (phrase_length <= sentence_length): 

    # Sends phrase to database
    User().send_highlighted_sentence(highlighted_text)
  
    if verbose:
      # print("Color: ", color)
      print("Phrase: ", highlighted_text)

    # text, chapter, index = User().find_argument_info()
    # compare_phrase_to_dict(text, chapter, index, highlighted_text, color)

    return jsonify({'displayedText': highlighted_text})
  
  return jsonify({'displayedText': 'Please highlight text only within the sentence, not including the index.'})

@app.route("/sendColor/", methods=['POST'])
def send_color_to_server(verbose=True):
  
  color = request.json.get('color', '')

  if verbose:
    print("send_color_to_server() called with ", color)
  
  return User().modify_user_color(color)

@app.route("/submitHighlight/", methods=['POST'])
def compare_phrase_to_dict(verbose=True):
  
  if verbose:
    print("\ncompare_phrase_to_dict() called in app.py")

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

  paragraph_num = None
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

              if result.modified_count > 0 and verbose: 
                print(f'Updated: content.{paragraph["paragraphNum"]-1}.sentences.{sentence_index}.wordList.{i}.1: {color}')
               
              elif result.modified_count < 1 and verbose:
                print("Update failed.", result.raw_result)
                print(f'content.{paragraph["paragraphNum"]-1}.sentences.{sentence_index}.wordList.{i}.1: {color}')

          else:
            print("error: None type variable in if statement for collection.update.\n")
            return jsonify({"error": "Text not highlighted"}), 405
          
  return jsonify({"message": "Highlight submitted successfully"}), 200
#
##################################################################################################
# App run
if __name__ == '__main__':
  app.jinja_env.auto_reload = True
  app.config['TEMPLATES_AUTO_RELOAD'] = True
  app.run(debug=True)