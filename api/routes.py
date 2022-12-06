import asyncio
from functools import wraps
import logging
from flask import Flask, Response,request
from flask_restx import Api, Resource, fields
from threading import Thread
from .config import BaseConfig, HttpStatusCode,EntityConfig
from dotenv import load_dotenv
from .excelHandler import createAllGoRestDataInExcel, uploadExcelToS3Aws
from .goRestAllData import getAllEntitiesData, getPagesNumbers
from .entityFaker import createFakeEntities
from .goRestCreator import createUser,createGoRestEntities
import simple_cache
import json
import time
import os
import logging
import uuid
logging.basicConfig(level = logging.INFO)
load_dotenv()

def CsvContinue_processing():
    try:
        startTime = time.time()
        logging.info('Start to create Csv file with all GoRest data')
        pagesNumbers = asyncio.run(getPagesNumbers())
        allEntities = asyncio.run(getAllEntitiesData(pagesNumbers))
        createAllGoRestDataInExcel(
            allEntities[f'{EntityConfig.USERS}'], allEntities[f'{EntityConfig.POSTS}'], allEntities[f'{EntityConfig.COMMENTS}'], allEntities[f'{EntityConfig.TODOS}'])
        logging.info(f'Finish to create Csv file with all GoRest data')
        isUploaded = uploadExcelToS3Aws(
            f'/tmp/{BaseConfig.GO_REST_EXCEL_FILENAME}', BaseConfig.GO_REST_BUCKETNAME, BaseConfig.GO_REST_EXCEL_FILENAME)
        logging.info(f'Finish to upload Csv file with all GoRest data to s3')
        os.remove(f'/tmp/{BaseConfig.GO_REST_EXCEL_FILENAME}')
        if (isUploaded == False):
            raise Exception("Faild to upload file to s3")
        print(f'/api/csv -- Execution Time: {startTime-time.time()} sec')
    except Exception as e:
        error = f'Failed to create csv file with all GoRest Data,Error:{e}'
        logging.error(error)
        raise Exception(error)

def createEntitiesContinue_processing(lastRunUUID):
    try:
        for num in range(1, 11):
            print(num)
        startTime = time.time()
        logging.info('Start to create fake entities')
        entities = createFakeEntities(1)
        print(entities)
        print('done')
        dataCreated = asyncio.run(createGoRestEntities(entities))
        json_object = json.dumps(dataCreated, indent=4)
        with open(f'/tmp/{BaseConfig.STORE_NAME}-{lastRunUUID}.json', "w") as outfile:
            outfile.write(json_object)
        simple_cache.save_key(f'/tmp/{BaseConfig.STORE_NAME}', lastRunUUID, dataCreated, 99999999999999999)
        print(f'/api/create-enitities -- Execution Time: {startTime-time.time()} sec')
    except Exception as e:
        error = f'Failed to create fake entities,Error:{e}'
        logging.error(error)
        raise Exception(error)





rest_api = Api(version="1.0", title="GoRest API")

"""
    Flask-Restx routes
"""


@rest_api.route('/api/health')
class Health(Resource):
    """
       Health-Check endpoint
    """
    @rest_api.expect(validate=True)
    def get(self):
        try:
            return {"data": None, "statusCode": HttpStatusCode.OK, "message": None}, HttpStatusCode.OK
        except Exception as e:
            logging.error(f'Failed to check health check,Error:{e}')
            return {"data": None, "statusCode": HttpStatusCode.INTERNAL_ERROR, "message": None}, HttpStatusCode.INTERNAL_ERROR


@rest_api.route('/api/csv')
class CSV(Resource):
    """
       Creating CSV file with all goRest current data
    """
    @rest_api.expect(validate=True)
    def post(self):
        try:
            lastRunUUID = str(uuid.uuid4())
            response = Response(f'{lastRunUUID}')
            Thread(target=CsvContinue_processing).start()
            return response
            # return {"data": None, "statusCode": HttpStatusCode.OK, "message": None}, HttpStatusCode.OK
        except Exception as e:
            logging.error(f'Failed to create csv file with all GoRest Data,Error:{e}')
            return {"data": None, "statusCode": HttpStatusCode.INTERNAL_ERROR, "message": None},  HttpStatusCode.INTERNAL_ERROR


@rest_api.route('/api/create-entities')
class CreateEntities(Resource):
    """
       Creating ten users, each of whom will create ten posts, ten comments, and ten to-do lists via the API. 
    """
    @rest_api.expect(validate=True)
    def post(self):
        try:
            lastRunUUID = str(uuid.uuid4())
            response = Response(f'{lastRunUUID}')
            Thread(target=createEntitiesContinue_processing,args=(lastRunUUID,)).start()
            return response
        except Exception as e:
            logging.error(f'Failed to create fake entities,Error:{e}')
            return {"data": None, "statusCode": HttpStatusCode.INTERNAL_ERROR, "message": None},  HttpStatusCode.INTERNAL_ERROR


@rest_api.route('/api/get-entities/<string:scan_id>')
class GetEntities(Resource):
    """
       get ten users, each of whom will create ten posts, ten comments, and ten to-do lists via the API. 
    """
    @rest_api.expect(validate=True)
    def get(self,scan_id):
        try:
            if (scan_id == False):
                logging.error(f'Scan id is missing to request')
                return {"data": None, "statusCode": HttpStatusCode.BAD_REQUEST, "message": 'scan_id is missing'},  HttpStatusCode.BAD_REQUEST
            scanID = scan_id
            isExist = os.path.exists(f'/tmp/{BaseConfig.STORE_NAME}-{scanID}.json')
            if(isExist == False):
                return {"data": None, "statusCode": HttpStatusCode.INTERNAL_ERROR, "message":'scan is not finished'},  HttpStatusCode.INTERNAL_ERROR
            data = simple_cache.load_key(f'/tmp/{BaseConfig.STORE_NAME}', f'/tmp/{BaseConfig.STORE_NAME}-{scanID}')
            if(data):
                return {"data": data, "statusCode": HttpStatusCode.OK, "message": None}, HttpStatusCode.OK
            with open(f'/tmp/{BaseConfig.STORE_NAME}-{scanID}.json', 'r') as openfile:
                json_object = json.load(openfile)
                return {"data": json_object, "statusCode": HttpStatusCode.OK, "message": None}, HttpStatusCode.OK
            
        except Exception as e:
            logging.error(f'Failed to create fake entities,Error:{e}')
            return {"data": None, "statusCode": HttpStatusCode.INTERNAL_ERROR, "message": None},  HttpStatusCode.INTERNAL_ERROR
