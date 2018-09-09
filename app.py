# Import flask and other such stuff
import json
import time
import datetime
from flask import Flask, request, jsonify
import boto3
import io
from PIL import Image
import numpy
from keys import AMAZON_KEYS_REC
from keys import TWILIO_KEYS
from pprint import pprint
from pymongo import MongoClient, DESCENDING
from flask_socketio import SocketIO, send
from twilio.rest import Client

#Output text
output = ""

# Setup up aws
rekognition = boto3.client('rekognition', region_name='us-east-1', aws_access_key_id=AMAZON_KEYS_REC[0], aws_secret_access_key=AMAZON_KEYS_REC[1])
dynamodb = boto3.client('dynamodb', region_name='us-east-1', aws_access_key_id=AMAZON_KEYS_REC[0], aws_secret_access_key=AMAZON_KEYS_REC[1])
s3 = boto3.resource('s3', aws_access_key_id=AMAZON_KEYS_REC[0], aws_secret_access_key=AMAZON_KEYS_REC[1])

# Set up MongoDB
client = MongoClient('mongodb://localhost:27017')
walkups = client.adoorable.walkups

# Set up flask
app = Flask(__name__)
socketio = SocketIO(app)

# Set up Twilio
account_sid = TWILIO_KEYS[0]
auth_token = TWILIO_KEYS[1]
client = Client(account_sid, auth_token)

def poopityscoop(words):
    client.messages.create(
        body=words,
        from_='+16474905328',
        to='+16476384839'
    )

@app.route('/uploadImage', methods=['POST'])
def yeet():
    now = datetime.datetime.now()
    data = request.files['image']
    print(type(data))

    # Aws facial recognition
    image = Image.open(data)
    stream = io.BytesIO()
    image.save(stream, format="JPEG")
    image_binary = stream.getvalue()

    response = rekognition.detect_faces(
        Image={'Bytes': image_binary}
    )

    all_faces = response['FaceDetails']

    # Initialize list object
    boxes = []

    # Get image diameters

    image_width = image.size[0]
    image_height = image.size[1]

    try: #This try/catch is important for debug
        # Crop face from image
        for face in all_faces:
            box = face['BoundingBox']
            x1 = int(box['Left'] * image_width) * 0.9
            y1 = int(box['Top'] * image_height) * 0.9
            x2 = int(box['Left'] * image_width + box['Width'] * image_width) * 1.10
            y2 = int(box['Top'] * image_height + box['Height'] * image_height) * 1.10
            image_crop = image.crop((x1, y1, x2, y2))

            stream = io.BytesIO()
            image_crop.save(stream, format="JPEG")
            image_crop_binary = stream.getvalue()

            pil_image = image_crop.convert('RGB')
            cropped = numpy.array(pil_image)

            # Submit individually cropped image to Amazon Rekognition
            response = rekognition.search_faces_by_image(
                CollectionId='family_collection',
                Image={'Bytes': image_crop_binary}
            )
            print(response)
            if len(response['FaceMatches']) > 0:
                # Return results
                print('Coordinates ', box)
                for match in response['FaceMatches']:

                    face = dynamodb.get_item(
                        TableName='PennappsXVIII',
                        Key={'RekognitionID': {'S': match['Face']['FaceId']}}
                    )

                    if 'Item' in face:
                        person = face['Item']['FullName']['S']
                    else:
                        person = 'no match found'

                    print(person)
                    walkups.insert_one({ 'face': match['Face']['FaceId'], 'time': now, 'name': person })
                    if person == "no match found":
                        poopityscoop("An unknown stranger has appeared at your house")
                    else:
                        poopityscoop(person + " is at ur front door yo")
                    return jsonify(faceID=match['Face']['FaceId'], confidence=match['Face']['Confidence'], faceName=person)

            else:
                # Upload the new face as an unknown entity
                print("Unknown person")
                walkups.insert_one({ 'time': now, 'name': 'An unknown person'})
                poopityscoop("An unknown stranger has appeared at your house")
                return jsonify(faceID='unknown', confidence=0, faceName='unknown')
    except Exception as e:
        print(e)
        return jsonify(faceID='unknown', confidence=0, faceName='unknown')


@app.route('/googleactions', methods=['POST'])
def theGoog():
    data = request.get_json()
    intentName = data['queryResult']['intent']['displayName']
    if intentName == 'Lock the door':
        send({'lock':true})
        return json.dumps({'fulfillmentText': 'I\'ve locked your door.' })
    elif intentName == 'Unlock the door':
        send({'unlock':true})
        return json.dumps({ 'fulfillmentText': 'You can totally believe I just unlocked your door' })
    elif intentName == 'Who is there':
        lastPerson = walkups.find_one(sort=[('time', DESCENDING)])
        if lastPerson:
            return json.dumps({ 'fulfillmentText': f'{lastPerson["name"]} was at your door at {lastPerson["time"]}' })
        else:
            return json.dumps({ 'fulfillmentText': 'No one has ever been to your door' })
    elif intentName == 'Read Lock State':
        state = None
        def ack(value):
            state = value
        send({'getState': true}, callback=ack)
        while state == None:
            time.sleep(10)
        if state:
            return json.dumps({ 'fulfillmentText': 'Your door is locked.' })
        else:
            return json.dumps({ 'fulfillmentText': 'Your door is unlocked.' })
    elif intentName == 'Take picture':
        return json.dumps({
            'fulfillmentMessages': [
                {
                    'card': {
                        'imageUri': 'https://media2.giphy.com/media/g9582DNuQppxC/giphy.gif'
                    }
                }
            ]
        })
    else:
        return json.dumps({ 'fulfillmentText': 'I don\'t understand.' })


if __name__ == '__main__':
    socketio.run(port=8080, debug=True)
