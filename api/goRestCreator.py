
import asyncio
import requests
import logging
import os
from .config import BaseConfig, HttpStatusCode, EntityConfig
import boto3
from botocore.exceptions import NoCredentialsError
import backoff
import time
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.INFO)


def fatal_code(e):
    return e.response.status_code != 429


@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_tries=30,
    max_time=300,
    giveup=fatal_code
)
async def createGoRestEntities(entities):
    try:
        tasks = []
        for entity in entities:
            tasks.append(asyncio.ensure_future(createUserAndRealtions(entity)))
        asyncioResponse = await asyncio.gather(*tasks)
        summary = calculateSummary(entities)
        createdData = buildEntityInformation(asyncioResponse, summary)
        return createdData
    except Exception as e:
        error = f'createGoRestEntities -- Failed to create entities, Error:{e}'
        logging.error(error)
        raise Exception(error)


def calculateSummary(entities):
    try:
        summary = dict()
        summary['Total Users'] = len(entities)
        summary['Total Comments'] = 0
        summary['Total Posts'] = 0
        summary['Total Todos'] = 0
        for entity in entities:
            summary['Total Comments'] = summary['Total Comments'] + \
                len(entity['comments'])
            summary['Total Posts'] = summary['Total Posts'] + \
                len(entity['posts'])
            summary['Total Todos'] = summary['Total Todos'] + \
                len(entity['todos'])
        return summary

    except Exception as e:
        error = f'calculateSummary -- Failed to calcualte summary, Error:{e}'
        logging.error(error)
        raise Exception(error)


def buildEntityInformation(data, summary):
    response = dict()
    response['data'] = data
    response['Summary'] = summary
    return response


async def createUserAndRealtions(entity):
    try:
        userObj = createUser(
            entity['name'], entity['email'], entity['gender'], entity['status'])
        tasks = []
        i = 0
        for postObj in entity['posts']:
            tasks.append(asyncio.ensure_future(creatPostAndRealtions(
                userObj["userID"], entity['name'], entity['email'], postObj, entity['comments'][i])))
            i = i+1
        for todoObj in entity['todos']:
            tasks.append(asyncio.ensure_future(createTodoByUser(
                userObj["userID"], todoObj['title'], todoObj['due_on'], todoObj['status'])))

        asyncioResponse = await asyncio.gather(*tasks)
        userObjGlobal = dict()
        userObjGlobal['userID'] = userObj["userID"]
        userObjGlobal['userEmail'] = userObj["userEmail"]
        userObjGlobal['userName'] = userObj["userName"]
        userObjGlobal['User Online Summary'] = dict()
        userObjGlobal['User Online Summary']["Posts"] = dict()
        userObjGlobal['User Online Summary']["Posts"]['Total Posts'] = len(
            entity['posts'])
        userObjGlobal['User Online Summary']["Posts"]['Posts Info'] = []
        userObjGlobal['User Online Summary']["Comments"] = dict()
        userObjGlobal['User Online Summary']["Comments"]['Total Comments'] = len(
            entity['comments'])
        userObjGlobal['User Online Summary']["Comments"]['Comments Info'] = []
        userObjGlobal['User Online Summary']["Todos"] = dict()
        userObjGlobal['User Online Summary']["Todos"]['Total Todos'] = len(
            entity['todos'])
        userObjGlobal['User Online Summary']["Todos"]['Todos Info'] = []

        for singleRes in asyncioResponse:
            if ('postObj' in singleRes and 'commentObj' in singleRes):
                userObjGlobal['User Online Summary']["Posts"]['Posts Info'].append(
                    singleRes['postObj'])
                userObjGlobal['User Online Summary']["Comments"]['Comments Info'].append(
                    singleRes['commentObj'])
                continue
            else:
                userObjGlobal['User Online Summary']["Todos"]['Todos Info'].append(
                    singleRes['todoObj'])
        return userObjGlobal
    except Exception as e:
        error = f'createUserAndRealtions -- Failed to create user: {entity["name"]}, Error:{e}'
        logging.error(error)
        raise Exception(error)


async def creatPostAndRealtions(userID, userName, userEmail, postObj, commentObj):
    try:
        createdPostObj = createPostByUser(
            userID, postObj['title'], postObj['body'])
        createdCommentObj = createCommentByUser(
            createdPostObj['id'], userName, userEmail, commentObj['body'])
        postRealtionObj = dict()
        postRealtionObj['postObj'] = createdPostObj
        postRealtionObj['commentObj'] = createdCommentObj
        return postRealtionObj
    except Exception as e:
        error = f'creatPostAndRealtions -- Failed to create post: {userName}, Error:{e}'
        logging.error(error)
        raise Exception(error)


