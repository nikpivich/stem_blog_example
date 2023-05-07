from rest_framework import serializers, permissions
from .models import News
from django.contrib.auth.models import User


#для явного указания полей
class NewsSerializer(serializers.Serializer):

    title = serializers.CharField(required=True, max_length=15)
    content = serializers.CharField(required=True)

    def create(self, validated_data):
        return News.objects.create(**validated_data)

    def update(self, instance: News, validated_data):
        instance.title = validated_data['title']
        instance.content = validated_data['content']
        instance.save()
        return instance


# с использованием модели
class NewsModelSerializer(serializers.ModelSerializer):
    """
    Для вывода всех постов и создания новых
    """

    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = News
        fields = ('title', 'content', 'date', 'user', 'image', 'id')
        read_only_fields = ('date',)


class UserSerializers(serializers.ModelSerializer):
    """Просмотр всех пользователей"""
    phone = serializers.CharField(source='profile.phone', max_length=20, required=False)
    country = serializers.CharField(source='profile.country', max_length=100, required=False)
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'country')

class UserCreateSerializer(serializers.ModelSerializer):
        """Создание пользователя"""

        phone = serializers.CharField(source='profile.phone', max_length=20, required=False)
        country = serializers.CharField(source='profile.country', max_length=100, required=False)

        class Meta:
            model = User
            fields = ('id', 'username', 'email', 'phone', 'country', 'password')



                  # Permission
####################################################
class NewsPermission(permissions.BasePermission):
    """
    Разрешение на изменение только своего поста, а просмотр всех
    """

    def has_object_permission(self, request, view, news: News):
        if request.method in permissions.SAFE_METHODS:
            return True
        return news.user == request.user