from rest_framework import serializers
from .models import News


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
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = News
        fields = ('title', 'content', 'date', 'user')
        read_only_fields = ('date', 'user')