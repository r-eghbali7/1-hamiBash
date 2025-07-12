# interactions/utils.py
from .models import Comment
from django.contrib.contenttypes.models import ContentType

def serialize_comment(comment):
    return {
        "id": comment.id,
        "user": comment.user.full_name,
        "text": comment.text,
        "created_at": comment.created_at,
        "replies": [
            serialize_comment(reply)
            for reply in comment.replies.filter(is_approved=True)
        ],
    }

def get_comments_for_object(content_object):
    content_type = ContentType.objects.get_for_model(content_object)
    root_comments = Comment.objects.filter(
        content_type=content_type,
        object_id=content_object.id,
        parent=None
    )
    return [serialize_comment(comment) for comment in root_comments]
