from flask import Flask, render_template, session, redirect, jsonify
from user.models import User # Imports user class created in models.py
from functools import wraps
import pymongo

app = Flask(__name__)
# Should probably change this
app.secret_key = 'Dreamteam'

# Database 'Dreamteam'
client = pymongo.MongoClient('localhost', 27017)
loginDB = client['loginInfo']
textDB = client['textStorage']


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
def find_sentence(chapter, sent_num):

  # Fixes indexing in dashboard where when clicking the first
  # sentence it was not returning 0, giving referenced before
  # assignment error
  sent_num += 1

  collection = textDB['ulyssesChap1']
  document = collection.find_one({"_id": chapter})

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

# Find characters function
def find_characters(chapter, num):

    collection = textDB['analysis']
    document = collection.find_one({"_id": chapter})
    categoricalD = document['data']
    print(len(categoricalD[0]['sentences'][num]))

    li = (categoricalD[0]['sentences'][num]['actors'])
    return "\n".join(li)

# Print chapter, returns sentence and sentence num
def print_chapter(chapter):

  collection = textDB['ulyssesChap1']
  document = collection.find_one({"_id": chapter})
  text = []

  for paragraph in document["content"]:
    # if a sentence add to text
    if("sentences") in paragraph:
        # iterate accross each paragrah sentence
        for sentenceBlock in paragraph["sentences"]:
            sentenceNum = sentenceBlock["sentenceNum"]
            sentence = sentenceBlock["text"]
            text.append(sentence)

  return text

# prints plain text line by line depending on what chapter was input
def output_text(chapter):

    collection = textDB['ulyssesChap1']
    document = collection.find_one({"_id": chapter})

    textRet=[]

    for paragraph in document["content"]:
        # if a sentence add to text
        if("sentences") in paragraph:
           textRet.append(paragraph['sentences'])
    
    return textRet

# returns the number of sentences that are in the given paragraph
def findParagraphLen(paragraph):
   return len(paragraph)

# denotes paragraphs by the ~&~ sign to print them correctly on the website
def returnText_originalParagraphs(chapter):

  retVal = []

  ret = output_text(chapter)
  #print(ret[0][0]['text'])

  #print(findParagraphLen(ret))

  for i in range(findParagraphLen(ret)):
    for j in range(findParagraphLen(ret[i])):
      retVal.append(ret[i][j]['text'])
    retVal.append("%&%")

  return retVal

#
##################################################################################################
# App routes for HTML Webpages

# Default page
@app.route('/')
def home():
  return render_template('index.html')

# Dashboard route, Login required
@app.route('/dashboard/')
@login_required
def dashboard():
    currentIndex = 0
  
    paragraphs = returnText_originalParagraphs('chap1')
    chapter = print_chapter('chap1')
    sentenceRet = find_sentence('chap1', currentIndex)
    return render_template('dashboard.html', paragraphs=paragraphs, chapter=chapter, retval=sentenceRet, currentIndex=currentIndex)

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

# Dashboard index route, calls find_sentence with passed index
@app.route('/dashboard/<int:index>')
@login_required
def selected_sentence(index):

  #print(index)
  sentenceRet = find_sentence('chap1', index)

  return jsonify({'index': sentenceRet[0],'sentence':sentenceRet[1]})



#
##################################################################################################
# App run
if __name__ == '__main__':
  app.jinja_env.auto_reload = True
  app.config['TEMPLATES_AUTO_RELOAD'] = True
  app.run(debug=True, port=5959)
