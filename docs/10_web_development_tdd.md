# TDD в веб-разработке

## 🎯 Применение TDD в веб-проектах

Веб-разработка представляет уникальные вызовы для TDD: HTTP запросы, базы данных, пользовательские интерфейсы, аутентификация. В этой главе мы рассмотрим как эффективно применять TDD при создании веб-приложений на Python.

## 🌐 Архитектура веб-приложения для TDD

### Слоистая архитектура

```python
# Структура проекта для TDD
webapp/
├── domain/              # Бизнес-логика (ядро)
│   ├── models.py       # Доменные модели
│   ├── services.py     # Бизнес-сервисы
│   └── repositories.py # Интерфейсы репозиториев
├── infrastructure/     # Внешние зависимости
│   ├── database.py     # Реализация БД
│   ├── email.py        # Email сервис
│   └── storage.py      # Файловое хранилище
├── web/                # Веб-слой
│   ├── api/           # REST API
│   ├── views.py       # Представления
│   └── forms.py       # Формы
└── tests/
    ├── unit/          # Unit тесты
    ├── integration/   # Интеграционные тесты
    └── e2e/          # End-to-end тесты
```

## 🔥 TDD с Flask

### Проект: API блога

#### Итерация 1: Создание поста

##### 🔴 RED: Тест модели

```python
# tests/unit/test_models.py
import pytest
from datetime import datetime
from domain.models import Post, User

def test_create_post():
    """Создание поста с заголовком и содержимым."""
    author = User(email="author@example.com", name="Author")
    post = Post(
        title="Test Post", 
        content="Test content",
        author=author
    )
    
    assert post.title == "Test Post"
    assert post.content == "Test content"
    assert post.author == author
    assert isinstance(post.created_at, datetime)
    assert post.slug == "test-post"

def test_post_requires_title():
    """Пост требует заголовок."""
    author = User(email="author@example.com", name="Author")
    
    with pytest.raises(ValueError, match="Title is required"):
        Post(title="", content="Content", author=author)
```

##### 🟢 GREEN: Модель Post

```python
# domain/models.py
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
import re

@dataclass
class User:
    email: str
    name: str
    id: Optional[int] = None

@dataclass  
class Post:
    title: str
    content: str
    author: User
    id: Optional[int] = None
    created_at: datetime = None
    slug: str = None
    
    def __post_init__(self):
        if not self.title.strip():
            raise ValueError("Title is required")
        
        if self.created_at is None:
            self.created_at = datetime.now()
        
        if self.slug is None:
            self.slug = self._generate_slug(self.title)
    
    def _generate_slug(self, title: str) -> str:
        """Генерация URL slug из заголовка."""
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
```

#### Итерация 2: Сервис для блога

##### 🔴 RED: Тест сервиса

```python
# tests/unit/test_blog_service.py
import pytest
from unittest.mock import Mock
from domain.services import BlogService
from domain.models import Post, User

@pytest.fixture
def mock_post_repository():
    return Mock()

@pytest.fixture
def blog_service(mock_post_repository):
    return BlogService(post_repository=mock_post_repository)

def test_create_post_service(blog_service, mock_post_repository):
    """Сервис создания поста."""
    author = User(email="author@example.com", name="Author")
    mock_post_repository.save.return_value = Post(
        title="Test Post",
        content="Test content", 
        author=author,
        id=1
    )
    
    post = blog_service.create_post(
        title="Test Post",
        content="Test content",
        author=author
    )
    
    assert post.id == 1
    mock_post_repository.save.assert_called_once()

def test_get_posts_by_author(blog_service, mock_post_repository):
    """Получение постов по автору."""
    author = User(email="author@example.com", name="Author")
    expected_posts = [
        Post(title="Post 1", content="Content 1", author=author),
        Post(title="Post 2", content="Content 2", author=author)
    ]
    mock_post_repository.find_by_author.return_value = expected_posts
    
    posts = blog_service.get_posts_by_author(author)
    
    assert len(posts) == 2
    assert posts == expected_posts
    mock_post_repository.find_by_author.assert_called_once_with(author)
```

##### 🟢 GREEN: Сервис блога

```python
# domain/services.py
from typing import List
from domain.models import Post, User

class BlogService:
    """Сервис для работы с блогом."""
    
    def __init__(self, post_repository):
        self.post_repository = post_repository
    
    def create_post(self, title: str, content: str, author: User) -> Post:
        """Создание нового поста."""
        post = Post(title=title, content=content, author=author)
        return self.post_repository.save(post)
    
    def get_posts_by_author(self, author: User) -> List[Post]:
        """Получение постов автора."""
        return self.post_repository.find_by_author(author)
    
    def get_all_posts(self) -> List[Post]:
        """Получение всех постов."""
        return self.post_repository.find_all()
    
    def get_post_by_slug(self, slug: str) -> Post:
        """Получение поста по slug."""
        return self.post_repository.find_by_slug(slug)
```

#### Итерация 3: Flask API

##### 🔴 RED: Тест API

