import json
import logging
import os
import time
import uuid
import boto3
import decimalencoder


class App():
    def __init__(self):
        """
        [summary]
        Class constructor: Assignmnet of DYNAMODB resource dynamically
        based on local/cloud execution 
        """
        if os.getenv('STAGE') == 'local':
            self.dynamodb = boto3.resource('dynamodb',
                                           endpoint_url='http://dynamodb:8000')
        else:
            self.dynamodb = boto3.resource('dynamodb')

        self.table = self.dynamodb.Table(os.getenv('DYNAMODB_TABLE'))

    def create(self, event, context):
        """[summary]
        Creates entry in DB table based on text passed in body
        Args:
            event ([json]): [AWS API Gateway event form]
            context ([None]): [None]

        Raises:
            Exception: [Trigger when "text" parameter not in body]

        Returns:
            [json]: [Response]
        """
        print('>> You have accessed the __create__ endpoint!')
        data = json.loads(event['body'])
        if 'text' not in data:
            logging.error("Validation Failed")
            raise Exception("Couldn't create the todo item.")
  
        timestamp = str(time.time())
        item = {
            'id': str(uuid.uuid1()),
            'text': data['text'],
            'checked': False,
            'createdAt': timestamp,
            'updatedAt': timestamp,
        }
        # write the todo to the database
        self.table.put_item(Item=item)
        # create a response
        response = {
            "statusCode": 200,
            "body": json.dumps(item)
        }
        return response
  
    def delete(self, event, context):
        """[summary]
        Deletes and existing entry in DB table
        based on the id passed in path parameter

        Args:
            event ([json]): [AWS API Gateway event form]
            context ([None]): [None]

        Returns:
            [json]: [Response]
        """
        print('>> You have accessed the __delete__ endpoint!')
        # delete the todo from the database
        self.table.delete_item(
            Key={
                'id': event['pathParameters']['id']
            }
        )
        deleted = f"Deleted ID: {event['pathParameters']['id']}"
        # create a response
        response = {
            "statusCode": 200,
            "body": json.dumps(deleted)
        }
        return response
        
    def get(self, event, context):
        """[summary]
        Gets and existing entry in DB table
        based on the id passed in path parameter

        Args:
            event ([json]): [AWS API Gateway event form]
            context ([None]): [None]

        Returns:
            [json]: [Response]
        """
        print('>> You have accessed the __get__ endpoint!')
        # fetch todo from the database
        result = self.table.get_item(
            Key={
                'id': event['pathParameters']['id']
            }
        )
        # create a response
        response = {
            "statusCode": 200,
            "body": json.dumps(result['Item'],
                               cls=decimalencoder.DecimalEncoder)
        }
        return response
    
    def show(self, event, context):
        """[summary]
        Lists all existing entries in DB table

        Args:
            event ([json]): [AWS API Gateway event form]
            context ([None]): [None]

        Returns:
            [json]: [Response]
        """
        print('>> You have accessed the __show__ endpoint!')
        result = self.table.scan()
        response = {
            "statusCode": 200,
            "body": json.dumps(result['Items'],
                               cls=decimalencoder.DecimalEncoder)
        }
        return response
        
    def translate(self, event, context):
        """
        [summary]
        Endpoint that translates any provided entry in DB table
        to the language of your choice

        Args:
            event ([json]): [ID to get the DB entry and target language]
            context ([None]): [None]

        Raises:
            Exception: [Any typing error during transaction to translate]

        Returns:
            [json]: [Response]
        """
        print('>> You have accessed the __translate__ endpoint!')
        # fetch todo from the database
        result = self.table.get_item(
            Key={
                'id': event['pathParameters']['id'],
            }
        )
        try:
            item = result['Item']
            # comprehend origin language
            comprehend = boto3.client(service_name='comprehend',
                                      region_name='us-east-1')
            related = comprehend.detect_dominant_language(Text=item['text'])
            # translate result text
            translate = boto3.client(service_name='translate',
                                     region_name='us-east-1',
                                     use_ssl=True)
            translation = translate.translate_text(
                Text=item['text'],
                SourceLanguageCode=related['Languages'][0]['LanguageCode'],
                TargetLanguageCode=event['pathParameters']['lang'])
            item['text'] = translation['TranslatedText']
            # create a response
            response = {
                "statusCode": 200,
                "body": json.dumps(item,
                                   cls=decimalencoder.DecimalEncoder)
            }
            return response
        except Exception as e:
            logging.error(str(e))
            raise Exception("[ErrorMessage]: " + str(e))
    
    def update(self, event, context):
        """
        [summary]

        Args:
            event ([json]): [AWS API Gateway event form]
            context ([None]): [None]

        Raises:
            Exception: [Triggered when text or checked not supplied]

        Returns:
            [json]: [Response]
        """
        print('>> You have accessed the __update__ endpoint!')
        data = json.loads(event['body'])
        if 'text' not in data or 'checked' not in data:
            logging.error("Validation Failed")
            raise Exception("Couldn't update the todo item.")
        timestamp = int(time.time() * 1000)
        # update the todo in the database
        result = self.table.update_item(
            Key={
                'id': event['pathParameters']['id']
            },
            ExpressionAttributeNames={'#todo_text': 'text'},
            ExpressionAttributeValues={':text': data['text'],
                                       ':checked': data['checked'],
                                       ':updatedAt': timestamp},
            UpdateExpression='SET #todo_text = :text, '
                             'checked = :checked, '
                             'updatedAt = :updatedAt',
            ReturnValues='ALL_NEW',
        )
        # create a response
        response = {
            "statusCode": 200,
            "body": json.dumps(result['Attributes'],
                               cls=decimalencoder.DecimalEncoder)
        }
        return response
