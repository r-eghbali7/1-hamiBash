from django.urls import path
from .views import *

urlpatterns = [
    path('', BlogPostListCreateView.as_view(), name='blog-list-create'),
    path('<uuid:pk>/', BlogPostDetailView.as_view(), name='blog-detail'),
    path('<uuid:pk>/update/', BlogPostUpdateView.as_view(), name='blog-update'),
    path('<uuid:pk>/delete/', BlogPostDeleteView.as_view(), name='blog-delete'),
    path('me/', BlogPostMyPostsView.as_view(), name='blog-my-posts'),
    path('tag/<str:tag>/', BlogPostTagListView.as_view(), name='blog-by-tag'),
]
