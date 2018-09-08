# Import flask and other such stuff
from flask import Flask, request

import requests

app = Flask(__name__)

@app.route('/uploadImage', methods=['GET'])
def yeet():
    data = request.args.to_dict()


@app.route('/googleactions', methods=['POST'])
def theGoog():
    data = request.args.to_dict()
    intentName = data['queryResult']['intent']['name']

