from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from taggit.models import Tag
from .models import BlogPost
from .serializers import BlogPostSerializer

class BlogPostListCreateView(generics.ListCreateAPIView):
    queryset = BlogPost.objects.filter(status="published")
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        user = self.request.user
        if user.user_level != "content_creator":
            raise PermissionDenied("تنها تولیدکنندگان محتوا می‌توانند پست ایجاد کنند.")
        serializer.save(author=user, status="pending")

class BlogPostDetailView(generics.RetrieveAPIView):
    queryset = BlogPost.objects.filter(status="published")
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.AllowAny]

class BlogPostUpdateView(generics.UpdateAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        blog = self.get_object()
        user = self.request.user
        if blog.author != user and not user.is_staff:
            raise PermissionDenied("فقط نویسنده یا ادمین می‌تواند این پست را ویرایش کند.")
        if blog.status == "published" and not user.is_staff:
            raise PermissionDenied("پست منتشر شده فقط توسط ادمین قابل ویرایش است.")
        serializer.save()

class BlogPostDeleteView(generics.DestroyAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        user = self.request.user
        if instance.author != user and not user.is_staff:
            raise PermissionDenied("فقط نویسنده یا ادمین می‌تواند این پست را حذف کند.")
        instance.delete()

class BlogPostMyPostsView(generics.ListAPIView):
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BlogPost.objects.filter(author=self.request.user)

class BlogPostTagListView(generics.ListAPIView):
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        tag = self.kwargs["tag"]
        return BlogPost.objects.filter(tags__name__in=[tag], status="published")
