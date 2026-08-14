from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rag.serializers import ChatQuerySerializer
from rag.search import RAGAnswerService

class ChatQueryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChatQuerySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "code": "invalid_request",
                "message": "Invalid query request.",
                "fields": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        resource_id = serializer.validated_data['resource_id']
        query = serializer.validated_data['query']
        
        try:
            result = RAGAnswerService.answer_query(resource_id=resource_id, query_text=query)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "code": "rag_error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
