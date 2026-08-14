import math
import os
import sys
# Disable C-extension for protobuf on Python 3.14 to avoid metaclass tp_new TypeError
sys.modules['google._upb._message'] = None
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

from django.db import connection
from vault.models import ResourceChunk

def calculate_python_cosine_distance(v1, v2):
    dot_product = sum(x * y for x, y in zip(v1, v2))
    norm_v1 = math.sqrt(sum(x * x for x in v1))
    norm_v2 = math.sqrt(sum(x * x for x in v2))
    if norm_v1 == 0 or norm_v2 == 0:
        return 1.0
    similarity = dot_product / (norm_v1 * norm_v2)
    # Cosine distance = 1 - cosine similarity
    dist = 1.0 - similarity
    # Bound it between 0 and 2 due to floating point inaccuracies
    return max(0.0, min(2.0, dist))

class VectorSearchService:
    @staticmethod
    def similarity_search(resource_id, query_embedding):
        """
        Retrieves the top 5 closest text chunks to the query embedding within a single resource.
        Returns a list of tuples: (ResourceChunk instance, cosine_distance)
        """
        if connection.vendor == 'sqlite':
            # SQLite fallback
            chunks = ResourceChunk.objects.filter(resource_id=resource_id)
            results = []
            for chunk in chunks:
                dist = calculate_python_cosine_distance(chunk.embedding, query_embedding)
                results.append((chunk, dist))
            
            # Sort by distance ascending
            results.sort(key=lambda x: x[1])
            return results[:5]
            
        else:
            # PostgreSQL pgvector query using <=> operator
            from pgvector.django import CosineDistance
            queryset = ResourceChunk.objects.filter(resource_id=resource_id).annotate(
                distance=CosineDistance('embedding', query_embedding)
            ).order_by('distance')[:5]
            
            return [(chunk, chunk.distance) for chunk in queryset]
