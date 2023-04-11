from django.contrib import admin
from .models import News, Profile
from django.utils.html import mark_safe
from django.contrib.auth.models import User


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'user', 'user_info', 'link')
    fieldsets = (
        ('Заголовок и дата',{'fields': ('title', )}),
        ('Содержимое', {'fields': ('content', 'user')}),
    )
    ordering = ('-date',)
    search_fields = ('title', 'content')

    list_filter = ('user',)

    def get_queryset(self, request):
        if len(request.GET) == 0:
            return News.objects.none()
        else:
            return super().get_queryset(request)

    @admin.display(description='Номер телефона / Страна')
    def user_info(self, obj: News):
        u = Profile.objects.get(user_id=obj.user.id)
        return mark_safe(f"""
        <li style="color:green;">{u.phone}</li>
        <li style="color:blue;">{u.country}</li>
        """)

    @admin.display(description='Открыть')
    def link(self, obj: News):
        return mark_safe(f'<a href="/news/{obj.id}" target="_blank">Читать</a>')

    # @admin.display(description='Страна')
    # def user_country(self, obj: News):
    #     return Profile.objects.get(user_id=obj.user.id).country


admin.site.unregister(User)

@admin.register(User)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active', 'is_staff', 'user_info', 'news_count',)
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    sortable_by = ('username', 'is_active')
    actions = ['deactivate']


    @admin.display(description='Номер телефона / Страна')
    def user_info(self, user: User):
        u = Profile.objects.get(user_id=user.id)
        return mark_safe(f"""
            <li style="color:green;">{u.phone}</li>
            <li style="color:blue;">{u.country}</li>
            """)

    @admin.display(description="Кол-во Новостей")
    def news_count(self, user: User):
        return News.objects.filter(user_id=user.id).count()

    @admin.action(description='Деактивировать пользователей')
    def deactivate(self, request, queryset):
        print(request, queryset)
        queryset.update(is_active=False)

