import time
import uuid
import boto3
import unittest
from pprint import pprint
from py_event_mocks import create_event
from botocore.exceptions import ClientError
from moto import mock_dynamodb2  # since we're going to mock DynamoDB service

from todolist import App


@mock_dynamodb2
class TodoListTest(unittest.TestCase):
    def setUp(self):
        """
        [summary]
        Prepare instance of app with mocked DynamoDB Table and create table itself
        """
        # Responses will be saved as attributes of the class
        self.response = None
        self.dynamodb = None
        self.table = None

        # Instance of DynamoDB instance
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        # Table creation for testing purposes:
        from ToDoCreateTable import create_todo_table
        self.table = create_todo_table(self.dynamodb)   
        print('Attributes setup')

    def tearDown(self):
        self.dynamodb = None
        self.table.delete()
        print('Attributes teared down')

    def test_table_exists(self):
        """
        [summary]
        Assert main unitary parameters of table
        """
        # Assert if table exists
        self.assertTrue(self.table)
        # Assert table name is correct
        self.assertIn('todoTable', self.table.name)
    
    def test_create(self):
        event = create_event("aws:api-gateway-event")
        event['body'] = '{"text":"Testing class with random message"}'
        self.response = App.create(self=self, event=event, context=None)
        self.assertEqual(self.response['statusCode'], 200)
        event['body'] = '{"this will fail": "Testing class with random message"}'
        with self.assertRaises(Exception):
            self.response = App.create(self=self, event=event, context=None)


    def test_delete(self):
        self.test_create()
        id_ = self.response['body'][8:44]
        event = create_event("aws:api-gateway-event")
        event['pathParameters'] = {'id': id_}
        response = App.delete(self=self, event=event, context=None)
        self.assertEqual(response['statusCode'], 200)

    def test_get(self):
        self.test_create()
        id_ = self.response['body'][8:44]
        event = create_event("aws:api-gateway-event")
        event['pathParameters'] = {'id': id_}
        response = App.get(self=self, event=event, context=None)
        self.assertEqual(response['statusCode'], 200)

    def test_show(self):
        self.test_create()
        response = App.show(self=self, event=None, context=None)
        self.assertEqual(response['statusCode'], 200)

    def test_update(self):
        self.test_create()
        id_ = self.response['body'][8:44]
        event = create_event("aws:api-gateway-event")
        event['pathParameters'] = {'id': id_}
        event['body'] = '{"text":"Changing message", "checked":"True"}'
        response = App.update(self=self, event=event, context=None)
        self.assertEqual(response['statusCode'], 200)

        event['body'] = '{"text":"Changing message", "this will fail":"True"}'
        with self.assertRaises(Exception):
            self.response = App.update(self=self, event=event, context=None)
        event['body'] = '{"this will fail":"Changing message", "checked":"True"}'
        with self.assertRaises(Exception):
            self.response = App.update(self=self, event=event, context=None)
        event['body'] = '{"this will fail":"Changing message", "this will fail":"True"}'
        with self.assertRaises(Exception):
            self.response = App.update(self=self, event=event, context=None)

if __name__ == '__main__':
    unittest.main()