```python
# tests/integration/test_blog_api.py
import pytest
import json
from web.app import create_app

@pytest.fixture
def app():
    """Создание Flask приложения для тестов."""
    app = create_app({
        'TESTING': True,
        'DATABASE_URL': 'sqlite:///:memory:'
    })
    
    with app.app_context():
        from infrastructure.database import db
        db.create_all()
        yield app

@pytest.fixture
def client(app):
    """Тестовый клиент."""
    return app.test_client()

@pytest.fixture
def auth_headers():
    """Заголовки авторизации."""
    return {
        'Authorization': 'Bearer test-token',
        'Content-Type': 'application/json'
    }

def test_create_post_api(client, auth_headers):
    """Тест создания поста через API."""
    post_data = {
        'title': 'Test Post',
        'content': 'This is test content for the post.'
    }
    
    response = client.post(
        '/api/posts',
        data=json.dumps(post_data),
        headers=auth_headers
    )
    
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data['title'] == 'Test Post'
    assert response_data['slug'] == 'test-post'
    assert 'id' in response_data

def test_get_posts_api(client):
    """Тест получения списка постов."""
    response = client.get('/api/posts')
    
    assert response.status_code == 200
    posts = json.loads(response.data)
    assert isinstance(posts, list)

def test_get_post_by_slug_api(client, auth_headers):
    """Тест получения поста по slug."""
    # Сначала создаем пост
    post_data = {'title': 'Test Post', 'content': 'Test content'}
    create_response = client.post(
        '/api/posts',
        data=json.dumps(post_data),
        headers=auth_headers
    )
    
    # Получаем пост по slug
    response = client.get('/api/posts/test-post')
    
    assert response.status_code == 200
    post = json.loads(response.data)
    assert post['title'] == 'Test Post'
    assert post['slug'] == 'test-post'

def test_create_post_unauthorized(client):
    """Тест создания поста без авторизации."""
    post_data = {'title': 'Test Post', 'content': 'Test content'}
    
    response = client.post(
        '/api/posts',
        data=json.dumps(post_data),
        headers={'Content-Type': 'application/json'}
    )
    
    assert response.status_code == 401
```

##### 🟢 GREEN: Flask API

```python
# web/app.py
from flask import Flask, request, jsonify, g
from domain.services import BlogService
from infrastructure.database import db, PostRepository
from web.auth import require_auth, get_current_user

def create_app(config=None):
    app = Flask(__name__)
    
    if config:
        app.config.update(config)
    
    db.init_app(app)
    
    @app.route('/api/posts', methods=['POST'])
    @require_auth
    def create_post():
        """Создание нового поста."""
        data = request.get_json()
        
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({'error': 'Title and content required'}), 400
        
        blog_service = BlogService(PostRepository(db.session))
        author = get_current_user()
        
        try:
            post = blog_service.create_post(
                title=data['title'],
                content=data['content'],
                author=author
            )
            
            return jsonify({
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'slug': post.slug,
                'created_at': post.created_at.isoformat(),
                'author': {
                    'id': post.author.id,
                    'name': post.author.name
                }
            }), 201
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/posts', methods=['GET'])
    def get_posts():
        """Получение списка постов."""
        blog_service = BlogService(PostRepository(db.session))
        posts = blog_service.get_all_posts()
        
        return jsonify([{
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'created_at': post.created_at.isoformat(),
            'author': {
                'id': post.author.id,
                'name': post.author.name
            }
        } for post in posts])
    
    @app.route('/api/posts/<slug>', methods=['GET'])
    def get_post(slug):
        """Получение поста по slug."""
        blog_service = BlogService(PostRepository(db.session))
        post = blog_service.get_post_by_slug(slug)
        
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        return jsonify({
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'slug': post.slug,
            'created_at': post.created_at.isoformat(),
            'author': {
                'id': post.author.id,
                'name': post.author.name
            }
        })
    
    return app
```

## 🎭 TDD с Django

### Проект: Система задач (TODO)

#### Итерация 1: Модель Task

##### 🔴 RED: Тест модели Django

```python
# tests/test_models.py
import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from tasks.models import Task

@pytest.mark.django_db
class TestTaskModel:
    """Тесты модели Task."""
    
    def test_create_task(self):
        """Создание задачи."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        
        task = Task.objects.create(
            title='Test Task',
            description='Test description',
            owner=user
        )
        
        assert task.title == 'Test Task'
        assert task.description == 'Test description'
        assert task.owner == user
        assert task.status == 'pending'
        assert not task.completed
    
    def test_task_requires_title(self):
        """Задача требует заголовок."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        
        with pytest.raises(ValidationError):
            task = Task(title='', owner=user)
            task.full_clean()
    
    def test_task_complete_method(self):
        """Метод завершения задачи."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        
        task = Task.objects.create(
            title='Test Task',
            owner=user
        )
        
        task.complete()
        
        assert task.completed == True
        assert task.status == 'completed'
        assert task.completed_at is not None
```

##### 🟢 GREEN: Django модель

```python
# tasks/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class Task(models.Model):
    """Модель задачи."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def clean(self):
        """Валидация модели."""
        if not self.title.strip():
            raise ValidationError({'title': 'Title cannot be empty'})
    
    def complete(self):
        """Завершить задачу."""
        self.completed = True
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def reopen(self):
        """Переоткрыть задачу."""
        self.completed = False
        self.status = 'pending'
        self.completed_at = None
        self.save()
```

#### Итерация 2: Views и Forms

##### 🔴 RED: Тест представлений

