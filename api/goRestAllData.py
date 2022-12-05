import asyncio
import requests
import logging
import math
from .config import EntityConfig, BaseConfig
from dotenv import load_dotenv
logging.basicConfig(level=logging.INFO)
load_dotenv()


async def getPagesByEntity(entity):
    try:
        temp = requests.get(
            f'{BaseConfig.GOREST_API_ENDPOINT}/{entity}?page=1')
        temp = temp.json()
        logging.info(
            f'getPagesByEntity -- Found {math.ceil(temp[0]["id"]/100)} pages for {entity}')
        return math.ceil(temp[0]["id"]/100)
    except Exception as e:
        logging.error(e)


async def getPagesNumbers():
    try:
        allPages = {}
        tasks = []
        tasks.append(asyncio.ensure_future(
            getPagesByEntity(f'{EntityConfig.USERS}')))
        tasks.append(asyncio.ensure_future(
            getPagesByEntity(f'{EntityConfig.POSTS}')))
        tasks.append(asyncio.ensure_future(
            getPagesByEntity(f'{EntityConfig.COMMENTS}')))
        tasks.append(asyncio.ensure_future(
            getPagesByEntity(f'{EntityConfig.TODOS}')))
        asyncioResponse = await asyncio.gather(*tasks)
        allPages[f'{EntityConfig.USERS}'] = asyncioResponse[0]
        allPages[f'{EntityConfig.POSTS}'] = asyncioResponse[1]
        allPages[f'{EntityConfig.COMMENTS}'] = asyncioResponse[2]
        allPages[f'{EntityConfig.TODOS}'] = asyncioResponse[3]
        return allPages
    except Exception as e:
        logging.error(e)


async def getEntitiesByType(entity, pages):
    try:
        allEntities = []
        tasks = []
        for number in range(1, pages+1):
            if (entity == f'{EntityConfig.USERS}'):
                tasks.append(asyncio.ensure_future(getUsersByPage(number)))
            if (entity == f'{EntityConfig.POSTS}'):
                tasks.append(asyncio.ensure_future(getPostsByPage(number)))
            if (entity == f'{EntityConfig.COMMENTS}'):
                tasks.append(asyncio.ensure_future(getCommentsByPage(number)))
            if (entity == f'{EntityConfig.TODOS}'):
                tasks.append(asyncio.ensure_future(getTodosByPage(number)))
        asyncioResponse = await asyncio.gather(*tasks)
        for resp in asyncioResponse:
            for entityObj in resp:
                allEntities.append(entityObj)
        logging.info(f'getEntitiesByType -- Found {len(allEntities)} {entity}')
        return allEntities
    except Exception as e:
        logging.error(e)


async def getAllEntitiesData(pagesNumbers):
    try:
        allData = {}
        tasks = []
        tasks.append(asyncio.ensure_future(getEntitiesByType(
            f'{EntityConfig.USERS}', pagesNumbers[f'{EntityConfig.USERS}'])))
        tasks.append(asyncio.ensure_future(getEntitiesByType(
            f'{EntityConfig.POSTS}', pagesNumbers[f'{EntityConfig.POSTS}'])))
        tasks.append(asyncio.ensure_future(getEntitiesByType(
            f'{EntityConfig.COMMENTS}', pagesNumbers[f'{EntityConfig.COMMENTS}'])))
        tasks.append(asyncio.ensure_future(getEntitiesByType(
            f'{EntityConfig.TODOS}', pagesNumbers[f'{EntityConfig.TODOS}'])))
        asyncioResponse = await asyncio.gather(*tasks)
        allData[f'{EntityConfig.USERS}'] = asyncioResponse[0]
        allData[f'{EntityConfig.POSTS}'] = asyncioResponse[1]
        allData[f'{EntityConfig.COMMENTS}'] = asyncioResponse[2]
        allData[f'{EntityConfig.TODOS}'] = asyncioResponse[3]
        return allData
    except Exception as e:
        logging.error(e)


async def getUsersByPage(pageNumber):
    try:
        all_users = []
        temp = requests.get(
            f'{BaseConfig.GOREST_API_ENDPOINT}/{EntityConfig.USERS}?page={pageNumber}&per_page=100')
        temp = temp.json()
        for j in temp:
            all_users.append(dict(
                id=j["id"], name=j["name"], email=j["email"], gender=j["gender"], status=j["status"]))
        return all_users
    except Exception as e:
        logging.error(e)


async def getPostsByPage(pageNumber):
    try:
        all_posts = []
        temp = requests.get(
            f'{BaseConfig.GOREST_API_ENDPOINT}/{EntityConfig.POSTS}?page={pageNumber}&per_page=100')
        temp = temp.json()
        for j in temp:
            all_posts.append(dict(
                id=j["id"], user_id=j["user_id"], body=j["body"], title=j["title"]))
        return all_posts
    except Exception as e:
        logging.error(e)


async def getCommentsByPage(pageNumber):
    try:
        all_comments = []
        temp = requests.get(
            f'{BaseConfig.GOREST_API_ENDPOINT}/{EntityConfig.COMMENTS}?page={pageNumber}&per_page=100')
        temp = temp.json()
        for j in temp:
            all_comments.append(dict(
                id=j["id"], post_id=j["post_id"], name=j["name"], email=j["email"], body=j["body"]))
        return all_comments
    except Exception as e:
        logging.error(e)


async def getTodosByPage(pageNumber):
    try:
        all_todos = []
        temp = requests.get(
            f'{BaseConfig.GOREST_API_ENDPOINT}/{EntityConfig.TODOS}?page={pageNumber}&per_page=100')
        temp = temp.json()
        for j in temp:
            all_todos.append(dict(
                id=j["id"], user_id=j["user_id"], title=j["title"], due_on=j["due_on"], status=j["status"]))
        return all_todos
    except Exception as e:
        logging.error(e)
