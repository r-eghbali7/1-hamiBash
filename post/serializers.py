# post/serializers.py
from rest_framework import serializers
from .models import BlogPost
from taggit.serializers import TagListSerializerField, TaggitSerializer


class BlogPostSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'body', 'author_name', 'is_published', 'created_at', 'updated_at', 'tags']
        read_only_fields = ['id', 'author_name', 'created_at', 'updated_at']
