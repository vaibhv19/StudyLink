import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.s3 import S3Storage

class ResourceStorage(S3Storage if getattr(settings, 'USE_S3', False) else FileSystemStorage):
    def __init__(self, *args, **kwargs):
        if getattr(settings, 'USE_S3', False):
            kwargs['location'] = 'resources'
        else:
            kwargs['location'] = os.path.join(settings.MEDIA_ROOT, 'resources')
        super().__init__(*args, **kwargs)
