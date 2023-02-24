from flask import Flask, render_template, request
from dotenv import load_dotenv
import os

# reading .env file
load_dotenv('.env.dev')

# Flask constructor
app = Flask(__name__, template_folder="templates", static_folder="static") 


# loading Environment variables to run.py
app.config['USER_DB'] = os.environ['USER_DB']
app.secret_key = os.environ['SECRET_KEY']


#----------------------------------------------------------------
# Login page
@app.route('/', methods =["GET", "POST"])
def login():           
    return render_template("login.html", value="Please login to continue.")

# Create new account
@app.route('/register', methods=['GET'])
def register():
    return render_template("create_account.html")


# ------------- MAIN --------------------------        
if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)