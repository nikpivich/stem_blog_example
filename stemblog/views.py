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
import datetime

from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponseNotAllowed, HttpResponseNotFound, Http404

from django.contrib.auth.hashers import make_password
from stemblog import models
import requests
from faker import Faker
from django.db.models import Q
from .forms import NewsForm, NewsModelForms
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404

from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from .serializers import NewsSerializer, NewsModelSerializer, NewsPermission, UserSerializers, UserCreateSerializer
from rest_framework.decorators import api_view
from rest_framework.views import Response, APIView
from rest_framework import status, permissions, generics



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

def faker_create_news(request):
    f = Faker()
    users = User.objects.all()
    for i in users:
        for j in range(10):
            models.News.objects.create(
                title=f.sentence(nb_words=5),
                content=f.sentence(nb_words=100),
                date=f.date_time_between(),
                user=i
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
def create_news(request):
    user_form = NewsModelForms()
    # Проверяем методы обращения к серверу
    if request.method == 'GET':
        return render(request=request, template_name='front/create_news_form.html', context={'form': user_form})

    # Если в шаблона ввели данные, перехватывем и сохраняем в переменные
    elif request.method == 'POST':
        # title = request.POST.get('title') or ''
        # content = request.POST.get('content') or ''

        user_form = NewsForm(request.POST, request.FILES)

        # Проверяем все ли поля заполнены и сохраняем введеные значения в базу данных
        if user_form.is_valid():

            # Обращаемся к классу и и сохраняем их по значению
            models.News.objects.create(
                        title=user_form.cleaned_data['title'],
                        content=user_form.cleaned_data['content'],
                        image=user_form.cleaned_data['image'],
                        user=User.objects.get(username=request.user.username),
                        date=datetime.datetime.now()
                        )

            # Возвращаем главную страницу
            return redirect('/')

        # Если данные введены не все, то выводим ошибку и возвращаем шаблон
        else:

            return render(request=request, template_name='front/create_news_form.html',
                          context={'form': user_form})


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
    print(request.user)
    try:
        user_profile = models.Profile.objects.get(user__username=user_name)
        news_user = models.News.objects.filter(user__username=user_name)

        return render(
            request=request,
            template_name='registration/profile.html',
            context={'user': user_profile, 'news':news_user },

        )
    except (User.DoesNotExist, models.Profile.DoesNotExist):
        return redirect('home')


class NewsCreate(CreateView):
    models = models.News
    form_class = NewsModelForms
    success_url = '/news/{id}'
    template_name = 'front/create_news_form.html'

    def form_valid(self, form):
        news_user= super().form_valid(form)
        self.object.user = self.request.user
        self.object.save()
        return news_user


class NewsUpdate(UpdateView):
    model = models.News
    form_class = NewsModelForms
    success_url = '/news/{id}'
    template_name = 'front/create_news_form.html'


class NewsDelete(DeleteView):
    models = models.News
    success_url = '/'


class NewsShow(ListView):
    model = models.News
    paginate_by = 10
    template_name = 'front/news.html'
    context_object_name = 'news'
    ordering = ('-date',)

    def get_queryset(self):
        if self.request.GET.get('d'):
            date = datetime.datetime.strptime(self.request.GET['d'], '%Y-%m-%d')
            date_to = date + datetime.timedelta(days=1)
            date_query = (Q(date__gte=date) & Q(date__lt=date_to))
        else:
            date_query = Q()

        if self.request.GET.get('s'):
            s = self.request.GET['s']
            q1 = models.News.objects.filter(
                date_query & Q(title__contains=s) & ~Q(content__contains=s)
            ).order_by('-date')
            q2 = models.News.objects.filter(
                date_query & ~Q(title__contains=s) & Q(content__contains=s)
            ).order_by('-date')

            q = q1 | q2

        else:
            q = models.News.objects.filter(date_query).order_by('-date').all().values('id', 'title', 'user', 'date')
            print(q.query)
        return q


@api_view(['GET', 'POST'])
def news_api(request):
    if request.method == 'GET':
        news_ = models.News.objects.all()[:100]
        serializer = NewsModelSerializer(news_, many=True)
        return Response(serializer.data)

    elif request.method == 'POST' and not request.user.is_anonymous:
        serializer = NewsModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'detail': 'not authorized'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'PUT', 'DELETE'])
def news_api_up_del(request, pk):

    try:
        news = models.News.objects.get(id=pk)
    except models.News.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        ser = NewsModelSerializer(news)
        return Response(ser.data)

    elif request.method == 'PUT':
        ser = NewsModelSerializer(news, data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    else:
        news.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NewsViewAPI(APIView):

    def get(self, request):
        news = models.News.objects.all()[:100]
        ser = NewsModelSerializer(news, many=True)
        return Response(ser.data)

    def post(self, request):
        serializer = NewsModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):

        try:
            news = models.News.objects.get(id=pk)
        except models.News.DoesNotExist:
            raise Http404

        ser = NewsModelSerializer(news, data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        news = get_object_or_404(models.News, pk=pk)
        news.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NewsListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = NewsModelSerializer
    queryset = models.News.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

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

class NewsRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.News.objects.all()
    serializer_class = NewsModelSerializer
    permission_classes = [NewsPermission]
    lookup_field = 'id'
    lookup_url_kwarg = 'news_id'

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializers
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


