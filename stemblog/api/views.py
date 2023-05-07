import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models import Q

from rest_framework import permissions
from rest_framework import generics
from rest_framework.views import Response
from rest_framework import status

from stemblog.api.serializers import PostsModelSerializer, PostDetailModelSerializer, ProfileListSerializer, \
    ProfileCreateSerializer, UserCreateSerializer, UserListSerializer, PostPermission, UserViewCreatePermission
from stemblog.paginator import LargeTablePaginatorAPI
from stemblog import models

User = get_user_model()


#################################################
#                   PROFILES                    #


class ProfileListCreateAPIView(generics.ListCreateAPIView):
    """Просмотр всех профилей пользователей и создание нового"""
    permission_classes = [UserViewCreatePermission]
    queryset = models.Profile.objects.all()
    serializer_class = ProfileCreateSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProfileListSerializer
        return ProfileCreateSerializer


#################################################
#                     USERS                     #

class UserListCreateAPIView(generics.ListCreateAPIView):
    """Просмотр всех пользователей и создание нового"""

    permission_classes = [permissions.IsAdminUser]
    queryset = models.User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserListSerializer
        return UserCreateSerializer

    def create(self, request, *args, **kwargs):
        profile_fields = [f.name for f in models.Profile._meta.get_fields()]
        user_fields = [f.name for f in User._meta.get_fields()]

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = dict(serializer.data)

        profile = models.Profile(**{k: v for k, v in data.items() if k in profile_fields})
        data['password'] = make_password(data['password'])
        user = User.objects.create(**{k: v for k, v in data.items() if k in user_fields})
        profile.user = user
        profile.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserDetailAPIView(generics.RetrieveAPIView):
    """Просмотр пользователя"""

    serializer_class = UserListSerializer
    lookup_field = 'username'
    lookup_url_kwarg = 'username'
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()


#################################################
#                    POSTS                      #

class PostViewAPIView(generics.ListCreateAPIView):
    """Просмотр всех постов и создание нового"""

    serializer_class = PostsModelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = LargeTablePaginatorAPI
    # authentication_classes = [TokenAuthentication]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        query = Q()

        if self.request.GET.get('date'):
            date = datetime.datetime.strptime(self.request.GET['date'], '%Y-%m-%d')
            date_to = date + datetime.timedelta(days=1)
            query = Q(date__gte=date) & Q(date__lt=date_to)

        if self.request.GET.get('search'):
            s = self.request.GET['search']
            query &= (Q(title__contains=s) | Q(content__contains=s))

        q = models.News.objects.filter(query).all().select_related()
        return q


class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Просмотр, изменение и удаление поста"""

    serializer_class = PostDetailModelSerializer
    permission_classes = [PostPermission]
    queryset = models.News.objects.all()