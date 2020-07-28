from decimal import Decimal
import json
import boto3

# resources
client = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('image-labels')
        
def lambda_handler(event, context):
    
    # since batch size is 1, index 0 will always work
    # load json from SQS
    image_records = json.loads(event['Records'][0]['body'])['Records']
    
    for record in image_records:
        # variables for later use
        bucket = record['s3']['bucket']['name'] 
        photo = record['s3']['object']['key']
        etag = record['s3']['object']['eTag']
    
        try:
            response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}}, MaxLabels=5) 
            # convert floats to decimals
            float_free = json.loads(json.dumps(response), parse_float=Decimal)
            # insert items to dyanmodb table
            table.put_item(Item = {
                'image': photo[7:],
                'eTag': etag,
                'Labels': float_free['Labels']
            })
        except client.exceptions.InvalidImageFormatException as e:
            # insert empty labels, invalid image format exception
            table.put_item(Item = {
                'image': photo[7:],
                'eTag': etag,
                'Labels': [],
            })