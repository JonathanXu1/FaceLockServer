# Import flask and other such stuff
from flask import Flask, request, jsonify

import requests

app = Flask(__name__)

@app.route('/uploadImage', methods=['POST'])
def yeet():
    data = request.files
    print(data)
    return jsonify({ 'message': 'success' })


@app.route('/googleactions', methods=['POST'])
def theGoog():
    data = request.args.to_dict()
    intentName = data['queryResult']['intent']['name']


if __name__ == '__main__':
    app.run(port=8080, debug=True)
