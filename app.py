from flask import Flask, redirect, render_template, request, session
from flask_socketio import SocketIO, emit, send
from flask_session import Session
from helpers import login_required
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from re import match
from imagekitio import ImageKit

import api.search as searchApiRoute

#Configures flask
app = Flask(__name__)
app.config["SECRET_KEY"] = "gVkYp3s6" # https://flask.palletsprojects.com/en/1.0.x/config/#SECRET_KEY
app.config["SESSION_PERMANENT"] = False # https://flask-session.readthedocs.io/en/latest/#configuration
app.config["SESSION_TYPE"] = "filesystem" # https://flask-session.readthedocs.io/en/latest/#configuration

app.config["TEMPLATES_AUTO_RELOAD"] = True  # Updates template changes without restarting flask for debugging. https://flask.palletsprojects.com/en/1.0.x/config/#TEMPLATES_AUTO_RELOAD

#Configures flask_session
Session(app)

#Configures flask_socketio
socketio = SocketIO(app)

#Configures database
db = SQL("sqlite:///database.db")

#Configures imagekit.io
imagekit = ImageKit(
    private_key='private_n6X1lvtdx2Cj59FaO9ZLz9udhlE=',
    public_key='public_+CaF11oA3XIvdEFms4DGqnOLCmI=',
    url_endpoint = 'https://ik.imagekit.io/w7b827uhp'
)

searchApiRoute.initializeSearchApiRoute(app, db)


@app.route("/", methods=["GET", "POST"])
def index():
    # Checks if the user is signed in. If so, redirect the user to the main forum. If not, render the index page containing the register and login links for the user.
    if session.get("user_id") != None:
        return redirect("/home.html")
    else:
        return render_template("index.html")

# Register Route
@app.route("/register.html", methods=["GET", "POST"])
def register():
    # Variables that can be passed to the client to indicate whether or not the password entered is too short or long when registering.
    isShortPassword = False
    isLongPassword = False
    # Variables that can be passed to the client to indicate whether or not the username entered is too short or long when registering.
    isShortUsername = False
    isLongUsername = False
    # Variable that can be passed to the client to indicate whether or not the submitted field contains only valid characters.
    isInvalidCharacters = False
    isUsernameTaken = False

    # On register submission:
    if request.method == "POST":
        # Gets the username and password submitted.
        username = request.form["username"]
        password = request.form["password"]
        # ============================================ Validation ===========================================#
        # Check: Username must be at least 1 character.                                                      #
        if len(username) < 1:                                                                                #
            isShortUsername = True                                                                           #
        # Check: Username can't exceed 15 characters.                                                        #
        if len(username) > 15:                                                                               #
            isLongUsername = True                                                                            #
        # Check: Username can't contain any characters that is not:                                          #
        #        a-z, A-Z, -, _, or 1, 2, 3, 4, 5, 6, 7, 8, 9, 0                                             #
        if not match("^[a-zA-Z-_1234567890]*$", username):                                                   #
            isInvalidCharacters = True                                                                       #
        if len(db.execute("SELECT * FROM users WHERE username=?", username)) != 0:                           #
            isUsernameTaken = True                                                                           #
                                                                                                             #
                                                                                                             #
        # Check: Password must be at least 5 characters.                                                     #
        if len(password) < 5:                                                                                #
            isShortPassword = True                                                                           #
        # Check: Password can't exceed 32 characters.                                                        #
        if len(password) > 32:                                                                               #
            isLongPassword = True                                                                            #
                                                                                                             #
        # Return all the checks to the client if any of the checks were failed.                              #
        if ((isShortPassword == True) or                                                                     #
             (isLongPassword == True) or                                                                     #
             (isShortUsername == True) or                                                                    #
             (isLongUsername == True) or                                                                     #
             (isInvalidCharacters == True) or                                                                #
             (isUsernameTaken == True)):                                                                     #
                                                                                                             #
            return  render_template("register.html", isShortPassword=isShortPassword,                        #
                                                     isLongPassword=isLongPassword,                          #
                                                     isShortUsername=isShortUsername,                        #
                                                     isLongUsername=isLongUsername,                          #
                                                     isInvalidCharacters=isInvalidCharacters,                #
                                                     isUsernameTaken=isUsernameTaken)                        #
        #====================================================================================================#

        # Hashes the password
        passwordHash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        # Stores the now registered username and password hash in the database.
        try:
            db.execute("INSERT INTO users(username, hash) VALUES(?, ?);", username, passwordHash)
        except:
            return redirect("/")

        return redirect("/")

    return render_template("register.html")

#Login Route
@app.route("/login.html", methods=["POST", "GET"])
def login():
    # Boolean variable that can be passed to the client that can be used to decide whether or not to render an "invalid username or password" message to the user upon a failed login.
    isInvalid = False

    # On login submission:
    if request.method == "POST":
        # Stores the submited username and password from the login form as variables.
        username = request.form["username"]
        password = request.form["password"]

        # Queries the database for the matching username.
        user = db.execute("SELECT * FROM users WHERE username=?", username)

        # Logs the user in.
        #
        # Doesn't login if:
        # 1. there's multiple rows returned by the query, as there should only be one row since usernames are unique (this shouldn't occur unless the database was manually changed)
        # 2. there's no rows returned returned by the query, then the username doesn't exist in the database
        # 3. the password is incorrect, as the stored password hash does not match up with the password entered
        if ( len(user) != 1 ) or ( check_password_hash(user[0]["hash"], password) == False ):
            ### print(f"Login failed from {username}")
            isInvalid = True
            return render_template("login.html", isInvalid=isInvalid)
        # Else logs in if there's no errors.
        else:
            ### print(f"Login success from {username}")
            # Sets user's unique id as a cookie.
            session["user_id"] = user[0]["id"]
            return redirect("/")

    # On visiting the page:
    else:
        return render_template("login.html")

