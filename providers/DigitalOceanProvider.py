import boto3
from botocore.client import Config

class DigitalOceanProvider:
    def __init__(self, credentials):
        self.bucket_name = credentials['bucket_name']
        self.region = credentials['region']
        self.key = credentials['key']
        self.secret = credentials['secret']
        self.client = None

        pass

    def credentials_correct(self):
        try:
            client = self.get_client()
            client.list_objects(Bucket=self.bucket_name)
        except:
            return False

        return True

    def sync_file(self, key, path, content_type):
        print("Uploading " + path + " to " + key)

        with open(path, 'rb') as data:
            self.get_client().put_object(Key=key, Body=data, Bucket=self.bucket_name,
                                 ACL='public-read',
                                 ContentType=content_type)

    def sync_string(self, key, content, content_type):
        # response = self.get_client().list_buckets()
        # print (response)

        self.get_client().put_object(Key=key, Body=content, Bucket=self.bucket_name,
                                  ACL='public-read',
                                  ContentType=content_type)

    def base_path(self):
        return "https://" + self.bucket_name + "." + self.region + ".digitaloceanspaces.com/"

    def get_client(self):
        if self.client is not None:
            return self.client
        # Digital Ocean has an Amazon S3 compatible API, so we can use Boto.
        self.client = boto3.client('s3',
                                   aws_access_key_id=self.key,
                                   aws_secret_access_key=self.secret,
                                   endpoint_url='https://' + self.region + '.digitaloceanspaces.com',
                                   config=Config(
                                        max_pool_connections=50,
                                    ))

        return self.client
