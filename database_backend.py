import mysql.connector
import hashlib
import secrets
import csv

cred = {}
with open("credentials.txt", "r") as credentials:
    reader = csv.reader(credentials, delimiter=",")
    for i in reader:
        cred[i[0]] = i[1]

USER = cred["USER"]
PASS = cred["PASS"]


def database_query(user, password, journal, data, identifier):
    '''
    data: {text, image}
    identifier! {date, filename}
    '''
    cnx = mysql.connector.connect(
        user=USER,
        password=PASS,
        host='127.0.0.1',
        database=journal)
    if data == "text":
        query = "SELECT entry FROM journalPage WHERE date = %s"
    elif data == "image":
        query = "SELECT imagedata FROM asset WHERE filename = %s"
    cursor = cnx.cursor(raw=True)
    cursor.execute(query, (identifier,))
    response = cursor.fetchone()
    cursor.close()
    cnx.close()
    if response is None:
        return ""
    else:
        if data == "image":
            response = response[0].hex()
        elif data == "text":
            response = response[0].decode()
        return response


def database_delete(user, password, journal, data, identifier):
    '''
    data: {text, image}
    identifier! {date, filename}
    '''
    cnx = mysql.connector.connect(
        user=USER,
        password=PASS,
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
        user=USER,
        password=PASS,
        host='127.0.0.1',
        database=journal)
    if data == "text":
        cursor = cnx.cursor()
        query = "INSERT INTO journalPage (date, entry) VALUES (%s, %s) ON DUPLICATE KEY UPDATE entry=%s"
        cursor.execute(query, (identifier, content, content))
    elif data == "image":
        cursor = cnx.cursor(raw=True)
        query = "INSERT INTO asset (filename, imagedata) VALUES (%s, %s)"
        cursor.execute(query, (identifier, bytes.fromhex(content)))
    cnx.commit()
    cursor.close()
    cnx.close()
    return ""


def database_activity(user, password, journal):
    '''
    data: {text, image}
    identifier! {date, filename}
    '''
    cnx = mysql.connector.connect(
        user=USER,
        password=PASS,
        host='127.0.0.1',
        database=journal)
    query = "SELECT 1"
    cursor = cnx.cursor()
    cursor.execute(query, ())
    response = next(cursor, "Wrong")
    if len(response):
        response = response[0]
    cursor.close()
    cnx.close()
    return response


def check_user(user):
    cnx = mysql.connector.connect(
        user=USER,
        password=PASS,
        host='127.0.0.1',
        database="account")
    cursor = cnx.cursor()
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (user,))
    data = cursor.fetchone()
    cursor.close()
    cnx.close()
    if data is None:
        return True
    else:
        return False


def get_db_name(user, password):
    cnx = mysql.connector.connect(
        user=USER,
        password=PASS,
        host='127.0.0.1',
        database="account")
    cursor = cnx.cursor()
    md5 = hashlib.new('md5', password.encode('utf-8'))
    query = "SELECT db_name FROM users WHERE username = %s and password = %s"
    cursor.execute(query, (user, md5.hexdigest()))
    data = cursor.fetchone()
    cursor.close()
    cnx.close()
    return data[0]


def connect(user, password):
    cnx = mysql.connector.connect(
        user=USER,
        password=PASS,
        host='127.0.0.1',
        database="account")
    md5 = hashlib.new('md5', password.encode('utf-8'))
    cursor = cnx.cursor()
    query = "SELECT * FROM users WHERE username = %s and password = %s"
    cursor.execute(query, (user, md5.hexdigest()))
    data = cursor.fetchone()
    cursor.close()
    cnx.close()
    if data is None:
        return False
    else:
        return True


def create_user(user, email, password):
    if connect(user, password):
        return False

    cnx = mysql.connector.connect(
        user=USER,
        password=PASS,
        host='127.0.0.1',
        database="account")
    md5 = hashlib.new('md5', password.encode('utf-8'))
    db_name = secrets.token_hex(16)
    cursor = cnx.cursor()
    query = "INSERT INTO users (username, password, email, db_name) VALUES (%s, %s, %s, %s)"
    try:
        cursor.execute(query, (user, md5.hexdigest(), email, db_name))
        cnx.commit()
        create_database(db_name)
        return True
    except mysql.connector.IntegrityError as err:
        return False
    finally:
        cursor.close()
        cnx.close()


def create_database(user):
    try:
        cnx = mysql.connector.connect(
            user=USER,
            password=PASS,
            host='127.0.0.1',
            database="account")
        query_0 = "CREATE DATABASE " + user
        cursor = cnx.cursor()
        cursor.execute(query_0)
        cnx1 = mysql.connector.connect(
            user=USER,
            password=PASS,
            host='127.0.0.1',
            database=user)
        query_1 = "CREATE TABLE IF NOT EXISTS asset ( filename TEXT, imagedata LONGBLOB)"
        query_2 = "CREATE TABLE IF NOT EXISTS journalPage (date TINYTEXT, entry TEXT)"
        query_3 = "ALTER TABLE journalPage ADD CONSTRAINT date_un UNIQUE (date(255))"
        cursor1 = cnx1.cursor()
        cursor1.execute(query_1)
        cursor1.execute(query_2)
        cursor1.execute(query_3)
        cnx.commit()
        return True
    except mysql.connector.IntegrityError as err:
        return False
    finally:
        cursor.close()
        cnx.close()
