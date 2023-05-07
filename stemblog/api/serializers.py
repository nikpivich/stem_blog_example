from rest_framework import serializers
from django.contrib.auth import get_user_model
from stemblog.models import News, Profile
from rest_framework import permissions
from django.contrib.auth.hashers import make_password
import re

__all__ = [
    "PostsModelSerializer",
    "PostDetailModelSerializer",
    'ProfileListSerializer',
    'ProfileCreateSerializer',
    'UserCreateSerializer',
    'UserListSerializer',
    'PostPermission',
    'UserViewCreatePermission'
]

User = get_user_model()

############################################################
#                  PROFILES Вложенность                    #

class UserSerializer(serializers.ModelSerializer):
    """Пользователь для просмотра"""

    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class ProfileListSerializer(serializers.ModelSerializer):
    """Просмотр профиля пользователя"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ('phone', 'address', 'hobby', 'user')
        depth = 2

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['phone'] = re.sub(r'\D', '', ret['phone'] or '')
        return ret


class UserSubCreateSerializer(serializers.ModelSerializer):
    """Для создания пользователя"""

    class Meta:
        model = User
        fields = ('username', 'password', 'email')


class ProfileCreateSerializer(serializers.ModelSerializer):
    """Создание профиля и пользователя"""

    user = UserSubCreateSerializer()

    class Meta:
        model = Profile
        fields = ('phone', 'address', 'hobby', 'user')
        depth = 2

    def create(self, validated_data):
        validated_data['user']['password'] = make_password(str(validated_data['user']['password']))
        user = User.objects.create(**validated_data.pop('user'))
        profile = Profile.objects.create(user=user, **validated_data)
        return profile


#############################################
#                  USERS                    #

class UserCreateSerializer(serializers.ModelSerializer):
    """Создание пользователя"""

    phone = serializers.CharField(source='profile.phone', max_length=20, required=False)
    address = serializers.CharField(source='profile.address', max_length=100, required=False)
    hobby = serializers.CharField(source='profile.hobby', max_length=200, required=False)
    email = serializers.EmailField(required=True, max_length=254)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'address', 'hobby', 'password')

    # def to_representation(self, instance):
    #     ret = super(UserCreateSerializer, self).to_representation(instance)
    #     ret['phone'] = re.sub('\D', '', ret['phone'] or '')
    #     return ret


class UserListSerializer(serializers.ModelSerializer):
    """Просмотр всех пользователей"""

    phone = serializers.CharField(source='profile.phone', read_only=True)
    address = serializers.CharField(source='profile.address', read_only=True)
    hobby = serializers.CharField(source='profile.hobby', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'address', 'hobby')


#############################################
#                  POSTS                    #

class PostsModelSerializer(serializers.ModelSerializer):
    """Для вывода всех постов и создания новых"""
    user = UserListSerializer(read_only=True)
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = News
        fields = ('id', 'date', 'user', 'url', 'title', 'content', 'image')
        read_only_fields = ('date',)


class PostDetailModelSerializer(PostsModelSerializer):
    """Для взаимодействия с уже существующими постами"""
    title = serializers.CharField(required=False)
    content = serializers.CharField(required=False)

    class Meta:
        model = News
        fields = ('id', 'date', 'user', 'url', 'title', 'content', 'image')
        read_only_fields = ('date',)

    def save(self, **kwargs):
        validated_data = {**self.validated_data, **kwargs}
        update_fields = []
        for field, value in validated_data.items():
            update_fields.append(field)
            setattr(self.instance, field, value)
        self.instance.save(update_fields=update_fields)
        return self.instance


##########################################
#               Разрешения               #

class PostPermission(permissions.BasePermission):
    """Разрешение на изменение только своего поста, а просмотр всех"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class UserViewCreatePermission(permissions.BasePermission):
    """Просмотр всех пользователей доступен только администраторам, а создание незарегистрированным"""

    def has_permission(self, request, view):
        print(request, view)
        if request.method == 'GET':
            return request.user.is_staff or request.user.is_superuser
        if request.method == 'POST':
            return request.user.is_anonymous or request.user.is_staff or request.user.is_superuser
        return False