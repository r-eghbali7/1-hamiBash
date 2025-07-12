# interactions/views.py

from rest_framework import generics, permissions
from .models import Comment
from .serializers import CommentSerializer
from django.contrib.contenttypes.models import ContentType
from notifications.tasks import send_notification_task
from post.models import BlogPost  # ← مسیر درست ایمپورت رو اصلاح کن

class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        model = self.request.query_params.get('model')  # مثال: blogpost
        object_id = self.request.query_params.get('object_id')

        content_type = ContentType.objects.get(model=model)

        return Comment.objects.filter(
            content_type=content_type,
            object_id=object_id,
            parent=None,
            is_approved=True
        ).prefetch_related('replies')

    def perform_create(self, serializer):
        comment = serializer.save(user=self.request.user)
        user = self.request.user
        content_obj = comment.content_object

        if isinstance(content_obj, BlogPost):
            if content_obj.author != user:
                send_notification_task.delay(
                    user_id=content_obj.author.id,
                    message=f"{user.full_name} روی پست شما کامنت گذاشت."
                )

        if comment.parent and comment.parent.user != user:
            send_notification_task.delay(
                user_id=comment.parent.user.id,
                message=f"{user.full_name} به کامنت شما پاسخ داد."
            )
