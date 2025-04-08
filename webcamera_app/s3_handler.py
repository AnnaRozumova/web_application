'''This module provides functionality for interacting with an AWS S3 bucket. 
It allows uploading image bytes to S3 and generating a presigned URL to 
access the uploaded object.'''
import os
import io
import logging
from dotenv import load_dotenv
import boto3
from botocore.exceptions import BotoCoreError, ClientError

load_dotenv()
LOGGER = logging.getLogger(__name__)

S3_BUCKET = 'webcamera-app-dev-65t20mo50'

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')

class S3Handler:
    '''A class that handles interactions with an AWS S3 bucket'''
    def __init__(self) -> None:
        '''Initialize an S3Handler instance that has its own S3 client.'''
        self.s3_client: "boto3.client" = boto3.client(
            "s3",
            region_name=AWS_DEFAULT_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        LOGGER.info("Initialized S3Handler with AWS credentials, AWS_DEFAULT_REGION=%s, AWS_ACCESS_KEY_ID=%s, AWS_SECRET_ACCESS_KEY=%s", AWS_DEFAULT_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

    def upload_bytes_and_get_presigned_url(
        self,
        image_bytes: bytes,
        object_name: str,
        expiration: int = 3600
    ) -> str:
        '''Uploads image bytes to S3 and returns a presigned URL for the object.'''
        file_obj = io.BytesIO(image_bytes)
        try:
            LOGGER.info("Uploading %s to S3", object_name)
            self.s3_client.upload_fileobj(file_obj, S3_BUCKET, object_name)
            url: str = str(self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET, 'Key': object_name},
                ExpiresIn=expiration
            ))
            LOGGER.info("Successfully uploaded object_name=%s. Presigned url: %s", object_name, url)
            return url

        except (BotoCoreError, ClientError) as e:
            LOGGER.error("Failed to upload or generate URL: %s", e)
            raise RuntimeError(f"Failed to upload or generate URL: {str(e)}") from e
