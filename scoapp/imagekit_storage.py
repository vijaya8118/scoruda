import requests
import uuid
from django.core.files.storage import Storage
from django.conf import settings

class ImageKitStorage(Storage):
    def _save(self, name, content):
        url = "https://upload.imagekit.io/api/v1/files/upload"

        files = {
            "file": (name or str(uuid.uuid4()), content),
        }

        data = {
            "fileName": name or str(uuid.uuid4()),
            "useUniqueFileName": "true",  # ✅ must be a string
        }

        response = requests.post(
            url,
            auth=(settings.IMAGEKIT_PRIVATE_KEY, ''),
            data=data,
            files=files
        )

        if response.status_code == 200:
            return response.json()["url"]
        else:
            raise Exception(f"ImageKit upload failed: {response.text}")

    def url(self, name):
        return name  # This is already a full URL from ImageKit

    def exists(self, name):
        return False
