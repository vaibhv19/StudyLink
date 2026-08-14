import uuid
from django.db import models
from django.conf import settings
from core.models import Subject, Course
from vault.storage import ResourceStorage

class Resource(models.Model):
    STATUS_CHOICES = (
        ('PROCESSING', 'Processing'),
        ('READY', 'Ready'),
        ('FAILED', 'Failed'),
        ('UNSEARCHABLE', 'Unsearchable'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_resources"
    )
    title = models.CharField(max_length=255)
    file_path = models.FileField(storage=ResourceStorage())
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PROCESSING'
    )
    is_active = models.BooleanField(default=True)
    upvote_count = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['subject']),
            models.Index(fields=['course']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.title

class ResourceUpvote(models.Model):
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="upvotes"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('resource', 'user')

class DoubtBoardComment(models.Model):
    id = models.AutoField(primary_key=True)
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )
    content = models.TextField()
    is_solved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.email} on {self.resource.title}"


# RAG Vector DB Compatibility Layer
import json
from django.db import connection

try:
    from pgvector.django import VectorField as BaseVectorField
    from pgvector.django import HnswIndex as BaseHnswIndex
except ImportError:
    class BaseVectorField(models.Field):
        def __init__(self, *args, dimensions=None, **kwargs):
            self.dimensions = dimensions
            super().__init__(*args, **kwargs)

    class BaseHnswIndex(models.Index):
        pass


class CompatibleVectorField(BaseVectorField):
    def db_type(self, connection):
        if connection.vendor == 'sqlite':
            return 'TEXT'
        return super().db_type(connection)

    def from_db_value(self, value, expression, connection):
        if connection.vendor == 'sqlite':
            if value is None:
                return value
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return [float(x) for x in value.split(',') if x.strip()]
        if hasattr(super(), 'from_db_value'):
            return super().from_db_value(value, expression, connection)
        return value

    def to_python(self, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return [float(x) for x in value.split(',') if x.strip()]
        if hasattr(super(), 'to_python'):
            return super().to_python(value)
        return value

    def get_prep_value(self, value):
        if connection.vendor == 'sqlite':
            if value is None:
                return value
            return json.dumps(list(value))
        return super().get_prep_value(value)


class CompatibleHnswIndex(BaseHnswIndex):
    def create_sql(self, model, schema_editor, using=''):
        if schema_editor.connection.vendor == 'sqlite':
            return models.Index(fields=self.fields, name=self.name).create_sql(model, schema_editor, using)
        return super().create_sql(model, schema_editor, using)


class ResourceChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="chunks"
    )
    content = models.TextField()
    page_number = models.IntegerField()
    embedding = CompatibleVectorField(dimensions=768)

    class Meta:
        indexes = [
            CompatibleHnswIndex(
                name="resource_chunks_hnsw_idx",
                fields=["embedding"],
                opclasses=["vector_cosine_ops"],
            )
        ]

    def __str__(self):
        return f"Chunk of {self.resource.title} (Page {self.page_number})"

