import boto3


s3 = boto3.resource('s3', aws_access_key_id='AKIAI3RFZQRXEA5HD5KA', aws_secret_access_key='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')

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