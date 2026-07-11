from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, CreateConversationSerializer
from services.models import Service

User = get_user_model()


class ConversationListCreateView(generics.GenericAPIView):
    """创建对话 / 获取对话列表"""
    permission_classes = [IsAuthenticated]
    serializer_class = CreateConversationSerializer

    def get(self, request):
        convs = Conversation.objects.filter(participants=request.user).order_by('-updated_at')
        data = ConversationSerializer(convs, many=True, context={"request": request}).data
        return Response({'code': 200, 'data': data})

    def post(self, request):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)

        provider = get_object_or_404(User, id=ser.validated_data['provider_id'])
        service_id = ser.validated_data.get('service_id')
        service = get_object_or_404(Service, id=service_id) if service_id else None

        # 自动添加 admin 账号作为客服
        admin = User.objects.filter(role='admin').first()

        # 查找是否已有相同参与者的对话
        participants = [request.user, provider]
        if admin:
            participants.append(admin)

        existing = Conversation.objects.filter(
            participants=request.user
        ).filter(participants=provider)
        if service:
            existing = existing.filter(service=service)
        if admin:
            existing = existing.filter(participants=admin)

        # 更精确的查找：找参与人数完全匹配的对话
        for conv in existing:
            if set(conv.participants.all()) == set(participants):
                return Response({
                    'code': 200,
                    'message': '对话已存在',
                    'data': ConversationSerializer(conv, context={'request': request}).data
                })

        conv = Conversation.objects.create(service=service)
        conv.participants.add(request.user, provider)
        if admin:
            conv.participants.add(admin)

        return Response({
            'code': 201,
            'message': '对话已创建',
            'data': ConversationSerializer(conv, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)


class MessageListCreateView(generics.GenericAPIView):
    """获取消息 / 发送消息"""
    permission_classes = [IsAuthenticated]

    def get(self, request, conv_id):
        conv = get_object_or_404(Conversation, id=conv_id, participants=request.user)
        messages = conv.messages.all()
        data = MessageSerializer(messages, many=True).data
        # 标记为已读
        conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        return Response({'code': 200, 'data': data})

    def post(self, request, conv_id):
        conv = get_object_or_404(Conversation, id=conv_id, participants=request.user)
        content = request.data.get('content', '').strip()
        if not content:
            return Response({'code': 400, 'message': '消息不能为空'}, status=400)
        msg = Message.objects.create(conversation=conv, sender=request.user, content=content)
        return Response({
            'code': 201,
            'message': '发送成功',
            'data': MessageSerializer(msg).data
        }, status=status.HTTP_201_CREATED)


class ConversationDetailView(generics.GenericAPIView):
    """对话详情"""
    permission_classes = [IsAuthenticated]

    def get(self, request, conv_id):
        conv = get_object_or_404(Conversation, id=conv_id, participants=request.user)
        return Response({
            'code': 200,
            'data': ConversationSerializer(conv, context={'request': request}).data
        })


class UnreadCountView(generics.GenericAPIView):
    """获取当前用户未读消息总数"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Q
        count = Message.objects.filter(
            conversation__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
        return Response({'code': 200, 'data': {'count': count}})
