import requests
import time

r0 = requests.post(
    "http://127.0.0.1:5000/",
    data={
        "type": "insert",
        "user": "benjamin",
        "password": "password",
        "journal": "journal",
        "data": "text",
        "identifier": "2021.11.30",
        "content": "text"})
time.sleep(3)
r2 = requests.post(
    "http://127.0.0.1:5000/",
    data={
        "type": "query",
        "user": "benjamin",
        "password": "password",
        "journal": "journal",
        "data": "text",
        "identifier": "2021.11.30"})
print(r2.text)