```python
# tests/test_views.py
import pytest
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from tasks.models import Task

@pytest.mark.django_db
class TestTaskViews:
    """Тесты представлений задач."""
    
    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def client(self):
        return Client()
    
    @pytest.fixture
    def authenticated_client(self, client, user):
        client.login(username='testuser', password='testpass123')
        return client
    
    def test_task_list_view(self, authenticated_client, user):
        """Тест списка задач."""
        # Создаем несколько задач
        Task.objects.create(title='Task 1', owner=user)
        Task.objects.create(title='Task 2', owner=user)
        
        response = authenticated_client.get(reverse('task_list'))
        
        assert response.status_code == 200
        assert 'Task 1' in response.content.decode()
        assert 'Task 2' in response.content.decode()
    
    def test_task_create_view_get(self, authenticated_client):
        """Тест GET запроса создания задачи."""
        response = authenticated_client.get(reverse('task_create'))
        
        assert response.status_code == 200
        assert 'form' in response.context
    
    def test_task_create_view_post(self, authenticated_client, user):
        """Тест POST запроса создания задачи."""
        response = authenticated_client.post(reverse('task_create'), {
            'title': 'New Task',
            'description': 'New task description'
        })
        
        assert response.status_code == 302  # Редирект после создания
        
        # Проверяем что задача создана
        task = Task.objects.get(title='New Task')
        assert task.owner == user
        assert task.description == 'New task description'
    
    def test_task_detail_view(self, authenticated_client, user):
        """Тест детального просмотра задачи."""
        task = Task.objects.create(
            title='Test Task',
            description='Test description',
            owner=user
        )
        
        response = authenticated_client.get(
            reverse('task_detail', kwargs={'pk': task.pk})
        )
        
        assert response.status_code == 200
        assert task.title in response.content.decode()
        assert task.description in response.content.decode()
    
    def test_task_complete_view(self, authenticated_client, user):
        """Тест завершения задачи."""
        task = Task.objects.create(title='Test Task', owner=user)
        
        response = authenticated_client.post(
            reverse('task_complete', kwargs={'pk': task.pk})
        )
        
        assert response.status_code == 302
        
        task.refresh_from_db()
        assert task.completed == True
        assert task.status == 'completed'
    
    def test_unauthorized_access(self, client):
        """Тест неавторизованного доступа."""
        response = client.get(reverse('task_list'))
        assert response.status_code == 302  # Редирект на логин
```

##### 🟢 GREEN: Django views

```python
# tasks/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Task
from .forms import TaskForm

@login_required
def task_list(request):
    """Список задач пользователя."""
    tasks = Task.objects.filter(owner=request.user)
    
    return render(request, 'tasks/list.html', {
        'tasks': tasks
    })

@login_required  
def task_detail(request, pk):
    """Детальный просмотр задачи."""
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    
    return render(request, 'tasks/detail.html', {
        'task': task
    })

@login_required
def task_create(request):
    """Создание новой задачи."""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.save()
            
            messages.success(request, 'Task created successfully!')
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm()
    
    return render(request, 'tasks/create.html', {
        'form': form
    })

@login_required
def task_complete(request, pk):
    """Завершение задачи."""
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        task.complete()
        messages.success(request, f'Task "{task.title}" completed!')
    
    return redirect('task_detail', pk=task.pk)

# tasks/forms.py
from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    """Форма для создания/редактирования задачи."""
    
    class Meta:
        model = Task
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter task description'
            })
        }
    
    def clean_title(self):
        title = self.cleaned_data['title']
        if not title.strip():
            raise forms.ValidationError('Title cannot be empty')
        return title.strip()
```

#### Итерация 3: API Views (Django REST Framework)

##### 🔴 RED: Тест API

```python
# tests/test_api.py
import pytest
import json
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from tasks.models import Task

@pytest.mark.django_db
class TestTaskAPI:
    """Тесты API задач."""
    
    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    @pytest.fixture
    def authenticated_client(self, api_client, user):
        api_client.force_authenticate(user=user)
        return api_client
    
    def test_get_tasks_list(self, authenticated_client, user):
        """Тест получения списка задач."""
        Task.objects.create(title='Task 1', owner=user)
        Task.objects.create(title='Task 2', owner=user)
        
        response = authenticated_client.get('/api/tasks/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
    
    def test_create_task(self, authenticated_client):
        """Тест создания задачи через API."""
        data = {
            'title': 'New API Task',
            'description': 'Created via API'
        }
        
        response = authenticated_client.post('/api/tasks/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New API Task'
        assert 'id' in response.data
        
        # Проверяем что задача создана в БД
        task = Task.objects.get(title='New API Task')
        assert task.description == 'Created via API'
    
    def test_get_task_detail(self, authenticated_client, user):
        """Тест получения детальной информации о задаче."""
        task = Task.objects.create(
            title='Test Task',
            description='Test description',
            owner=user
        )
        
        response = authenticated_client.get(f'/api/tasks/{task.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Test Task'
        assert response.data['description'] == 'Test description'
    
    def test_update_task(self, authenticated_client, user):
        """Тест обновления задачи."""
        task = Task.objects.create(title='Original Title', owner=user)
        
        data = {'title': 'Updated Title', 'description': 'Updated description'}
        response = authenticated_client.put(f'/api/tasks/{task.id}/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Title'
        
        task.refresh_from_db()
        assert task.title == 'Updated Title'
    
    def test_delete_task(self, authenticated_client, user):
        """Тест удаления задачи."""
        task = Task.objects.create(title='To Delete', owner=user)
        
        response = authenticated_client.delete(f'/api/tasks/{task.id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(id=task.id).exists()
    
    def test_unauthorized_access(self, api_client):
        """Тест неавторизованного доступа к API."""
        response = api_client.get('/api/tasks/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

##### 🟢 GREEN: Django REST API

```python
# tasks/serializers.py
from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Task."""
    
    owner = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 
            'completed', 'created_at', 'updated_at', 
            'completed_at', 'owner'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at', 'owner']
    
    def validate_title(self, value):
        """Валидация заголовка."""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value.strip()

class TaskCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания задачи."""
    
    class Meta:
        model = Task
        fields = ['title', 'description']
    
    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value.strip()

# tasks/api_views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer, TaskCreateSerializer

