import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.s3 import S3Storage

class ListingStorage(S3Storage if getattr(settings, 'USE_S3', False) else FileSystemStorage):
    def __init__(self, *args, **kwargs):
        if getattr(settings, 'USE_S3', False):
            kwargs['location'] = 'listings'
        else:
            kwargs['location'] = os.path.join(settings.MEDIA_ROOT, 'listings')
        super().__init__(*args, **kwargs)
