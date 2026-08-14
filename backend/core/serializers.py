from rest_framework import serializers
from core.models import Subject, Course

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ('id', 'name', 'slug')

class CourseSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'code', 'name', 'subject')
