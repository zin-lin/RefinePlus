import os
import bcrypt
from flask import *
from flask_cors import *
from flask_bcrypt import *

import respositories
from models import *

#  set up app
app = Flask(__name__)
# configuration
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type' # allows CORS
app.config['SECRETE_KEY'] = 'annex-refine+-llbt34whatis67' # set up Database with SQLAlchemy
app.secret_key = 'annex-refine+-llbt34whatis67'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///server.db'

# Make sessions permanent
app.config['SESSION_PERMANENT'] = True

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

#inits
bcrypt = Bcrypt(app)
db.init_app(app)


# Create database
with app.app_context():
    db.create_all()
    db.session.commit()
#session.permanent = True

@app.route("/api/")
def default():
    return "Hello"

#get user detail service to get user name
@app.route("/api/get-user/<uid>")
@cross_origin()
def get_user_deatils_service(uid):
    try:
        user = User.query.get(uid)
        if user is None:
            return ""
        return user.get_email().split("@")[0]
    except:
        return ""


# dummy home page
@app.route("/home")
@cross_origin()
def home():
    return "Hello World"


# Checking if Authenticated
# returns "" if not, if so return user id
@app.route("/api/authed")
@cross_origin()
def if_authed():
    try:
        value = session.get('user_id') # get user_id
        if value is None:
            return ""
        elif value.startswith("<"):
            return ""
        return value
    except:
        return ""


# Logging Out
@app.route("/api/logout")
@cross_origin()
def logout():
    try:
        session.pop('user_id') # clear user cookies
        return "Sucessful Logout"
    except:
        return "Unsuccessful Logout"


# Register new user then log in
@app.route('/api/register', methods= ['GET','POST'])
@cross_origin()
def register():
    email = request.json['email']
    password = request.json['password']

    user_exists=False
    try:
        user_exists = User.query.filter_by(email=email).first()
    except:
        print("table hasn't been created, creating table")


    hashed = bcrypt.generate_password_hash(password) # creating password hash
    new_user = User(email = email, password= hashed)

    if user_exists:
        return jsonify({"error":"Ready as I'll ever be"}), 409

    db.session.add(new_user)
    db.session.commit()
    session['user_id'] = new_user.id

    return "Hello"


# login, check if user id exist in database
@app.route("/api/login", methods=["GET", "POST"])
@cross_origin()
def login():
    email = request.json['email']
    password = request.json['password']

    user_exists=None
    try:
        user_exists = User.query.filter_by(email=email).first()
    except:
        print("table hasn't been created, creating table")

    if user_exists is None:
        return jsonify({"error":"unauthed"}), 401 # invalid credential

    if not bcrypt.check_password_hash(user_exists.password, password):
        return jsonify({"error":"wrong credentials"}), 401 # invalid credential

    session['user_id'] = user_exists.id
    return "Sucessful Login"


# Update user details
# get data from request form sent from
@app.route("/api/update-user-details", methods = ["GET", "POST"])
@cross_origin()
def update_udeatails():
    name = request.json['name']
    profession = request.json['profession']
    api = request.json['api']
    pic = request.json['profile_pic']
    uid = request.json["uid"]
    if uid != session.get('user_id'):
        return 'invalid access' # security feature
    detail = UserDetails.query.filter_by(uid=uid).first()
    if detail:
        detail.name = name
        detail.api = api
        detail.profile_pic = pic
        detail.profession = profession + uid
        db.session.commit()
        return "Successfully Updated"

    else:
        detail = UserDetails(uid = uid, profession = profession, api = '0', profile_pic = pic, name = name)
        db.session.add(detail)
        db.session.commit()
        return "Successfully Created User Details"


# Get user details
@app.route("/api/get-user-details/<uid>", methods = ["GET"])
@cross_origin()
def get_user_details_all (uid):
    detail = UserDetails.query.filter_by(uid = uid).first() #if exists
    if detail is None:
        detail = UserDetails(profession = "", api = "", profile_pic = "", name ="", uid = "")

    return jsonify({"profession": detail.profession.replace(uid, ''), "api": detail.api, "profile_pic":detail.profile_pic,
                        "name":detail.name }) # return user as json


# Add a new book
# post and get methods
@app.route("/api/addproject/", methods = ["GET", "POST"])
@cross_origin()
def add_book():
    data = request.form
    title = request.form.get('title')
    uid = data.get('uid')

    if session.get('user_id') != uid:
        return 'access denied'

    # Access the file data
    file_data = request.files.get('file')
    proj = respositories.Project(uid, title, file_data, True )
    # write to database
    new_project = Project(id=proj.id, uid=proj.uid, title=proj.title, filename=proj.fil)
    db.session.add(new_project)
    db.session.commit() # db commit
    return proj.id


# Get Book Id and Title object
@app.route("/api/get-titles/<uid>")
@cross_origin()
def get_title(uid):
    titles = Project.query.filter_by(uid=uid).with_entities(Project.title, Project.id).all()
    titles = [{'title':title[0], 'bid':title[1]} for title in titles]
    return titles

# Get Book as a json object
@app.route("/api/getbook/<bid>")
@cross_origin()
def get_book(bid):
    return respositories.Project.getBook(bid)


# Update Book Details
@app.route('/api/updateproject/<bid>', methods= ['POST'])
@cross_origin()
def update_book(bid):
    proj = Project.query.filter_by(id=bid).first() # get book
    if proj.uid != session.get('user_id'):
        return "invalid access"

    title = request.form.get('title')
    file_data = request.files.get('file')
    respositories.Project.updateBook(bid, title, file_data)
    project = Project.query.filter_by(id=bid).first()
    project.title = title
    db.session.commit()

    return 'ok'


# Get Project Details
@app.route('/api/get-project-details/<bid>', methods= ['GET'])
@cross_origin()
def get_project_details(bid):
    proj = Project.query.filter_by(id=bid).first() # get book
    if proj.uid != session.get('user_id'):
        return "invalid access"

    return respositories.Project.get_project_details(bid)

# Get Rows
@app.route('/api/get-project-rows/<len>/<pid>', methods = ['GET'])
@cross_origin()
def get_project_rows(len, pid):
    return respositories.Project.get_project_rows_len(len, pid)

@app.route('/api/change-cell/', methods = ['POST'])
def change_cell():
    bid = request.form.get('bid')
    att = request.form.get('att')
    idx = (int)(request.form.get('idx')) # cast to int
    val = request.form.get('val')
    print(att)
    print(idx)
    print(val)

    return respositories.Project.change_cell(val, att, idx, bid)

# index
@app.route('/')
def index():
    return 'hello world'

# run main program
if __name__ == '__main__':
    app.run(debug = True)