def createUser(name, email, gender, status):
    statssession = requests.Session()
    payload = {
        "access-token": os.getenv('GOREST_AUTH_KEY'),
        "name": name,
        "email": email,
        "gender": gender,
        "status": status
    }
    for _ in range(0, 5):
        try:
            r = statssession.post(
                f'{BaseConfig.GOREST_API_ENDPOINT}/{EntityConfig.USERS}', data=payload, timeout=10)
            if r.status_code == HttpStatusCode.CREATED:
                logging.info(f'Sucsseded to create new user:{name}')
                response = r.json()
                userObj = dict()
                userObj["userID"] = response['id']
                userObj["userEmail"] = email
                userObj["userName"] = name
                return userObj
            if r.status_code >= HttpStatusCode.TOO_MANY_REQUESTS:
                time.sleep(5)
                continue
            elif r.status_code >= HttpStatusCode.BAD_REQUEST:
                raise Exception(r.text)
        except Exception as e:
            error = f'createUser -- Failed to create user: {name}, Error:{e}'
            logging.error(error)
            raise Exception(error)


def createPostByUser(userID, title, body):
    statssession = requests.Session()
    payload = {
        "access-token": os.getenv('GOREST_AUTH_KEY'),
        "user_id": userID,
        "title": title,
        "body": body
    }
    for _ in range(0, 5):
        try:
            r = statssession.post(
                f'{BaseConfig.GOREST_API_ENDPOINT}/{EntityConfig.POSTS}', data=payload, timeout=10)
            if r.status_code == HttpStatusCode.CREATED:
                logging.info(
                    f'Sucsseded to create new posts:{title} by user_id:{userID}')
                response = r.json()
                postObj = dict()
                postObj["id"] = response['id']
                postObj["body"] = response['body']
                return postObj
            if r.status_code >= HttpStatusCode.TOO_MANY_REQUESTS:
                    time.sleep(5)
                    continue
            elif r.status_code >= HttpStatusCode.BAD_REQUEST:
                raise Exception(r.text)
        except Exception as e:
            error = f'createPostByUser -- Failed to create post by userID:{userID}, Error:{e}'
            logging.error(error)
            raise Exception(error)


def createCommentByUser(postID, name, email, body):
    statssession = requests.Session()
    payload = {
        "access-token": os.getenv('GOREST_AUTH_KEY'),
        "post_id": postID,
        "name": name,
        "email": email,
        "body": body
    }
    for _ in range(0, 5):
        try:
            r = statssession.post(
                f'{BaseConfig.GOREST_API_ENDPOINT}/{EntityConfig.COMMENTS}', data=payload, timeout=10)
            if r.status_code == HttpStatusCode.CREATED:
                logging.info(
                    f'Sucsseded to create new comment:{name} by user:{name} on post:{postID}')
                response = r.json()
                commentObj = dict()
                commentObj["id"] = response['id']
                commentObj["body"] = body
                return commentObj
            if r.status_code >= HttpStatusCode.TOO_MANY_REQUESTS:
                    time.sleep(5)
                    continue
            elif r.status_code >= HttpStatusCode.BAD_REQUEST:
                raise Exception(r.text)
        except Exception as e:
            error = f'createCommentByUser -- Failed to create comment by user:{name}, Error:{e}'
            logging.error(error)
            raise Exception(error)


async def createTodoByUser(userID, title, due_on, status):
    statssession = requests.Session()
    payload = {
        "access-token": os.getenv('GOREST_AUTH_KEY'),
        "user_id": userID,
        "title": title,
        "due_on": due_on,
        "status": status
    }
    for _ in range(0, 5):
        try:
            r = statssession.post(
                f'{BaseConfig.GOREST_API_ENDPOINT}/{EntityConfig.TODOS}', data=payload, timeout=10)
            if r.status_code == HttpStatusCode.CREATED:
                logging.info(f'Sucsseded to create new todo:{title}')
                response = r.json()
                todoObj = dict()
                todoObj["id"] = response['id']
                todoObj["title"] = title
                todoObj["due_on"] = due_on
                todoObj["due_on"] = status
                return dict(todoObj=todoObj)
            if r.status_code >= HttpStatusCode.TOO_MANY_REQUESTS:
                    time.sleep(5)
                    continue
            elif r.status_code >= HttpStatusCode.BAD_REQUEST:
                raise Exception(r.text)
        except Exception as e:
            error = f'createTodoByUser -- Failed to create todo by user:{userID}, Error:{e}'
            logging.error(error)
            raise Exception(error)
