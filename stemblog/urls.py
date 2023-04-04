"""
Все URLconf представлены как обьекты списка urlpatterns
Задаются в виде:
    path('Имя в адресной строке/', views.(имя функции), name='имя для передачи в шаблон'

"""
from django.urls import path    #
from stemblog import views      # Импортируем наши представления для указания пути


urlpatterns = [
    path('', views.welcoming, name='home'),             # ВЫзываем функцию привествия
    path('news/', views.all_news, name='news'),         # Вызываем функцию вывода новостей новостей
    path('converter/', views.converter, name='convert'),# Вызываем функцию конвертера валют
    path('crete/', views.crate_news, name='create_news'),   # Вызываем функцию создания новости
    # Вызываем функцию показа поста и указываем путь в адресной строке по его id
    path('news/<int:news_id>', views.views_news, name='views_news_id'),
    path('update/<int:news_id>', views.update_news, name='update'),
    path('delete/<int:news_id>', views.news_delete, name='delete'),
    path('profile/<user_name>', views.profile, name='profile'),


    # Для FAKE
    path('fake/users', views.faker_create_user),
    path('fake/news', views.faker_create_news)
]