#Logout Route
@app.route("/logout")
def logout():
    # Clears session cookies.
    session.clear()
    return redirect("/")


##########################################################################################################################################################################################
##########################################################################################################################################################################################


@app.route("/thread/<int:topic_id>", methods=["GET", "POST"])
@login_required
def thread(topic_id):
    if request.method == "POST":
        reply = request.form["reply"]
        user_id = session.get("user_id")
        username = db.execute("SELECT * FROM users where id=?", user_id)[0]["username"]
        date = db.execute("SELECT DATETIME()")[0]["DATETIME()"]
        pfp = db.execute("SELECT pfp_link FROM users WHERE username=?", username)[0]["pfp_link"]

        db.execute("INSERT INTO posts(author_id, topic_id, content, date) VALUES (?,?,?,?) ", user_id, topic_id, reply, date)
        
        replies = db.execute("SELECT * FROM posts WHERE topic_id=? ORDER BY date ASC", topic_id)
        for r in replies:
            author_id = r["author_id"]
            replier_username = db.execute("SELECT username FROM users WHERE id=?", author_id)
            replier_pfp = db.execute("SELECT pfp_link FROM users WHERE id=?", author_id)
         
            r["replier_pfp"] = replier_pfp[0]["pfp_link"]
            r["replier_username"] = replier_username[0]["username"]


        thread = db.execute("SELECT * FROM topics WHERE topic_id=?", topic_id)[0]
        
        author_id = thread["author_id"]
        author_pfp = db.execute("SELECT pfp_link FROM users WHERE id=?", author_id)
        thread["author_pfp"] = author_pfp[0]["pfp_link"]

        
        
        return render_template("thread.html", thread=thread, topic_id=topic_id, replies=replies, username=username, pfp=pfp)
    else:
        user_id = session.get("user_id")
        username = db.execute("SELECT * FROM users where id=?", user_id)[0]["username"]
        replies = db.execute("SELECT * FROM posts WHERE topic_id=? ORDER BY date ASC", topic_id)
        pfp = db.execute("SELECT pfp_link FROM users WHERE username=?", username)[0]["pfp_link"]
          
        for r in replies:
            author_id = r["author_id"]
            replier_username = db.execute("SELECT username FROM users WHERE id=?", author_id)
            replier_pfp = db.execute("SELECT pfp_link FROM users WHERE id=?", author_id)
         
            r["replier_pfp"] = replier_pfp[0]["pfp_link"]
            r["replier_username"] = replier_username[0]["username"]

        thread = db.execute("SELECT * FROM topics WHERE topic_id=?", topic_id)

        # Render 404
        if len(thread) == 0:
          return render_template("404.html")

        thread = thread[0]
        
        author_id = thread["author_id"]
        author_pfp = db.execute("SELECT pfp_link FROM users WHERE id=?", author_id)
        thread["author_pfp"] = author_pfp[0]["pfp_link"]


        return render_template("thread.html", thread=thread, topic_id=topic_id, replies=replies, username=username, pfp=pfp)

@app.route("/home.html")
@login_required
def home():
    user_id = session.get("user_id")
    threads = db.execute("SELECT * FROM topics ORDER BY topic_id DESC")

    # Appends author_name into threads
    for thread in threads:

        
        n = db.execute("SELECT username FROM users where id=?", thread["author_id"])[0]["username"]
        #print(n)
        thread["author_name"] = n

        
        thread["posts_count"] = db.execute("SELECT COUNT(*) FROM posts WHERE topic_id=?", thread["topic_id"])[0]["COUNT(*)"]
        

    #print(threads)

    
    return render_template("home.html", threads=threads, user_id=user_id)

@app.route("/post.html", methods=["POST", "GET"])
@login_required
def post():
    if request.method == "POST":
        topic = request.form["topic"]
        content = request.form["content"]
        author_id = session["user_id"]
        date = db.execute("SELECT DATETIME()")[0]["DATETIME()"]
        # todo: validation
        db.execute("INSERT INTO topics(author_id, title, content, date) VALUES(?, ?, ?, ?);", author_id, topic, content, date)
        return redirect("/home.html")

    else:

        return render_template("post.html")

@app.route("/profile/profile.html", methods=["POST", "GET"])
@login_required
def profile():
        # Returns the current logged in user's username and set it to the variable "username"
        username = db.execute("SELECT username FROM users WHERE id=?", session.get("user_id"))
        username = username[0]["username"]

        # Uploading profile pictures (pfp).
        if request.method == "POST":
            # Gets the user's uploaded pfp file from the form.
            file = request.files["upload"]

            # todo: file validation

            # Clears all previous images in the user's pfp folder.
            # /Users/username/pfp
            for i in imagekit.list_files({"path": "/Users/" + username + "/pfp"})["response"]:
                fileId = (i["fileId"])
                imagekit.delete_file(fileId)

            # Uploads the uploaded pfp file to imagekit in the user's respective pfp folder.
            # /Users/username/pfp
            file_name = imagekit.upload_file(file, "upload", options={"folder": "/Users/" + username + "/pfp", "use_unique_file_name": True,})

            # Stores image url into database
            db.execute("UPDATE users SET pfp_link=? WHERE username=?", file_name["response"]["url"], username)

            # Get's the user's corresponding pfp file from database and returns it to the form.
            pfp = db.execute("SELECT pfp_link FROM users WHERE username=?", username)[0]["pfp_link"]
            return render_template("profile.html", pfp=pfp)
        else:
            pfp = db.execute("SELECT pfp_link FROM users WHERE username=?", username)[0]["pfp_link"]
            return render_template("profile.html", pfp=pfp)





app.run(host='0.0.0.0', port=5000)