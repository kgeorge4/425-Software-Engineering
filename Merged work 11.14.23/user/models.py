from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256 # Encrypts password, VScode labels as unresolved but works
import pymongo
import uuid

# Database
client = pymongo.MongoClient('localhost', 27017)
db = client['loginInfo']

class User:

  # Creates session for user
  def start_session(self, user):
  
    del user['password']
    session['logged_in'] = True
    session['user'] = user

    return jsonify(user), 200
  

  def signup(self):
    #print(request.form)

    # Create the user object
    user = {
      "_id": uuid.uuid4().hex,
      "name": request.form.get('name'),
      "password": request.form.get('password')
    }

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

    session.clear()

    return redirect('/')
  
  # Checks database for matching user'name' to login
  def login(self):

    user = db.users.find_one({
      "name": request.form.get('name')
    })

    if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
      return self.start_session(user)
    
    return jsonify({ "error": "Invalid login" }), 401
