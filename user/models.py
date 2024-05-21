from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256 # Encrypts password, VScode labels as unresolved but works
from datetime import datetime
import pytz
import pymongo
import uuid

# Database
client = pymongo.MongoClient('mongodb://jkretschmer1:aiN4mooheitaez@localhost:27017/?authSource=admin')
db = client['loginInfo']

class User:

  # Creates session for user
  def start_session(self, user):
  
    del user['password']
    session['logged_in'] = True
    session['user'] = user

    return jsonify(user), 200
  

  def signup(self):

    id = uuid.uuid4().hex

    # Create the user object
    user = {
      "_id": id,
      "name": request.form.get('name'),
      "password": request.form.get('password'),
      "current_color": '#ff0000',
      "current_text": None,
      "current_chapter": None,
      "current_index": 0
    }

    # Create logging collection
    log = {
        "_id": id,
        "content": []
    }
    db.sessionInfo.insert_one(log)  # set the user specific log id

    # Encrypt the password
    user['password'] = pbkdf2_sha256.encrypt(user['password'])

    # Check for existing username
    if db.users.find_one({ "name": user['name'] }):
      return jsonify({ "error": "Username already in use" }), 400

    # Inserts user into mongoDB collection loginInfo
    if db.users.insert_one(user):
      return self.start_session(user)

    return jsonify({ "error": "Signup failed" }), 400
  
  # Clears session and redirects to index
  def signout(self):

    if 'user' in session:
      user = db.users.find_one({"_id": session['user']['_id']})

      if user:
        signout_time = datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M')
        db.users.update_one(
          {"_id": user['_id']},
          {"$set": {"signout_time": signout_time}}
        )

    session.clear()       # Clear session 
    return redirect('/joyce')  # Redirect to the index page
  
  # Checks database for matching user'name' to login
  def login(self):

    user = db.users.find_one({
      "name": request.form.get('name')
    })

    if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
      return self.start_session(user)
    
    return jsonify({ "error": "Invalid login" }), 401
  
  def log_message(self, message, verbose=False):

    if verbose:
      print("Models.py: LOG_ERROR Function Called.\n")

    timestamp = datetime.now(pytz.timezone('US/Eastern')).strftime('%d-%m-%Y %H:%M:%S')
      
    if 'user' in session:
      user = db.users.find_one({"_id": session['user']['_id']})

      db.sessionInfo.update_one(
        {"_id": user['_id']},
        {"$push": {"content": '[' + timestamp + '] ' + message}}  
    )
      
  def text_index_info(self, collection, verbose=False):

    if verbose:
      print("Models.py: TEXT_INDEX_INFO Function Called.\n")
      
    if 'user' in session:
      user = db.users.find_one({"_id": session['user']['_id']})

      if user:
        db.users.update_one(
          {"_id": user['_id']},
          {"$set": {"current_text": collection}},
        )

  def modify_user_color(self, color, verbose=False):

    if verbose:
      print("Models.py: MODIFY_USER_COLOR Function Called.\n")

    if 'user' in session:
      user = db.users.find_one({"_id": session['user']['_id']})
    
      if user:
          db.users.update_one(
            {"_id": user['_id']},
            {
              "$set": {
                  "current_color": color
              }
            }
          )

          return {"message": "Color updated successfully"}, 200
      else:  
        return {"error": "User not found"}, 404
    else:
        return {"error": "User not authenticated"}, 401

  def get_user_color(self, verbose=False):

    if verbose:
      print("Models.py: GET_USER_COLOR Function Called.\n")

    current_color = None

    if 'user' in session:
      user = db.users.find_one({"_id": session['user']['_id']})
    
      if user:
        current_color = user.get("current_color")

        if verbose:
          print("current_color: ", current_color)

    return current_color

  def modifyLastChapter(self, collection, lastChapter, verbose=False):

    if verbose:
      print("Models.py: MODIFYLASTCHAPTER Function Called.\n")
      
    if 'user' in session:
      user = db.users.find_one({"_id": session['user']['_id']})

      if user:
        db.users.update_one(
          {"_id": user['_id']},
          {
            "$set": {
                "current_text": collection,
                "current_chapter": lastChapter,
                "current_index": 0
            }
          }
        )
  

  def modifyLastChapterIndex(self, collection, lastChapter, lastIndex, sentence, verbose=False):

    if verbose:
      print("Models.py: MODIFYLASTCHAPTERINDEX Function Called.\n")
      
    if 'user' in session:
      user = db.users.find_one({"_id": session['user']['_id']})

      if user:
        db.users.update_one(
          {"_id": user['_id']},
          {
            "$set": {
                "current_text": collection,
                "current_chapter": lastChapter,
                "current_index": lastIndex,
                "current_sentence": sentence
            }
          }
        )

        #"current_paragraph": paragraph,
  def send_highlighted_sentence(self, phrase, verbose=False):

    if verbose:
      print("Models.py: SEND_HIGHTLIGHTED_SENTENCE Function Called.\n")

    if 'user' in session:
      user = db.users.find_one({"_id": session['user']['_id']})

      if user:
        db.users.update_one(
          {"_id": user['_id']},
          {
            "$set": {
                "current_phrase": phrase
            }
          }
        )

  def find_argument_info(self, verbose=False):

    if verbose:
      print("Models.py: FIND_ARGUMENT_INFO Function Called.\n")

    if 'user' in session:
      user = db.users.find_one({"_id": session['user']['_id']})

      if user:
        current_text = user.get("current_text")
        current_chapter = user.get("current_chapter")
        current_index = user.get("current_index")

      if verbose:
        print(current_text, current_chapter, current_index)
    
      return current_text, current_chapter, current_index
  
    return jsonify({ "error": "find_argument_info function" }), 401
  
  def get_file_chapter(self, verbose=False):

    if 'user' in session:
      user = db.users.find_one({"_id": session['user']['_id']})

      if user:
        current_file = user.get("current_text")
        current_chapter = user.get("current_chapter")

        return current_file, current_chapter

    return jsonify({ "error": "get_file_chapter function" }), 401
  
  def get_index(self, verbose=False):

    if 'user' in session:
      user = db.users.find_one({"_id": session['user']['_id']})

      if user:
        current_index = user.get("current_index")

        if current_index == '':
          return 0
        
        return current_index

    return jsonify({ "error": "get_index function" }), 401

  def get_Uid(self, verbose=False):

    if verbose:
      print("Models.py: GET_UID Function Called.\n")

    if 'user' in session:
      user = db.users.find_one({"_id": session['user']['_id']})

    return session['user']['_id']
  
  def get_keyList(self, verbose=False):

    if verbose:
      print("Models.py: GET_KEYLIST() Function Called.\n")

    if 'user' in session:
      user = db.users.find_one({"_id": session['user']['_id']})

      if user:
        key_list = user.get("key_list")

        if key_list == None:

          db.users.update_one(
          {"_id": user['_id']},
          {
            "$set": {
              "key_list": [('#000000', '+'), ('#000000', '+'), ('#000000', '+'),
                           ('#000000', '+'), ('#000000', '+'), ('#000000', '+')]
            }
          }
          )

        return key_list
      
    return jsonify({ "error": "get_keylist function" }), 401

  def get_phrase(self, verbose=False):

    if verbose:
      print("Models.py: GET_PHRASE Function Called.\n")

    if 'user' in session:
      user = db.users.find_one({"_id": session['user']['_id']})

      if user:
        current_phrase = user.get("current_phrase")

        return current_phrase

    return jsonify({ "error": "get_phrase function" }), 401
  
  def find_sentence_length(self, verbose=False):

    if verbose:
      print("Models.py: FIND_SENTENCE_LENGTH Function Called.\n")

    if 'user' in session:
      user = db.users.find_one({"_id": session['user']['_id']})

      if user:
        current_sentence = user.get("current_sentence")

        if verbose:
          print("find_sentence_length returned sentence: ", current_sentence)

        return len(current_sentence)
    
    return jsonify({ "error": "find_sentence_length function" }), 401
  
  def modify_user_name(self, new_username):

    if 'user' in session:
      user = db.users.find_one({"_id": session['user']['_id']})

      #if db.users.find_one({ "name": user['name'] }):
      #  return { "error": "Username already in use" }
    
      if user:
          db.users.update_one(
            {"_id": user['_id']},
            {
              "$set": {
                  "name": new_username
              }
            }
          )

          return {"message": "userName updated successfully"}, 200
      
      else:  
        return {"error": "User not found"}, 404
    else:
        return {"error": "User not authenticated"}, 401
    
  def modify_user_password(self, new_password):

    new_password = pbkdf2_sha256.encrypt(new_password)

    if 'user' in session:
      user = db.users.find_one({"_id": session['user']['_id']})
    
      if user:
          db.users.update_one(
            {"_id": user['_id']},
            {
              "$set": {
                  "password": new_password
              }
            }
          )

          return {"message": "password updated successfully"}, 200
      else:  
        return {"error": "password not found"}, 404
    else:
        return {"error": "password not authenticated"}, 401

