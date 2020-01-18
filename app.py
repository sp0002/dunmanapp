# Python standard libraries
import json
import os
import sqlite3
from datetime import datetime, timedelta

# Third party libraries
from flask import Flask, redirect, request, url_for, render_template
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests

# Internal imports
from db import init_db_command, get_db
from user import User
year = str(datetime.today().year)
year = year[2:]
# Configuration
GOOGLE_CLIENT_ID = "171099557791-u72uro3ecbc2fcrjkbstrrh10kdrence.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "kTjpc7Pj1P7QO4X8YmALyZJf"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.unauthorized_handler
def unauthorized():
    return "You must be logged in to access this content.", 403


# Naive database setup
try:
    init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass

#admin emails
PERMS = ["ivan.ng.qifan@dhs.sg","gu.boyuan@dhs.sg","wee.jiawei.kevan@dhs.sg", "khoo.phaikchoo.carina@dhs.sg", "xun.shengdi@dhs.sg", "mathew.rithu.ann@dhs.sg", "liu.yixuan@dhs.sg", "tee.renwey@dhs.sg", "lim.valerie@dhs.sg"]

# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route("/")
def index():
    if current_user.is_authenticated:
        connection = sqlite3.connect("sqlite_db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM flagraising")
        levels = cursor.fetchall()
        connection.close()
        return render_template("index.html", admin=current_user.admin, levels=levels, user_email=current_user.name)
    else:
        return render_template("login2.html")


@app.route("/about")
@login_required
def about():
    return render_template("about.html", admin=current_user.admin)

@app.route("/competition")
@login_required
def competition():
    connection = sqlite3.connect("sqlite_db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM competition")
    competitions = cursor.fetchall()
    now = datetime.now()
    i = 0
    while i < len(competitions):
        eventdate = datetime.strptime(competitions[i][2], "%Y-%m-%d")
        if now > eventdate + timedelta(days=1):
            cursor.execute("DELETE FROM competition WHERE id={}".format(competitions[i][0]))
            competitions.pop(i)
        else:
            i += 1
    connection.commit()
    connection.close()
    return render_template("competition.html", admin=current_user.admin, competitions=competitions)

@app.route("/competition_details")
@login_required
def competition_details():
    

@app.route("/announcements")
@login_required
def announcements():
    connection = sqlite3.connect("sqlite_db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM announcement")
    announcements = cursor.fetchall()
    now = datetime.now()
    i = 0
    while i < len(announcements):
        eventdate = datetime.strptime(announcements[i][2], "%Y-%m-%d")
        if now > eventdate + timedelta(days=1):
            cursor.execute("DELETE FROM announcement WHERE id={}".format(announcements[i][0]))
            announcements.pop(i)
        else:
            i += 1
    connection.commit()
    connection.close()

    return render_template("announcements.html", admin=current_user.admin, announcements=announcements)

@app.route("/announcement_details")
@login_required
def announcements_details():
    _id = request.args.get("id")
    connection = sqlite3.connect("sqlite_db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM announcement WHERE id={}".format(_id))
    announcement = cursor.fetchone()
    connection.commit()
    connection.close()
    return render_template("announcement_details.html", admin=current_user.admin, announcement=announcement)

@app.route("/links")
@login_required
def links():
    return render_template("links.html", admin=current_user.admin)


@app.route("/totw")
@login_required
def totw():
    connection = sqlite3.connect("sqlite_db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM totw")
    totw = cursor.fetchall()
    connection.commit()
    connection.close()
    return render_template("totw.html", admin=current_user.admin, totw=totw)

@app.route("/submit")
@login_required
def submit():
    if current_user.admin == 1:
        return render_template("submit.html", admin=current_user.admin)
    else:
        return "Unauthorized user"

@app.route("/submit2", methods=["POST"])
@login_required
def submit2():
    group = request.form.get("group")
    if current_user.admin == 1:
        return render_template("submit2.html", admin=current_user.admin, group=group)
    else:
        return "Unauthorized user"

