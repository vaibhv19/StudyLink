from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from core.pagination import StandardResultsSetPagination
from vault.models import Resource
from vault.serializers import ResourceUploadSerializer, ResourceSerializer

class ResourceListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ResourceUploadSerializer
        return ResourceSerializer

    def get_queryset(self):
        queryset = Resource.objects.filter(is_active=True).select_related('uploader', 'subject', 'course').order_by('-id')
        
        subject_slug = self.request.query_params.get('subject')
        if subject_slug:
            queryset = queryset.filter(subject__slug=subject_slug)
            
        course_code = self.request.query_params.get('course')
        if course_code:
            queryset = queryset.filter(course__code=course_code)
            
        search_query = self.request.query_params.get('search') or self.request.query_params.get('title')
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
            
        return queryset

    def create(self, request, *args, **kwargs):
        # Use ResourceUploadSerializer for creation, but return ResourceSerializer representation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resource = serializer.save()
        response_serializer = ResourceSerializer(resource, context=self.get_serializer_context())
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

class ResourceDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ResourceSerializer
    queryset = Resource.objects.filter(is_active=True).select_related('uploader', 'subject', 'course')
