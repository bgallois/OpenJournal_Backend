from flask import Flask
from flask import request
from flask import Response

import mysql.connector

app = Flask(__name__)


@app.route("/", methods=["POST"])
def parse_request():
    if request.method == "POST":
        data = request.form
        if data["type"] == "query":
            resp = database_query(
                data["user"],
                data["password"],
                data["journal"],
                data["data"],
                data["identifier"])
        elif data["type"] == "insert":
            resp = database_insert(
                data["user"],
                data["password"],
                data["journal"],
                data["data"],
                data["identifier"],
                data["content"])
        elif data["type"] == "delete":
            resp = database_delete(
                data["user"],
                data["password"],
                data["journal"],
                data["data"],
                data["identifier"])
        return {"data": resp}


def database_query(user, password, journal, data, identifier):
    '''
    data: {text, image}
    identifier! {date, filename}
    '''
    cnx = mysql.connector.connect(
        user=user,
        password=password,
        host='127.0.0.1',
        database=journal)
    if data == "text":
        query = "SELECT entry FROM journalPage WHERE date = %s"
    elif data == "image":
        query = "SELECT imagedata FROM asset WHERE filename = %s"
    cursor = cnx.cursor()
    cursor.execute(query, (identifier,))
    response = next(cursor)
    cursor.close()
    cnx.close()
    print(response)
    return response


def database_delete(user, password, journal, data, identifier):
    '''
    data: {text, image}
    identifier! {date, filename}
    '''
    cnx = mysql.connector.connect(
        user=user,
        password=password,
        host='127.0.0.1',
        database=journal)
    if data == "text":
        query = "DELETE FROM journalPage WHERE date = %s"
    elif data == "image":
        query = "DELETE FROM asset WHERE filename = %s"
    cursor = cnx.cursor()
    cursor.execute(query, (identifier,))
    cnx.commit()
    cursor.close()
    cnx.close()
    return ""


def database_insert(user, password, journal, data, identifier, content):
    '''
    data: {text, image}
    identifier! {date, filename}
    '''
    cnx = mysql.connector.connect(
        user=user,
        password=password,
        host='127.0.0.1',
        database=journal)
    cursor = cnx.cursor()
    if data == "text":
        query = "INSERT INTO journalPage (date, entry) VALUES (%s, %s) ON DUPLICATE KEY UPDATE entry=%s"
        cursor.execute(query, (identifier, content, content))
    elif data == "image":
        query = "INSERT INTO asset (filename, imagedata) VALUES (%s, %s)"
        cursor.execute(query, (identifier, content))
    cnx.commit()
    cursor.close()
    cnx.close()
    return ""
