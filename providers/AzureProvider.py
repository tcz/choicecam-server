import os, uuid
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, ContentSettings


class AzureProvider:
    def __init__(self, credentials):
        self.container_name = credentials['container_name']
        self.connection_string = credentials['connection_string']
        self.client = None

        pass

    def credentials_correct(self):
        try:
            client = self.get_client()
            container_client = client.get_container_client(self.container_name)
            container_client.list_blobs()
        except:
            return False

        return True

    def sync_file(self, key, path, content_type):
        with open(path, 'rb') as data:
            blob_client = self.get_client().get_blob_client(container=self.container_name, blob=key)
            my_content_settings = ContentSettings(content_type=content_type)
            blob_client.upload_blob(data, overwrite=True, content_settings=my_content_settings)

    def sync_string(self, key, content, content_type):
        blob_client = self.get_client().get_blob_client(container=self.container_name, blob=key)
        my_content_settings = ContentSettings(content_type=content_type)
        blob_client.upload_blob(content, overwrite=True, content_settings=my_content_settings)

    def base_path(self):
        return "https://" + self.container_name + ".blob.core.windows.net/" + self.container_name + "/"

    def get_client(self):
        if self.client is not None:
            return self.client

        self.client = BlobServiceClient.from_connection_string(self.connection_string)

        return self.client


