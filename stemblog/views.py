""" Manifest from Nikita Olegovich
    Документация к Django на русском https://django.fun/ru/docs/django/4.1/ (Чтобы перейти по ссылке нажмите на нее с зажатым Ctrl)
    По возничшим вопросом обращаться к Nikita Olegovich

    Файл views.py  используется для написания представлений( логическая часть сайта).
    Чтобы вызвать представление, нам нужно сопоставить его с URL - и для этого нам нужен URLconf(urls.py). URL прописывается как путь к функции/классу.
    def welcoming(request): Выводин на главный экран приветствие.
    def converter(request): Производит рассчет валют.
    def views_news(request, news_id): показывает пост по его id
    def all_news(request): Вы водит все новости
    def crate_news(request): Принимает введенные значения и сохраняет их в базу данных
"""
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponseNotAllowed, HttpResponseNotFound
from stemblog import models
import requests
from faker import Faker
# from django.db.models import Q


def faker_create_user(request):
    f = Faker('ru_RU')
    for i in range(10):

        p = f.profile()
        User.objects.create(
            username=p['username'],
            email=p['mail'],
            password=f.password()
        )
    return redirect('/')



# функция приветсвия
# При нажатии на на кнопку "Stem" вызывается эта функция
def welcoming(request):
    # Присваиваем переменной "name" Имя пользователя
    name = 'mr.Stem'

    # Сохраняем переменную "name" как значение в словарь по ключу "name7"
    # Ключ "name7" используем для HTML-шаблона
    context = {
        'name7': name
    }

    # Возвращаем в заданный шаблон('front/home.html') и обеденяем с заданным словарем(context=context)
    return render(request=request, template_name='front/home.html', context=context)


# Напишем функцию для работы конвертера
def converter(request):
    # Здесь записываем в переменную словарь с данными валют по отношению к 1 доллару(USD)
    response = requests.get(url='https://api.exchangerate-api.com/v4/latest/USD').json()
    currencies = response.get('rates')

    # Создаем проверку методов запроса
    # GET-запрос — метод передачи данных от клиента к серверу с целью получения информации, указанной с помощью конкретных GET-параметров.
    # Это публичные данные, доступные при повторном просмотре ссылки в истории. Такой запрос актуально использовать при неизменных данных в адресной строке.
    if request.method == 'GET':
        context = {
            'currencies': currencies
        }
        # Возвращаем шаблон конвертера
        return render(request=request, template_name='front/converter.html', context=context)


    # Если же метод запроса POST, прописываем логику
    # Метод запроса POST предназначен для направления запроса, при котором веб-сервер принимает данные, заключённые в тело сообщения, для хранения.
    # Он часто используется для загрузки файла или представления заполненной веб-формы. В отличие от него, метод HTTP GET предназначен для получения информации от сервера.
    if request.method == 'POST':

        # Сохраняем в переменные введенные данные с шаблонв по ключам( ключи указаны в скобках)
        from_amount = float(request.POST.get('from-amount'))
        from_curr = request.POST.get('from-curr')
        to_curr = request.POST.get('to-curr')

        # Проводим вычисления
        converted_amount = round((currencies[to_curr] / currencies[from_curr]) * float(from_amount), 2)

        # Создаем словарь для хранения  { "ключ": значение }
        context = {
            'from_curr': from_curr,
            'to_curr': to_curr,
            'from_amount': from_amount,
            'currencies': currencies,
            'converted_amount': converted_amount
        }
        # Возвращаем шаблон конвертера
        return render(request=request, template_name='front/converter.html', context=context)


# Создаем фукцию показа поста
def views_news(request, news_id):
    try:
        user_post = models.News.objects.get(id=news_id)
        author = user_post.user.username

        return render(request, template_name='front/views_news.html', context={'news': user_post,'author':author })
    except models.News.DoesNotExist:
         return HttpResponseNotFound(request)


# Создаем функцию вывода сохраненных данных из базы данных на шаблон
def all_news(request):

    if request.GET.get('search'):
        str_search = request.GET['search']
        #news_object_all = models.News.objects.filter(Q(title__contains=str_search) | Q(content__contains=str_search))
        news_object_all = list(models.News.objects.filter(title__contains=str_search))
        news_object_all += list(models.News.objects.filter(content__contains=str_search).exclude(title__contains=str_search))
    else:
    # Обращаемся к обьектам классса модели News и выводим все в переменную
        news_object_all = models.News.objects.all()

    # Передаем переменную в словарь как значение по ключу, в шаблоне с помощью цкла выводим эти значения
    return render(request=request, template_name='front/news.html', context={'news': news_object_all, 'str_search': request.GET.get('search', '')},)


#Создаем функцию создания новости и сохранение данных в базу данных с шаблона
def crate_news(request):

    # Проверяем методы обращения к серверу
    if request.method == 'GET':
        return render(request=request, template_name='front/create_news.html')

    # Если в шаблона ввели данные, перехватывем и сохраняем в переменные
    elif request.method == 'POST':
        print(request.POST)
        title = request.POST.get('title') or ''
        content = request.POST.get('content') or ''

        # Проверяем все ли поля заполнены и сохраняем введеные значения в базу данных
        if title and content:

            # Обращаемся к классу и и сохраняем их по значению
            models.News(title=title, content=content, user=request.user).save()

            # Возвращаем главную страницу
            return redirect('/')

        # Если данные введены не все, то выводим ошибку и возвращаем шаблон
        else:

            # Текст указывающий на ошибку
            error = 'Укажите все поля'
            return render(request=request, template_name='front/create_news.html', context={'title': title, 'content': content, 'error': error})


def update_news(request, news_id):
    update_news_id = models.News.objects.get(id=news_id)

    # Проверяем методы обращения к серверу
    if request.method == 'GET':
        return render(request=request, template_name='front/create_news.html',
                      context={'title': update_news_id.title, 'content': update_news_id.content, 'delete': True, 'news_id': news_id})

    # Если в шаблона ввели данные, перехватывем и сохраняем в переменные
    elif request.method == 'POST':

        title = request.POST.get('title') or ''
        content = request.POST.get('content') or ''

        # Проверяем все ли поля заполнены и сохраняем введеные значения в базу данных
        if title and content:
            update_fields = []
            # Обращаемся к классу и и сохраняем их по значению
            if update_news_id.title != title:
                update_fields.append('title')
                update_news_id.title = title

            if update_news_id.title != content:
                update_fields.append('content')
                update_news_id.title = content

            update_news_id.save(update_fields=update_fields or None)

            # Возвращаем главную страницу
            return redirect('/news')

        # Если данные введены не все, то выводим ошибку и возвращаем шаблон
        else:

            # Текст указывающий на ошибку
            error = 'Укажите все поля'
            return render(request=request, template_name='front/create_news.html',
                          context={'title': title, 'content': content, 'error': error, 'delete': True, 'news_id': news_id})


def news_delete(request, news_id):

    if request.method == 'POST':
        ty_news_delete = models.News.objects.get(id=news_id)
        ty_news_delete.delete()
        return redirect('/news')
    else:
        return HttpResponseNotAllowed(request)


def profile(request, user_name):
    try:
        user_profile = models.Profile.objects.get(user__username=user_name)
        news_user = models.News.objects.filter(user__username=user_name)
        return render(request=request, template_name='registration/profile.html', context={'user': user_profile, 'news':news_user })
    except (User.DoesNotExist, models.Profile.DoesNotExist):
        return redirect('home')
