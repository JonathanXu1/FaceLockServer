import boto3
from keys import AMAZON_KEYS_SEED

s3 = boto3.resource('s3', aws_access_key_id=AMAZON_KEYS_SEED[0], aws_secret_access_key=AMAZON_KEYS_SEED[1])

# Get list of objects for indexing
images = [('image01.jpg','Jonathan'),
          ('image02.jpg','Jonathan'),
          ('image03.jpg','Jonathan'),
          ('image04.jpg','Tristan'),
          ('image05.jpg','Tristan'),
          ('image06.jpg','Tristan')
          ]

# Iterate through list to upload objects to S3
for image in images:
    file = open("training/" + image[0],'rb')
    object = s3.Object('pennappsxviii','index/'+ image[0])
ret = object.put(Body=file, Metadata={'FullName':image[1]})