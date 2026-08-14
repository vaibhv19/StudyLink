import math
import os
import sys
# Disable C-extension for protobuf on Python 3.14 to avoid metaclass tp_new TypeError
sys.modules['google._upb._message'] = None
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

from django.db import connection
from vault.models import ResourceChunk
from rag.client import GeminiClient
from rag.prompt import GROUNDING_PROMPT_TEMPLATE

def calculate_python_cosine_distance(v1, v2):
    dot_product = sum(x * y for x, y in zip(v1, v2))
    norm_v1 = math.sqrt(sum(x * x for x in v1))
    norm_v2 = math.sqrt(sum(x * x for x in v2))
    if norm_v1 == 0 or norm_v2 == 0:
        return 1.0
    similarity = dot_product / (norm_v1 * norm_v2)
    dist = 1.0 - similarity
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


class RAGAnswerService:
    @staticmethod
    def answer_query(resource_id, query_text):
        """
        Coordinates RAG execution: generates query embedding, executes similarity search,
        applies threshold cutoff, formats grounding prompt, and queries Gemini LLM.
        """
        # 1. Generate query embedding
        query_embedding = GeminiClient.get_embedding(query_text)
        
        # 2. Retrieve top 5 matches
        results = VectorSearchService.similarity_search(resource_id, query_embedding)
        
        fallback_response = "I couldn't find any relevant information in this specific document to answer that."
        
        if not results:
            return {
                'answer': fallback_response,
                'citations': [],
                'sources': []
            }
            
        # 3. Compute top chunk similarity score
        top_chunk, top_distance = results[0]
        top_similarity = 1.0 - top_distance
        
        # 4. Enforce Cutoff Threshold
        if top_similarity < 0.65:
            return {
                'answer': fallback_response,
                'citations': [],
                'sources': []
            }
            
        # 5. Collect context and citations
        excerpts_list = []
        citations_set = set()
        sources = []
        for chunk, dist in results:
            excerpts_list.append(f"[Page {chunk.page_number}]:\n{chunk.content}")
            citations_set.add(chunk.page_number)
            sources.append({
                'page_number': chunk.page_number,
                'excerpt': chunk.content,
                'similarity_score': round(1.0 - dist, 4)
            })
            
        context_text = "\n\n".join(excerpts_list)
        
        # 6. Format grounding prompt
        prompt = GROUNDING_PROMPT_TEMPLATE.format(
            query=query_text,
            context=context_text
        )
        
        # 7. Generate answer using Gemini
        answer = GeminiClient.generate_answer(prompt)
        
        return {
            'answer': answer.strip(),
            'citations': sorted(list(citations_set)),
            'sources': sources
        }
