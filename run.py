from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from modules import generate_uuid, DB, Webuser
from dotenv import load_dotenv
import os

# reading .env file
load_dotenv('.env.dev')

# Flask constructor
app = Flask(__name__, template_folder="templates", static_folder="static") 
useragent = Webuser()

# loading Environment variables to run.py
app.config['USER_DB'] = os.environ['USER_DB']
app.secret_key = os.environ['SECRET_KEY']

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


#----------------------------------------------------------------
# Define User model
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

    def get_id(self):
        return str(self.id)
    

#----------------------------------------------------------------
# Login page
@app.route('/', methods =["GET", "POST"])
def login():           
    if request.method == "POST":
       # getting input with name = fname in HTML form
       name = request.form.get("Uname")
       # getting input with name = lname in HTML form
       password = request.form.get("Pass")
       
       # user validation with database
       db = DB(app.config['USER_DB']) # LOAD
       
       try:
           uname, uuid = db.read("user_uuid", ("username", name)) # READ
           uuid, pwd = db.read("uuid_pwd", ("uuid", uuid)) # READ
           if pwd == password:
               useragent.username = uname
               useragent.uuid = uuid
               user_obj = User(uuid)
               login_user(user_obj)
               print(f"""
                     PASSWORD MATCH FOUND
                     --------------------
                     LOGIN CRIDENTIALS: 
                        |   USER: {uname} 
                        |   PWD : *******
                     """)
               
               return redirect("/home", code=302) 
           else:
               return render_template("login.html", value="Wrong password ! Try again.") 
           
       except Exception as e:
           print("Error MSG: ", e)
           
    return render_template("login.html", value="Please login to continue.")

# Create new account
@app.route('/register', methods=['GET'])
def register():
    return render_template("create_account.html")

# add new user to database
@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['Uname']
    email = request.form['Mail']
    password = request.form['Pass']
    
    if name!="" or password!="":
        # register new user 
        uuid = generate_uuid() # GENERATE - ID
        db = DB(app.config['USER_DB']) # LOAD
        db.insert("user_uuid", (name, uuid)) # SAVE
        db.insert("uuid_pwd", (uuid, password)) # SAVE
        
        print(f"""
            |     User: {name}
            |     Email: {email}
            |     Password: {password[0]}*****{password[-1]}
            |
            ---- CREATED SUCCESFULLY ----
            -----------------------------
            """)
    else:
        print("MSG: Invalid user cridentials.")
    
    # Do something with the user's input data here
    return redirect("/", code=302)

# Define logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    useragent.username = ""
    useragent.uuid = ""
    return redirect(url_for('login'))

# Define user loader function
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# ------------- MAIN --------------------------        
if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)