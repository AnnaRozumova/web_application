import os
from dotenv import load_dotenv
import boto3
import io
from botocore.exceptions import BotoCoreError, ClientError

load_dotenv()

S3_BUCKET = 'webcamera-app-hu2119tru05'

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')

class S3Handler:
    def __init__(self):
        """
        Initialize an S3Handler instance that has its own S3 client.
        """
        self.s3_client = boto3.client(
            "s3",
            region_name=AWS_DEFAULT_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

    def upload_bytes_and_get_presigned_url(
        self,
        image_bytes: bytes,
        object_name: str,
        expiration: int = 3600
    ) -> str:
        """
        Uploads image bytes to S3 and returns a presigned URL for the object.
        """
        try:
            file_obj = io.BytesIO(image_bytes)

            self.s3_client.upload_fileobj(file_obj, S3_BUCKET, object_name)

            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET, 'Key': object_name},
                ExpiresIn=expiration
            )

            return url

        except (BotoCoreError, ClientError) as e:
            raise RuntimeError(f"Failed to upload or generate URL: {str(e)}") from e
