from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask
from flask import session
from flask_session import Session
from flask import Response
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
from flask_mail import Mail, Message
from datetime import timedelta
from database_backend import *


cred = {}
with open("credentials.txt", "r") as credentials:
    reader = csv.reader(credentials, delimiter=",")
    for i in reader:
        cred[i[0]] = i[1]

MAIL_SERVER = cred["MAIL_SERVER"]
MAIL_PORT = cred["MAIL_PORT"]
MAIL_USERNAME = cred["MAIL_USERNAME"]
MAIL_PASSWORD = cred["MAIL_PASSWORD"]

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)
app.secret_key = secrets.token_hex(16)
app.config['PREFERRED_URL_SCHEME'] = 'https'
app.config["SESSION_PERMANENT"] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


@app.route("/", methods=["POST"])
def parse_request():
    try:
        if request.method == "POST":
            data = request.form
            if not connect(data["user"], data["password"]):
                return "401"
            if data["type"] == "query":
                resp = database_query(
                    data["user"],
                    data["password"],
                    get_db_name(data["user"], data["password"]),
                    data["data"],
                    data["identifier"])
                if data["data"] == "image":
                    return {"type": data["type"], "data": data["data"],
                            "content": resp, "identifier": data["content"]}
                else:
                    return {"type": data["type"], "data": data["data"],
                            "content": resp, "identifier": data["identifier"]}
            elif data["type"] == "query_all":
                resp = database_query_all(
                    data["user"],
                    data["password"],
                    get_db_name(data["user"], data["password"]),
                    data["data"],
                    data["identifier"])
                return {"type": data["type"], "data": data["data"],
                        "content": resp, "identifier": data["identifier"]}
            elif data["type"] == "insert":
                resp = database_insert(
                    data["user"],
                    data["password"],
                    get_db_name(data["user"], data["password"]),
                    data["data"],
                    data["identifier"],
                    data["content"])
                return {"type": data["type"], "data": data["data"],
                        "content": resp, "identifier": data["identifier"]}
    except BaseException:
        return "500"


@app.route("/token", methods=['GET', 'POST'])
def token():
    if request.method == 'POST' and "register_2" in request.form:
        if request.form["token"] == session["token"] and create_user(
                session["user"], session["email"], session["password"]):
            msg = Message(
                'OpenJournal registration successfull',
                sender='business@gallois.cc',
                recipients=[
                    session['email']])
            msg.body = "Hello, your successfully register to OpenJournal Cloud with credentials " + \
                session["user"] + " and password " + session["password"]
            mail.send(msg)
            msg = Message(
                'OpenJournal new registration',
                sender='benjamin@gallois.cc',
                recipients=[
                    "business@gallois.cc"])
            msg.body = "New user " + session["user"]
            mail.send(msg)
            return render_template('account.html', error="Success")
        else:
            return render_template('account.html', error="Echec")
    return render_template("account.html", email=session["email"])


@app.route("/register", methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST' and "register_1" in request.form:
        if not check_user(request.form['username']):
            error = "User already taken !"
            return render_template('register.html', error=error)
        else:
            session["token"] = secrets.token_hex(32)
            session["user"] = request.form['username']
            session["password"] = request.form['password']
            session["email"] = request.form['email']
            msg = Message(
                'OpenJournal confirmation',
                sender='business@gallois.cc',
                recipients=[
                    request.form['email']])
            msg.body = "Hello, the token is " + session["token"]
            mail.send(msg)
            error = "Token was sent"
            return redirect(url_for('token'))
    return render_template('register.html', error=error)


if __name__ == "__main__":
    app.run()