class TaskListCreateView(generics.ListCreateAPIView):
    """Список задач и создание новой задачи."""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детальный просмотр, обновление и удаление задачи."""
    
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_task(request, pk):
    """API для завершения задачи."""
    try:
        task = Task.objects.get(pk=pk, owner=request.user)
    except Task.DoesNotExist:
        return Response(
            {'error': 'Task not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    task.complete()
    serializer = TaskSerializer(task)
    
    return Response(serializer.data)

# tasks/urls.py
from django.urls import path
from . import views, api_views

urlpatterns = [
    # Web views
    path('', views.task_list, name='task_list'),
    path('create/', views.task_create, name='task_create'),
    path('<int:pk>/', views.task_detail, name='task_detail'),
    path('<int:pk>/complete/', views.task_complete, name='task_complete'),
    
    # API views
    path('api/tasks/', api_views.TaskListCreateView.as_view(), name='api_task_list'),
    path('api/tasks/<int:pk>/', api_views.TaskDetailView.as_view(), name='api_task_detail'),
    path('api/tasks/<int:pk>/complete/', api_views.complete_task, name='api_task_complete'),
]
```

## ⚡ TDD с FastAPI

### Проект: User Management API

FastAPI представляет современный подход к созданию API с автоматической валидацией, документацией и высокой производительностью. Рассмотрим TDD для асинхронного API управления пользователями.

#### Итерация 1: Pydantic модели и схемы

##### 🔴 RED: Тест моделей данных

```python
# tests/test_schemas.py
import pytest
from datetime import datetime
from pydantic import ValidationError
from schemas.user import UserCreate, UserResponse, UserUpdate

def test_user_create_schema():
    """Тест схемы создания пользователя."""
    user_data = {
        "email": "test@example.com",
        "password": "securepassword123",
        "name": "Test User"
    }
    
    user = UserCreate(**user_data)
    
    assert user.email == "test@example.com"
    assert user.password == "securepassword123"
    assert user.name == "Test User"

def test_user_create_email_validation():
    """Тест валидации email."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="invalid-email",
            password="password123",
            name="Test User"
        )
    
    assert "value is not a valid email address" in str(exc_info.value)

def test_user_create_password_strength():
    """Тест требований к паролю."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@example.com", 
            password="123",  # слишком короткий
            name="Test User"
        )
    
    assert "Password must be at least 8 characters" in str(exc_info.value)

def test_user_response_excludes_password():
    """Тест что схема ответа не содержит пароль."""
    user_data = {
        "id": 1,
        "email": "test@example.com",
        "name": "Test User",
        "is_active": True,
        "created_at": datetime.now()
    }
    
    user = UserResponse(**user_data)
    
    assert hasattr(user, 'email')
    assert hasattr(user, 'name')
    assert not hasattr(user, 'password')  # пароль не должен быть в ответе

def test_user_update_optional_fields():
    """Тест что в обновлении все поля опциональны."""
    # Пустое обновление должно быть валидным
    update = UserUpdate()
    assert update.email is None
    assert update.name is None
    
    # Частичное обновление должно работать
    update = UserUpdate(name="New Name")
    assert update.name == "New Name"
    assert update.email is None
```

##### 🟢 GREEN: Pydantic схемы

```python
# schemas/user.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator

class UserBase(BaseModel):
    """Базовая схема пользователя."""
    email: EmailStr
    name: str

class UserCreate(UserBase):
    """Схема для создания пользователя."""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserUpdate(BaseModel):
    """Схема для обновления пользователя."""
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('Name cannot be empty')
        return v.strip() if v else v

class UserResponse(UserBase):
    """Схема ответа с данными пользователя."""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # Для совместимости с SQLAlchemy

class UserInDB(UserResponse):
    """Схема пользователя в базе данных."""
    password_hash: str

# schemas/auth.py
from pydantic import BaseModel

class Token(BaseModel):
    """Схема токена аутентификации."""
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    """Схема запроса аутентификации."""
    email: EmailStr
    password: str
```

#### Итерация 2: FastAPI endpoints с dependency injection

##### 🔴 RED: Тест API endpoints

```python
# tests/test_user_api.py
import pytest
from httpx import AsyncClient
from fastapi import status
from main import app

@pytest.fixture
async def async_client():
    """Асинхронный тестовый клиент."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def sample_user_data():
    """Данные тестового пользователя."""
    return {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "name": "Test User"
    }

