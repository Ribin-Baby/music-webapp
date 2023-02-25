from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from modules import generate_uuid, DB, Webuser, convert, clean_text
from mutagen.mp3 import MP3  
from mutagen.easyid3 import EasyID3 
from dotenv import load_dotenv
import os, time

# reading .env file
load_dotenv('.env.dev')

# Flask constructor
app = Flask(__name__, template_folder="templates", static_folder="static") 
useragent = Webuser()

# loading Environment variables to run.py
app.config['UPLOAD_FOLDER'] = os.environ['UPLOAD_FOLDER']
app.config['USER_DB'] = os.environ['USER_DB']
app.config['MUSIC_DB'] = os.environ['MUSIC_DB']
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

@app.route('/home', methods=['GET'])
@login_required
def homepage():
    # song metadata with database
    db = DB(app.config['MUSIC_DB']) # LOAD
    music_list = db.read("music_db", data=None, many=True) # READ all aibums
    useragent.myalbums = db.read("music_db", ("uuid", useragent.uuid), many=True) # READ myalbums
    return render_template("home.html", items=music_list)

# myspace == myalbum
@app.route('/myspace')
@login_required
def myspace():
    # song metadata with database
    return render_template('myspace.html', items=useragent.myalbums)

# create music-direct link
@app.route('/music/<fileid>', methods=['GET'])
@login_required
def music(fileid):
    # song metadata with database
    db = DB(app.config['MUSIC_DB']) # LOAD
    filename, artist, _, uuid = db.read("music_db", ("file_id", fileid)) # READ
    can_delete = False
    if uuid == useragent.uuid:
        can_delete = True
    return render_template('music.html', title=filename, artist=artist, filename=filename, can_delete=can_delete)

# read audio from folder
@app.route('/play/<filename>')
@login_required
def play_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# download audio file from web
@app.route('/download/<filename>')
@login_required
def download_audio(filename):
    audio_path = app.config['UPLOAD_FOLDER'] + filename
    return send_file(audio_path, as_attachment=True, attachment_filename=filename)

# download audio file from web
@app.route('/delete/<filename>')
@login_required
def delete_audio(filename):
    print("DELETE: ", filename, ".mp3")
    
    # deleting song metadata from derver database
    db = DB(app.config['MUSIC_DB']) # LOAD
    db.remove("music_db", ("filename", filename))
    useragent.myalbums = db.read("music_db", ("uuid", useragent.uuid), many=True) # READ
    
    # deleting song from server folder
    file_path = app.config['UPLOAD_FOLDER'] + filename + ".mp3"
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print("The file does not exist")
    return redirect("/myspace", code=302)

# creating search function
@app.route('/search')
@login_required
def search():
    search_results = []
    query = request.args.get('query')
    # perform search based on query
    db = DB(app.config['MUSIC_DB']) # LOAD
    filedb = db.read("music_db", data=None, many=True) # READ all aibums
    for filename, artist, fileid, uuid in filedb:
        _query = clean_text(query)
        _filename = clean_text(filename)
        _artist = clean_text(artist)
        if _query in _filename or _query in _artist:
            search_results += [(filename, artist, fileid, uuid)]
    print(search_results)
    return render_template("home.html", items=search_results)

# music uploader - SAVE TO database
@app.route('/upload', methods=['POST'])
@login_required
def upload():
   if request.method == 'POST':
        file = request.files['audiofile']
        filename = file.filename
        if file and filename.endswith(".mp3"):
            # song metadata with database
            db = DB(app.config['MUSIC_DB']) # LOAD
            
            print(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            audio = MP3(filepath, ID3=EasyID3)
            
            hour, min, secs = convert(audio.info.length)
            duration = f"{min} Minutes {round(secs)} Seconds"
            print(audio)
            title = filename.split(".")[0]
            artist = "unknown"
            song_id = round(time.time())
            
            if "artist" in audio.keys():
                artist = audio['artist'][0]
            else:
                print("NO if entered..")
            print(f"""
                  AUDIO METADATA
                  --------------
                  |     Time   : {duration}
                  |     Title  : {title}
                  |     Artist : {artist}
                  |     song_id: {song_id}
                  --------------
                  """)
            print(useragent.uuid)
            db.insert("music_db", (title, artist, song_id, useragent.uuid)) # SAVE
            useragent.myalbums = db.read("music_db", ("uuid", useragent.uuid), many=True) # READ
            # Do something with the uploaded file
            return redirect("/myspace", code=302)
        else:
            # Do something with the uploaded file
            return 'Some error occured ! only supports mp3 file.'

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