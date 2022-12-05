import xlsxwriter
import logging
import datetime
import os
from .config import BaseConfig
import boto3
from botocore.exceptions import NoCredentialsError
from faker import Faker
import uuid
from dotenv import load_dotenv
load_dotenv()


def createFakeEntities(entityNumber):
    fake = Faker()
    users = []
    for i in range(0, entityNumber):
        userName= f'{fake.name()}-{str(uuid.uuid4())}'
        userEmail = f'{str(uuid.uuid4())}@gmail.com'
        user = dict()
        user['name'] = userName
        user['email'] = userEmail
        user['gender'] = 'male'
        user['status'] = 'active'
        user['posts'] = []
        user['comments'] = []
        user['todos'] = []
        for j in range(0,entityNumber):
            post = dict()
            comment = dict()
            todo = dict()
            post['title'] = fake.text()
            post['body'] = fake.text()
            comment['body'] = fake.text()
            comment['name'] = userName
            comment['email'] = userEmail
            todo['title'] = fake.text() 
            todo['due_on'] = str(datetime.datetime.now())
            todo['status'] = 'completed'
            user['posts'].append(post)
            user['todos'].append(todo)
            user['comments'].append(comment)
        users.append(user)
    return users

