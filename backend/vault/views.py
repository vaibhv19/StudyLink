from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from vault.serializers import ResourceUploadSerializer, ResourceSerializer

class ResourceListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = ResourceUploadSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        resource = serializer.save()
        response_serializer = ResourceSerializer(resource, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
