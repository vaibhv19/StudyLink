from django.core.files.storage import default_storage

class ResourceStorage(default_storage.__class__):
    pass
