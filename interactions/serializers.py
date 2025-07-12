# interactions/serializers.py
from rest_framework import serializers
from .models import Comment
from django.contrib.contenttypes.models import ContentType

class RecursiveCommentSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = CommentSerializer(value, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    replies = RecursiveCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'text', 'created_at', 'parent', 'replies',
            'content_type', 'object_id'
        ]
        read_only_fields = ['user', 'created_at', 'replies']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
