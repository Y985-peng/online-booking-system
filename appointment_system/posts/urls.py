from django.urls import path
from .views import (
    PostListCreateView, PostDetailView,
    PostLikeToggleView, PostFavoriteToggleView,
    PostCommentListCreateView,
    UserPostsView, MyPostsView,
    LikedPostsView, FavoritedPostsView,
    NotificationListView, NotificationUnreadCountView, NotificationReadAllView,
    FollowToggleView, FollowStatsView,
    PendingPostsView, ApprovePostView, RejectPostView,
)

urlpatterns = [
    path('', PostListCreateView.as_view(), name='post-list'),
    path('<int:post_id>/', PostDetailView.as_view(), name='post-detail'),
    path('<int:post_id>/like/', PostLikeToggleView.as_view(), name='post-like'),
    path('<int:post_id>/favorite/', PostFavoriteToggleView.as_view(), name='post-favorite'),
    path('<int:post_id>/comments/', PostCommentListCreateView.as_view(), name='post-comments'),
    path('my/', MyPostsView.as_view(), name='my-posts'),
    path('liked/', LikedPostsView.as_view(), name='liked-posts'),
    path('favorited/', FavoritedPostsView.as_view(), name='favorited-posts'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/unread-count/', NotificationUnreadCountView.as_view(), name='notif-unread'),
    path('notifications/read-all/', NotificationReadAllView.as_view(), name='notif-read-all'),
    path('pending/', PendingPostsView.as_view(), name='posts-pending'),
    path('<int:post_id>/approve/', ApprovePostView.as_view(), name='post-approve'),
    path('<int:post_id>/reject/', RejectPostView.as_view(), name='post-reject'),
    path('user/<int:user_id>/', UserPostsView.as_view(), name='user-posts'),
    path('follow/<int:user_id>/', FollowToggleView.as_view(), name='follow-toggle'),
    path('follow/stats/<int:user_id>/', FollowStatsView.as_view(), name='follow-stats'),
]