@pytest.mark.asyncio
async def test_create_user(async_client: AsyncClient, sample_user_data):
    """Тест создания пользователя."""
    response = await async_client.post("/users/", json=sample_user_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    
    user_data = response.json()
    assert user_data["email"] == sample_user_data["email"] 
    assert user_data["name"] == sample_user_data["name"]
    assert "password" not in user_data  # пароль не должен возвращаться
    assert "id" in user_data
    assert user_data["is_active"] == True

@pytest.mark.asyncio
async def test_create_user_duplicate_email(async_client: AsyncClient, sample_user_data):
    """Тест создания пользователя с дублирующимся email."""
    # Создаем первого пользователя
    await async_client.post("/users/", json=sample_user_data)
    
    # Пытаемся создать второго с тем же email
    response = await async_client.post("/users/", json=sample_user_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_users_list(async_client: AsyncClient, sample_user_data):
    """Тест получения списка пользователей."""
    # Создаем пользователей
    await async_client.post("/users/", json=sample_user_data)
    
    user_data_2 = sample_user_data.copy()
    user_data_2["email"] = "user2@example.com"
    await async_client.post("/users/", json=user_data_2)
    
    # Получаем список
    response = await async_client.get("/users/")
    
    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert len(users) == 2
    assert any(user["email"] == sample_user_data["email"] for user in users)

@pytest.mark.asyncio
async def test_get_user_by_id(async_client: AsyncClient, sample_user_data):
    """Тест получения пользователя по ID."""
    # Создаем пользователя
    create_response = await async_client.post("/users/", json=sample_user_data)
    user_id = create_response.json()["id"]
    
    # Получаем пользователя по ID
    response = await async_client.get(f"/users/{user_id}")
    
    assert response.status_code == status.HTTP_200_OK
    user_data = response.json()
    assert user_data["id"] == user_id
    assert user_data["email"] == sample_user_data["email"]

@pytest.mark.asyncio
async def test_get_user_not_found(async_client: AsyncClient):
    """Тест получения несуществующего пользователя."""
    response = await async_client.get("/users/999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "User not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_update_user(async_client: AsyncClient, sample_user_data):
    """Тест обновления пользователя."""
    # Создаем пользователя
    create_response = await async_client.post("/users/", json=sample_user_data)
    user_id = create_response.json()["id"]
    
    # Обновляем имя
    update_data = {"name": "Updated Name"}
    response = await async_client.patch(f"/users/{user_id}", json=update_data)
    
    assert response.status_code == status.HTTP_200_OK
    user_data = response.json()
    assert user_data["name"] == "Updated Name"
    assert user_data["email"] == sample_user_data["email"]  # email не изменился

@pytest.mark.asyncio
async def test_delete_user(async_client: AsyncClient, sample_user_data):
    """Тест удаления пользователя."""
    # Создаем пользователя
    create_response = await async_client.post("/users/", json=sample_user_data)
    user_id = create_response.json()["id"]
    
    # Удаляем пользователя
    response = await async_client.delete(f"/users/{user_id}")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Проверяем что пользователь действительно удален
    get_response = await async_client.get(f"/users/{user_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
```

##### 🟢 GREEN: FastAPI endpoints

```python
# main.py
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.user import UserCreate, UserResponse, UserUpdate
from services.user_service import UserService

app = FastAPI(
    title="User Management API",
    description="TDD example with FastAPI",
    version="1.0.0"
)

security = HTTPBearer()

# Dependency для получения сервиса пользователей
async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """Создание нового пользователя."""
    try:
        user = await user_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.get("/users/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service)
):
    """Получение списка пользователей."""
    users = await user_service.get_users(skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Получение пользователя по ID."""
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@app.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    user_service: UserService = Depends(get_user_service)
):
    """Обновление пользователя."""
    user = await user_service.update_user(user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Удаление пользователя."""
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
```

#### Итерация 3: Async database операции

##### 🔴 RED: Тест сервиса пользователей

```python
# tests/test_user_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from services.user_service import UserService
from schemas.user import UserCreate, UserUpdate
from models.user import User

@pytest.fixture
def mock_db_session():
    """Мок сессии базы данных."""
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def user_service(mock_db_session):
    """Сервис пользователей с мок базой данных."""
    return UserService(mock_db_session)

@pytest.fixture
def sample_user_create():
    """Данные для создания пользователя."""
    return UserCreate(
        email="test@example.com",
        password="testpassword123",
        name="Test User"
    )

@pytest.mark.asyncio
async def test_create_user_success(user_service, mock_db_session, sample_user_create):
    """Тест успешного создания пользователя."""
    # Настраиваем мок - пользователя с таким email нет
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    
    # Мокаем сохранение и возврат созданного пользователя
    created_user = User(
        id=1,
        email=sample_user_create.email,
        name=sample_user_create.name,
        password_hash="hashed_password",
        is_active=True
    )
    mock_db_session.merge.return_value = created_user
    
    result = await user_service.create_user(sample_user_create)
    
    assert result.id == 1
    assert result.email == sample_user_create.email
    assert result.name == sample_user_create.name
    assert result.is_active == True
    
    # Проверяем что был вызван commit
    mock_db_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_create_user_duplicate_email(user_service, mock_db_session, sample_user_create):
    """Тест создания пользователя с дублирующимся email."""
    # Настраиваем мок - пользователь с таким email уже есть
    existing_user = User(
        id=1,
        email=sample_user_create.email,
        name="Existing User",
        password_hash="hash",
        is_active=True
    )
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = existing_user
    
    with pytest.raises(ValueError, match="Email already registered"):
        await user_service.create_user(sample_user_create)

@pytest.mark.asyncio
async def test_get_user_by_id_found(user_service, mock_db_session):
    """Тест получения существующего пользователя по ID."""
    expected_user = User(
        id=1,
        email="test@example.com",
        name="Test User",
        password_hash="hash",
        is_active=True
    )
    mock_db_session.get.return_value = expected_user
    
    result = await user_service.get_user_by_id(1)
    
    assert result == expected_user
    mock_db_session.get.assert_called_once_with(User, 1)

@pytest.mark.asyncio
async def test_get_user_by_id_not_found(user_service, mock_db_session):
    """Тест получения несуществующего пользователя."""
    mock_db_session.get.return_value = None
    
    result = await user_service.get_user_by_id(999)
    
    assert result is None

@pytest.mark.asyncio
async def test_update_user_success(user_service, mock_db_session):
    """Тест успешного обновления пользователя."""
    # Существующий пользователь
    existing_user = User(
        id=1,
        email="old@example.com",
        name="Old Name",
        password_hash="hash",
        is_active=True
    )
    mock_db_session.get.return_value = existing_user
    
    # Данные для обновления
    update_data = UserUpdate(name="New Name", email="new@example.com")
    
    result = await user_service.update_user(1, update_data)
    
    assert result.name == "New Name"
    assert result.email == "new@example.com"
    mock_db_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_delete_user_success(user_service, mock_db_session):
    """Тест успешного удаления пользователя."""
    existing_user = User(id=1, email="test@example.com", name="Test")
    mock_db_session.get.return_value = existing_user
    
    result = await user_service.delete_user(1)
    
    assert result == True
    mock_db_session.delete.assert_called_once_with(existing_user)
    mock_db_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_delete_user_not_found(user_service, mock_db_session):
    """Тест удаления несуществующего пользователя."""
    mock_db_session.get.return_value = None
    
    result = await user_service.delete_user(999)
    
    assert result == False
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()
```

##### 🟢 GREEN: User service

```python
# services/user_service.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from models.user import User
from schemas.user import UserCreate, UserUpdate

class UserService:
    """Сервис для работы с пользователями."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Создание нового пользователя."""
        # Проверяем уникальность email
        existing_user = await self._get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Хэшируем пароль
        password_hash = self.pwd_context.hash(user_data.password)
        
        # Создаем пользователя
        user = User(
            email=user_data.email,
            name=user_data.name,
            password_hash=password_hash,
            is_active=True
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID."""
        return await self.db.get(User, user_id)
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получение списка пользователей."""
        query = select(User).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Обновление пользователя."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Обновляем только переданные поля
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        """Удаление пользователя."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        await self.db.delete(user)
        await self.db.commit()
        
        return True
    
    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email."""
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля."""
        return self.pwd_context.verify(plain_password, hashed_password)

# models/user.py
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

class User(Base):
    """Модель пользователя."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    password_hash: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
```

#### Итерация 4: JWT аутентификация

##### 🔴 RED: Тест аутентификации

```python
# tests/test_auth.py
import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from datetime import datetime, timedelta

from services.auth_service import AuthService
from services.user_service import UserService
from schemas.auth import LoginRequest
from models.user import User

@pytest.fixture
def mock_user_service():
    return AsyncMock(spec=UserService)

@pytest.fixture
def auth_service(mock_user_service):
    return AuthService(mock_user_service, secret_key="test_secret")

@pytest.fixture
def test_user():
    return User(
        id=1,
        email="test@example.com",
        name="Test User",
        password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        is_active=True,
        created_at=datetime.now()
    )

@pytest.mark.asyncio
async def test_authenticate_user_success(auth_service, mock_user_service, test_user):
    """Тест успешной аутентификации пользователя."""
    mock_user_service._get_user_by_email.return_value = test_user
    mock_user_service.verify_password.return_value = True
    
    login_data = LoginRequest(email="test@example.com", password="secret")
    
    result = await auth_service.authenticate_user(login_data)
    
    assert result == test_user
    mock_user_service._get_user_by_email.assert_called_once_with("test@example.com")
    mock_user_service.verify_password.assert_called_once_with("secret", test_user.password_hash)

@pytest.mark.asyncio 
async def test_authenticate_user_wrong_email(auth_service, mock_user_service):
    """Тест аутентификации с неверным email."""
    mock_user_service._get_user_by_email.return_value = None
    
    login_data = LoginRequest(email="wrong@example.com", password="secret")
    
    result = await auth_service.authenticate_user(login_data)
    
    assert result is None

@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(auth_service, mock_user_service, test_user):
    """Тест аутентификации с неверным паролем."""
    mock_user_service._get_user_by_email.return_value = test_user
    mock_user_service.verify_password.return_value = False
    
    login_data = LoginRequest(email="test@example.com", password="wrongpassword")
    
    result = await auth_service.authenticate_user(login_data)
    
    assert result is None

@pytest.mark.asyncio
async def test_create_access_token(auth_service, test_user):
    """Тест создания access token."""
    token = await auth_service.create_access_token(test_user)
    
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Декодируем токен и проверяем payload
    payload = auth_service._decode_token(token)
    assert payload["sub"] == str(test_user.id)
    assert payload["email"] == test_user.email
    assert "exp" in payload

@pytest.mark.asyncio
async def test_get_current_user_valid_token(auth_service, mock_user_service, test_user):
    """Тест получения текущего пользователя по валидному токену."""
    token = await auth_service.create_access_token(test_user)
    mock_user_service.get_user_by_id.return_value = test_user
    
    result = await auth_service.get_current_user(token)
    
    assert result == test_user
    mock_user_service.get_user_by_id.assert_called_once_with(test_user.id)

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(auth_service, mock_user_service):
    """Тест с невалидным токеном."""
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.get_current_user("invalid_token")
    
    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_get_current_user_expired_token(auth_service, mock_user_service, test_user):
    """Тест с истекшим токеном."""
    # Создаем токен с истекшим временем
    expired_token = auth_service._create_token(
        data={"sub": str(test_user.id), "email": test_user.email},
        expires_delta=timedelta(seconds=-1)  # уже истек
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.get_current_user(expired_token)
    
    assert exc_info.value.status_code == 401
```

##### 🟢 GREEN: Auth service и endpoints

```python
# services/auth_service.py
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
import jwt
from passlib.context import CryptContext

from models.user import User
from schemas.auth import LoginRequest
from services.user_service import UserService

class AuthService:
    """Сервис аутентификации."""
    
    def __init__(self, user_service: UserService, secret_key: str):
        self.user_service = user_service
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
    
    async def authenticate_user(self, login_data: LoginRequest) -> Optional[User]:
        """Аутентификация пользователя."""
        user = await self.user_service._get_user_by_email(login_data.email)
        if not user:
            return None
        
        if not self.user_service.verify_password(login_data.password, user.password_hash):
            return None
        
        return user
    
    async def create_access_token(self, user: User) -> str:
        """Создание access token."""
        data = {
            "sub": str(user.id),
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        }
        
        return jwt.encode(data, self.secret_key, algorithm=self.algorithm)
    
    async def get_current_user(self, token: str) -> User:
        """Получение текущего пользователя по токену."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = int(payload.get("sub"))
            if user_id is None:
                raise credentials_exception
        except (jwt.PyJWTError, ValueError):
            raise credentials_exception
        
        user = await self.user_service.get_user_by_id(user_id)
        if user is None:
            raise credentials_exception
        
        return user
    
    def _decode_token(self, token: str) -> dict:
        """Вспомогательный метод для декодирования токена (для тестов)."""
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
    
    def _create_token(self, data: dict, expires_delta: timedelta) -> str:
        """Вспомогательный метод создания токена с кастомным временем жизни."""
        data["exp"] = datetime.utcnow() + expires_delta
        return jwt.encode(data, self.secret_key, algorithm=self.algorithm)

# Добавляем в main.py новые endpoints
from fastapi.security import HTTPBearer
from services.auth_service import AuthService
from schemas.auth import LoginRequest, Token

# Dependency для auth service
async def get_auth_service(
    user_service: UserService = Depends(get_user_service)
) -> AuthService:
    return AuthService(user_service, secret_key="your-secret-key")

# Dependency для получения текущего пользователя
async def get_current_user(
    token: str = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    return await auth_service.get_current_user(token.credentials)

@app.post("/auth/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Аутентификация пользователя."""
    user = await auth_service.authenticate_user(login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = await auth_service.create_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Получение информации о текущем пользователе."""
    return current_user

# Защищаем существующие endpoints
@app.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),  # Требуем аутентификации
    user_service: UserService = Depends(get_user_service)
):
    """Обновление пользователя (только для аутентифицированных)."""
    # Пользователь может обновлять только свои данные
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = await user_service.update_user(user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
```

### FastAPI + pytest-asyncio конфигурация

```python
# conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from main import app
from database import get_db
from models.user import Base

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop():
    """Создание event loop для всей сессии тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Тестовый движок базы данных."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Удаляем таблицы после тестов
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def test_session(test_engine):
    """Тестовая сессия базы данных."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session

@pytest.fixture
async def test_client(test_session):
    """Тестовый HTTP клиент."""
    # Переопределяем dependency базы данных
    app.dependency_overrides[get_db] = lambda: test_session
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Очищаем переопределения
    app.dependency_overrides.clear()

# pytest.ini
[tool:pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --tb=short
    -v
markers = 
    asyncio: marks tests as async
```

## 🔧 Полезные паттерны для веб-TDD

### 1. Page Object Pattern для E2E тестов

```python
# tests/page_objects.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:
    """Page Object для страницы логина."""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def open(self):
        self.driver.get("http://localhost:8000/login")
        return self
    
    def login(self, username, password):
        username_field = self.wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = self.driver.find_element(By.NAME, "password")
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        
        username_field.send_keys(username)
        password_field.send_keys(password)
        submit_button.click()
        
        return TaskListPage(self.driver)

class TaskListPage:
    """Page Object для списка задач."""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def create_task(self, title, description=""):
        create_button = self.wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Create Task"))
        )
        create_button.click()
        
        return TaskCreatePage(self.driver).fill_form(title, description)
    
    def get_task_titles(self):
        task_elements = self.driver.find_elements(By.CSS_SELECTOR, ".task-title")
        return [element.text for element in task_elements]

# tests/e2e/test_task_flow.py
import pytest
from selenium import webdriver
from tests.page_objects import LoginPage

@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()

def test_complete_task_flow(driver, live_server):
    """E2E тест полного потока работы с задачами."""
    # Логин
    task_page = (LoginPage(driver)
                 .open()
                 .login("testuser", "testpass123"))
    
    # Создание задачи
    task_page.create_task("E2E Test Task", "Created via E2E test")
    
    # Проверяем что задача появилась в списке
    tasks = task_page.get_task_titles()
    assert "E2E Test Task" in tasks
```

### 2. Factory Pattern для тестовых данных

```python
# tests/factories.py
import factory
from django.contrib.auth.models import User
from tasks.models import Task

class UserFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания пользователей."""
    
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

class TaskFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания задач."""
    
    class Meta:
        model = Task
    
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('text')
    owner = factory.SubFactory(UserFactory)
    status = 'pending'

# Использование в тестах
def test_task_with_factory():
    """Тест с использованием фабрики."""
    user = UserFactory(username='specificuser')
    task = TaskFactory(owner=user, title='Specific Task')
    
    assert task.owner.username == 'specificuser'
    assert task.title == 'Specific Task'
```

### 3. Миксины для тестов

```python
# tests/mixins.py
from django.contrib.auth.models import User
from rest_framework.test import APIClient

class AuthenticatedTestMixin:
    """Миксин для тестов с аутентификацией."""
    
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

class TaskTestMixin:
    """Миксин для тестов с задачами."""
    
    def create_task(self, **kwargs):
        defaults = {
            'title': 'Test Task',
            'description': 'Test description',
            'owner': self.user
        }
        defaults.update(kwargs)
        return Task.objects.create(**defaults)

# Использование миксинов
class TestTaskAPI(AuthenticatedTestMixin, TaskTestMixin, TestCase):
    
    def test_create_task(self):
        response = self.client.post('/api/tasks/', {
            'title': 'New Task',
            'description': 'New description'
        })
        
        self.assertEqual(response.status_code, 201)
```

## 🎯 Следующие шаги

В следующей главе мы рассмотрим продвинутые техники TDD: BDD, архитектурные тесты, тестирование производительности.

## 🚀 Интерактивная практика

### 🌐 Flask API с TDD

Готовы создать полноценный RESTful API? Разработайте TODO API используя принципы TDD:

**[🎯 Интерактивное упражнение: Flask API с TDD](exercises/10_flask_api_tdd.md)**

В этом упражнении вы:
- Создадите полноценный RESTful API с CRUD операциями
- Освоите архитектурные паттерны (Repository, Service, Model)
- Изучите валидацию данных и обработку ошибок
- Протестируете все HTTP методы и статус коды
- Поработаете с edge cases и продвинутыми сценариями

Это упражнение покажет, как TDD помогает создавать надежные и хорошо структурированные веб-API!

## 🧪 Проверьте свои знания

<div class="quiz-container" id="web-development-tdd-quiz">
<script type="application/json">
{
  "title": "TDD в веб-разработке",
  "description": "Проверьте понимание применения TDD при разработке веб-приложений",
  "icon": "🌐",
  "questions": [
    {
      "question": "Какие слои обычно выделяют в веб-приложении для эффективного TDD?",
      "type": "multiple",
      "options": [
        {"text": "Domain (бизнес-логика)", "correct": true},
        {"text": "Infrastructure (внешние зависимости)", "correct": true},
        {"text": "Web (HTTP слой)", "correct": true},
        {"text": "Database (схема БД)", "correct": false},
        {"text": "Frontend (HTML/CSS/JS)", "correct": false}
      ],
      "explanation": "В TDD-friendly архитектуре выделяют Domain (ядро), Infrastructure (БД, email, etc.) и Web (API, views). Database и Frontend не являются отдельными слоями в этой архитектуре.",
      "points": 2
    },
    {
      "question": "Что тестируется в интеграционных тестах веб-API?",
      "type": "multiple",
      "options": [
        {"text": "HTTP статус коды", "correct": true},
        {"text": "JSON сериализация/десериализация", "correct": true},
        {"text": "Валидация входных данных", "correct": true},
        {"text": "Стилизация HTML страниц", "correct": false},
        {"text": "JavaScript функциональность", "correct": false}
      ],
      "explanation": "Интеграционные тесты API проверяют HTTP статусы, JSON обработку и валидацию. Стилизация и JS функциональность тестируются отдельно.",
      "points": 2
    },
    {
      "question": "Какой паттерн лучше использовать для тестирования Flask приложений?",
      "type": "single",
      "code": "# Вариант A: Прямое тестирование функций\napp = create_app()\nwith app.test_client() as client:\n    response = client.get('/api/users')\n\n# Вариант B: Тестирование через pytest fixtures\n@pytest.fixture\ndef client(app):\n    return app.test_client()\n\ndef test_api_endpoint(client):\n    response = client.get('/api/users')",
      "options": [
        {"text": "Вариант A - прямое тестирование", "correct": false},
        {"text": "Вариант B - через pytest fixtures", "correct": true},
        {"text": "Оба варианта одинаково хороши", "correct": false},
        {"text": "Ни один из вариантов не подходит", "correct": false}
      ],
      "explanation": "Pytest fixtures обеспечивают лучшую изоляцию, переиспользование и читаемость тестов по сравнению с прямым созданием test_client.",
      "points": 1
    },
    {
      "question": "Какие аспекты важно тестировать при работе с JWT токенами?",
      "type": "multiple",
      "options": [
        {"text": "Валидность токена", "correct": true},
        {"text": "Истечение срока действия", "correct": true},
        {"text": "Payload содержимое", "correct": true},
        {"text": "Длина токена в символах", "correct": false},
        {"text": "Цвет интерфейса логина", "correct": false}
      ],
      "explanation": "Для JWT важно тестировать валидность, expiration и payload. Длина токена и UI аспекты не относятся к безопасности токенов.",
      "points": 2
    },
    {
      "question": "Что такое Test Double в контексте веб-API тестирования?",
      "type": "single",
      "options": [
        {"text": "Дублирование тестовых данных", "correct": false},
        {"text": "Замена реальных зависимостей фейковыми объектами", "correct": true},
        {"text": "Создание двух копий одного теста", "correct": false},
        {"text": "Тестирование на двух разных серверах", "correct": false}
      ],
      "explanation": "Test Double - это общий термин для заменителей реальных объектов в тестах (Mock, Stub, Fake, etc.) для изоляции тестируемого кода.",
      "points": 1
    },
    {
      "question": "Какой подход лучше для тестирования веб-приложений с TDD?",
      "type": "single",
      "options": [
        {"text": "Сначала пишем E2E тесты, потом разбираем на unit тесты", "correct": false},
        {"text": "Начинаем с domain логики (unit тесты), затем API, потом E2E", "correct": true},
        {"text": "Пишем все типы тестов параллельно", "correct": false},
        {"text": "Фокусируемся только на UI тестах", "correct": false}
      ],
      "explanation": "В TDD для веб-приложений лучше начинать с domain логики (unit тесты), затем добавлять API тесты и наконец E2E тесты. Это обеспечивает пирамиду тестов.",
      "points": 2
    }
  ]
}
</script>
</div>

---

**Следующая глава:** [Продвинутые техники TDD](11_advanced_tdd.md)

*🌐 Веб-приложения под контролем — изучаем продвинутые техники!*
