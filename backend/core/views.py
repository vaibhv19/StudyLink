from rest_framework.generics import ListAPIView
from core.models import Subject, Course
from core.serializers import SubjectSerializer, CourseSerializer

class SubjectListView(ListAPIView):
    queryset = Subject.objects.all().order_by('name')
    serializer_class = SubjectSerializer
    permission_classes = []
    pagination_class = None

class CourseListView(ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = []
    pagination_class = None

    def get_queryset(self):
        queryset = Course.objects.all().select_related('subject').order_by('code')
        subject_slug = self.request.query_params.get('subject')
        if subject_slug:
            queryset = queryset.filter(subject__slug=subject_slug)
        return queryset
