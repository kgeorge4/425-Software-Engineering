from flask import Flask
from app import app # Imports app instance created in app.py
from user.models import User # Imports user class created in models.py

@app.route('/user/signup', methods=['POST'])
def signup():
  return User().signup()

@app.route('/user/signout')
def signout():
  return User().signout()

@app.route('/user/login', methods=['POST'])
def login():
  return User().login()
