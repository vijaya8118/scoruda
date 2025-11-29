from django.utils.functional import LazyObject
from django.utils.module_loading import import_string

class LazyImageKitStorage(LazyObject):
    def _setup(self):
        self._wrapped = import_string('scoapp.imagekit_storage.ImageKitStorage')()
