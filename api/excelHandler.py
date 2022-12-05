import xlsxwriter
import logging
import os
from .config import BaseConfig
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
load_dotenv()


def createAllGoRestDataInExcel(users, posts, comments, todos):
    try:
        xlsxFile = xlsxwriter.Workbook(BaseConfig.GO_REST_EXCEL_FILENAME)
        sheetOne = xlsxFile.add_worksheet("Users")
        sheetTwo = xlsxFile.add_worksheet("Posts")
        sheetThree = xlsxFile.add_worksheet("Comments")
        sheetFour = xlsxFile.add_worksheet("Todos")
        usersRow = 1
        sheetOne.write(0, 0, "id")
        sheetOne.write(0, 1, "name")
        sheetOne.write(0, 2, "email")
        sheetOne.write(0, 3, "gender")
        sheetOne.write(0, 4, "status")
        for item in users:
            sheetOne.write(usersRow, 0, item["id"])
            sheetOne.write(usersRow, 1, item["name"])
            sheetOne.write(usersRow, 2, item["email"])
            sheetOne.write(usersRow, 3, item["gender"])
            sheetOne.write(usersRow, 4, item["status"])
            usersRow += 1
#####################################################
        postsRow = 1
        sheetTwo.write(0, 0, "id")
        sheetTwo.write(0, 1, "user_id")
        sheetTwo.write(0, 2, "body")
        sheetTwo.write(0, 3, "title")
        for item in posts:
            sheetTwo.write(postsRow, 0, item["id"])
            sheetTwo.write(postsRow, 1, item["user_id"])
            sheetTwo.write(postsRow, 2, item["body"])
            sheetTwo.write(postsRow, 3, item["title"])
            postsRow += 1
#####################################################
        commentsRow = 1
        sheetThree.write(0, 0, "id")
        sheetThree.write(0, 1, "post_id")
        sheetThree.write(0, 2, "name")
        sheetThree.write(0, 3, "email")
        sheetThree.write(0, 4, "body")
        for item in comments:
            sheetThree.write(commentsRow, 0, item["id"])
            sheetThree.write(commentsRow, 1, item["post_id"])
            sheetThree.write(commentsRow, 2, item["name"])
            sheetThree.write(commentsRow, 3, item["email"])
            sheetThree.write(commentsRow, 4, item["body"])
            commentsRow += 1
#####################################################
        todosRow = 1
        sheetFour.write(0, 0, "id")
        sheetFour.write(0, 1, "user_id")
        sheetFour.write(0, 2, "title")
        sheetFour.write(0, 3, "due_on")
        sheetFour.write(0, 4, "status")
        for item in todos:
            sheetFour.write(todosRow, 0, item["id"])
            sheetFour.write(todosRow, 1, item["user_id"])
            sheetFour.write(todosRow, 2, item["title"])
            sheetFour.write(todosRow, 3, item["due_on"])
            sheetFour.write(todosRow, 4, item["status"])
            todosRow += 1
        xlsxFile.close()
    except Exception as e:
        logging.error(e)


def uploadExcelToS3Aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
                      aws_secret_access_key=os.getenv('S3_SECRET_KEY'))
    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False
