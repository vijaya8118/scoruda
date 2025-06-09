import os
import uuid
import requests
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible


@deconstructible
class ImageKitStorage(Storage):
    def _save(self, name, content):
        private_key = os.environ.get('IMAGEKIT_PRIVATE_KEY')
        if not private_key:
            raise Exception("IMAGEKIT_PRIVATE_KEY not set in environment variables.")

        url = "https://upload.imagekit.io/api/v1/files/upload"

        files = {
            "file": (name or str(uuid.uuid4()), content),
        }

        data = {
            "fileName": name or str(uuid.uuid4()),
            "useUniqueFileName": "true",
        }

        response = requests.post(
            url,
            auth=(private_key, ""),
            data=data,
            files=files
        )

        if response.status_code == 200:
            # Returning the filename so that Django knows what to store
            return response.json().get("name")
        else:
            raise Exception(f"ImageKit upload failed: {response.text}")

    def exists(self, name):
        # You can make an API call to check if a file exists on ImageKit
        # But here we'll return False to always allow upload (can be customized)
        return False

    def url(self, name):
        public_url_base = os.environ.get("IMAGEKIT_URL_ENDPOINT")
        if not public_url_base:
            raise Exception("IMAGEKIT_URL_ENDPOINT not set in environment variables.")
        return f"{public_url_base.rstrip('/')}/{name}"

    def _open(self, name, mode='rb'):
        url = self.url(name)
        response = requests.get(url)
        if response.status_code == 200:
            return ContentFile(response.content)
        raise FileNotFoundError(f"Unable to open file at {url}")