@app.route("/submission", methods=["POST"])
@login_required
def submission():
    if current_user.admin == 1:
        group = request.form.get("group")
        if group == "announcements" or group == "competition":
            title = request.form.get("title")
            eventdate = request.form.get("eventdate")
            people_list = request.form.getlist("people")
            people = ""
            for a in people_list:
                people = people + a + ", "
            people = people[:-2]
            details = request.form.get("details")

            if group == "announcements":
                db = get_db()
                db.execute(
                    "INSERT INTO announcement (title, eventdate, people, details) "
                    "VALUES (?, ?, ?, ?)",
                    (title, eventdate, people, details)
                )
                db.commit()
                
            elif group == "competition":
                db = get_db()
                db.execute(
                    "INSERT INTO competition (title, eventdate, people, details) "
                    "VALUES (?, ?, ?, ?)",
                    (title, eventdate, people, details)
                )
                db.commit()
        else:
            y1 = request.form.get("y1")
            y2 = request.form.get("y2")
            y3 = request.form.get("y3")
            y4 = request.form.get("y4")
            y5 = request.form.get("y5")
            y6 = request.form.get("y6")
            staff = request.form.get("staff")
            
            db = get_db()
            db.execute("""
                UPDATE flagraising
                SET y1=?, y2=?, y3=?, y4=?, y5=?, y6=?, staff=?
            """, (y1, y2, y3, y4, y5, y6, staff))
            db.commit()

        return render_template("success.html", admin=current_user.admin)
    else:
        return "Unauthorized user"

@app.route("/delete")
@login_required
def delete():
    if current_user.admin == 1:
        return render_template("delete.html", admin=current_user.admin)
    else:
        return "Unauthorized user"

@app.route("/delete2", methods=["POST"])
@login_required
def delete2():
    group = request.form.get("group")
    connection = sqlite3.connect("sqlite_db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM {}".format(group))
    details = cursor.fetchall()
    connection.close()
    if current_user.admin == 1:
        return render_template("delete2.html", admin=current_user.admin, group=group, details = details)
    else:
        return "Unauthorized user"

@app.route("/deletion", methods=["POST"])
@login_required
def deletion():
    todelete = request.form.get("todelete")
    group = request.form.get("group")
    if todelete is not None:
        connection = sqlite3.connect("sqlite_db")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM {} WHERE id={}".format(group, todelete))
        connection.commit()
        connection.close()
        return render_template("success_delete.html", admin=current_user.admin)
    else:
        return render_template("failure_delete.html", admin=current_user.admin)

 
@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    temp = year + "Y"
    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        users_email = userinfo_response.json()["email"]
        if users_email[-7:] == "@dhs.sg":
            users_classid = userinfo_response.json()["given_name"]
            if users_classid[:3] == temp or users_classid[:5].lower() == "staff":
                unique_id = userinfo_response.json()["sub"]
                picture = userinfo_response.json()["picture"]
                users_name = userinfo_response.json()["family_name"]
            else:
                return "You are no longer from DHS!"
        else:
            return "You are not from DHS!"
    else:
        return "User email not available or not verified by Google.", 400
    users_email = userinfo_response.json()["email"]
    # Doesn't exist? Add to database
    if not User.get(unique_id):
        if users_classid[:5].lower() == "staff" or users_email in PERMS:
            User.create(unique_id, users_classid, users_name, users_email, picture, 1)
        else:
            User.create(unique_id, users_classid, users_name, users_email, picture, 0)

    user = User.get(unique_id)

    # Begin user session by logging the user in
    login_user(user)
    
    
    #for debugging
    userinfo_response = requests.get(uri, headers=headers, data=body)
    users_email = userinfo_response.json()["email"]
    print("Success!", users_email, '1')
    
    # Send user back to homepage
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    
   # print(current_user)
    if current_user.is_authenticated:
        logout_user()
        print("Logout")
    userinfo_endpoint = requests.get(GOOGLE_DISCOVERY_URL).json()["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    users_email = userinfo_response.json()["email"]
    print("Logout!", users_email, '1')
    print(current_user)
    
    
    return redirect(url_for("index"))

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route('/cdn')
def bootstrap():
    return render_template('testbootstrap.html')

#normal flask cmd run

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    #app.debug = False
    #for normal local testing use this run
    app.run(ssl_context="adhoc",host='127.0.0.1', port=port, debug=True)
    #for deployment to heroku app use this
    #app.run(host='0.0.0.0', port=port, debug=True)
    