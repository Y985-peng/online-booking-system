from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.contrib.auth import get_user_model
from .models import Post, PostLike, PostFavorite, PostComment, Follow, Notification
from .serializers import PostSerializer, PostCommentSerializer, NotificationSerializer
from services.models import Service

User = get_user_model()


class PostListCreateView(generics.GenericAPIView):
    """帖子列表 / 发布帖子"""
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def get(self, request):
        if request.user.role == 'admin':
            posts = Post.objects.all()
        else:
            posts = Post.objects.filter(is_approved=True)
        
        service_id = request.query_params.get('service')
        if service_id:
            posts = posts.filter(service_id=service_id)
        
        search = request.query_params.get('search', '')
        if search:
            posts = posts.filter(content__icontains=search)
        
        ordering = request.query_params.get('ordering', '-created_at')
        if ordering in ['-like_count', 'like_count']:
            from django.db.models import Count, Value, IntegerField
            posts = posts.annotate(like_cnt=Count('likes'))
            order_field = ordering.replace('like_count', 'like_cnt')
            posts = posts.order_by(order_field, '-created_at')
        else:
            posts = posts.order_by(ordering, '-created_at')
        
        data = PostSerializer(posts, many=True, context={'request': request}).data
        return Response({'code': 200, 'data': data})

    def post(self, request):
        content = request.data.get('content', '').strip()
        if not content:
            return Response({'code': 400, 'message': '内容不能为空'}, status=400)

        service_id = request.data.get('service_id')
        service = None
        if service_id:
            service = get_object_or_404(Service, id=service_id)

        post = Post.objects.create(user=request.user, content=content, service=service, is_approved=request.user.role == 'admin')
        return Response({
            'code': 201,
            'message': '发布成功',
            'data': PostSerializer(post, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)


class PostDetailView(generics.GenericAPIView):
    """帖子详情（含互动状态）"""
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        data = PostSerializer(post, context={'request': request}).data
        return Response({'code': 200, 'data': data})


class PostLikeToggleView(generics.GenericAPIView):
    """点赞/取消点赞"""
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like, created = PostLike.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
            return Response({'code': 200, 'is_liked': False, 'like_count': post.likes.count()})
        # 创建通知
        if post.user != request.user:
            Notification.objects.create(user=post.user, from_user=request.user, post=post, type='like')
        return Response({'code': 201, 'is_liked': True, 'like_count': post.likes.count()})


class PostFavoriteToggleView(generics.GenericAPIView):
    """收藏/取消收藏"""
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        fav, created = PostFavorite.objects.get_or_create(user=request.user, post=post)
        if not created:
            fav.delete()
            return Response({'code': 200, 'is_favorited': False, 'favorite_count': post.favorites.count()})
        # 创建通知
        if post.user != request.user:
            Notification.objects.create(user=post.user, from_user=request.user, post=post, type='favorite')
        return Response({'code': 201, 'is_favorited': True, 'favorite_count': post.favorites.count()})


class PostCommentListCreateView(generics.GenericAPIView):
    """评论列表 / 发表评论"""
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        comments = post.comments.all()
        data = PostCommentSerializer(comments, many=True).data
        return Response({'code': 200, 'data': data})

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        content = request.data.get('content', '').strip()
        if not content:
            return Response({'code': 400, 'message': '内容不能为空'}, status=400)
        comment = PostComment.objects.create(user=request.user, post=post, content=content)
        # 创建通知
        if post.user != request.user:
            Notification.objects.create(user=post.user, from_user=request.user, post=post, type='comment', content=content[:60])
        return Response({
            'code': 201,
            'message': '评论成功',
            'data': PostCommentSerializer(comment).data
        }, status=status.HTTP_201_CREATED)


class UserPostsView(generics.GenericAPIView):
    """某个用户的所有帖子"""
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        posts = Post.objects.filter(user=user).order_by('-created_at')
        data = PostSerializer(posts, many=True, context={'request': request}).data
        return Response({'code': 200, 'data': data})


class MyPostsView(generics.GenericAPIView):
    """我自己的帖子"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.filter(user=request.user).order_by('-created_at')
        data = PostSerializer(posts, many=True, context={'request': request}).data
        return Response({'code': 200, 'data': data})


class FollowToggleView(generics.GenericAPIView):
    """关注/取消关注"""
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        target = get_object_or_404(User, id=user_id)
        if target == request.user:
            return Response({'code': 400, 'message': '不能关注自己'}, status=400)

        follow = Follow.objects.filter(follower=request.user, following=target)
        if follow.exists():
            follow.delete()
            return Response({'code': 200, 'message': '已取消关注', 'is_following': False})
        else:
            Follow.objects.create(follower=request.user, following=target)
            return Response({'code': 201, 'message': '已关注', 'is_following': True}, status=201)


class FollowStatsView(generics.GenericAPIView):
    """关注/粉丝统计"""
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        following_count = Follow.objects.filter(follower=user).count()
        followers_count = Follow.objects.filter(following=user).count()
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()
        return Response({
            'code': 200,
            'data': {
                'following_count': following_count,
                'followers_count': followers_count,
                'is_following': is_following,
            }
        })


class LikedPostsView(generics.GenericAPIView):
    """我点赞过的帖子"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        post_ids = PostLike.objects.filter(user=request.user).values_list('post_id', flat=True)
        posts = Post.objects.filter(id__in=post_ids).order_by('-created_at')
        data = PostSerializer(posts, many=True, context={'request': request}).data
        return Response({'code': 200, 'data': data})


class FavoritedPostsView(generics.GenericAPIView):
    """我收藏过的帖子"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        post_ids = PostFavorite.objects.filter(user=request.user).values_list('post_id', flat=True)
        posts = Post.objects.filter(id__in=post_ids).order_by('-created_at')
        data = PostSerializer(posts, many=True, context={'request': request}).data
        return Response({'code': 200, 'data': data})


class NotificationListView(generics.GenericAPIView):
    """通知列表"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifs = Notification.objects.filter(user=request.user)
        data = NotificationSerializer(notifs, many=True).data
        return Response({'code': 200, 'data': data})


class NotificationUnreadCountView(generics.GenericAPIView):
    """未读通知数"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'code': 200, 'data': {'count': count}})


class NotificationReadAllView(generics.GenericAPIView):
    """全部标记已读"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'code': 200, 'message': '已全部标记已读'})


class PendingPostsView(generics.GenericAPIView):
    """待审核帖子（管理员）"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'admin':
            return Response({'code': 403, 'message': '仅管理员可查看'}, status=403)
        posts = Post.objects.filter(is_approved=False).order_by('-created_at')
        data = PostSerializer(posts, many=True, context={'request': request}).data
        return Response({'code': 200, 'data': data})


class ApprovePostView(generics.GenericAPIView):
    """审核通过"""
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        if request.user.role != 'admin':
            return Response({'code': 403, 'message': '仅管理员可操作'}, status=403)
        post = get_object_or_404(Post, id=post_id)
        post.is_approved = True
        post.save()
        return Response({'code': 200, 'message': '已通过审核'})


class RejectPostView(generics.GenericAPIView):
    """拒绝（删除）"""
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        if request.user.role != 'admin':
            return Response({'code': 403, 'message': '仅管理员可操作'}, status=403)
        post = get_object_or_404(Post, id=post_id)
        post.delete()
        return Response({'code': 200, 'message': '已拒绝'})
