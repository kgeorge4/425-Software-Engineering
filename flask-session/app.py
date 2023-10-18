from flask import Flask, render_template, session, redirect
from functools import wraps
import pymongo

app = Flask(__name__)
# Should probably change this
app.secret_key = 'Dreamteam'

# Database
client = pymongo.MongoClient('localhost', 27017)
db = client['loginInfo']

# Decorators
def login_required(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs)
    else:
      return redirect('/')
  
  return wrap

# Routes
from user import routes

# Default page
@app.route('/')
def home():
  return render_template('index.html')

# Dashboard page
@app.route('/dashboard/')
@login_required
def dashboard():
  return render_template('dashboard.html')