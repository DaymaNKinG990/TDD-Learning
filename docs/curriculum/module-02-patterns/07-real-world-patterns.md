# 🌍 Паттерны в реальном мире: анализ популярных Python библиотек

## 🎯 Цели урока

После изучения этого урока вы сможете:
- ✅ Распознавать паттерны проектирования в реальных библиотеках и фреймворках
- ✅ Понимать мотивацию выбора конкретных паттернов в production-коде
- ✅ Анализировать архитектурные решения в open-source проектах
- ✅ Применять найденные решения в собственных проектах

## 📚 Введение

Изучив теорию паттернов проектирования, важно увидеть, как они применяются в реальных проектах. В этом уроке мы проанализируем использование паттернов в популярных Python библиотеках и поймем, почему разработчики выбрали именно эти решения.

### 💡 Простыми словами

**Аналогия**: Изучение архитектуры зданий
- Теория = чертежи и правила
- Практика = реальные здания (Django, FastAPI, SQLAlchemy)
- Анализ = понимание, почему архитектор выбрал именно это решение

**В программировании:**
- Изучаем код популярных библиотек
- Видим, как паттерны решают реальные проблемы
- Учимся применять те же решения в своих проектах

### 📊 Визуализация паттернов в библиотеках

```mermaid
graph TB
    A[Популярные библиотеки] --> B[Django<br/>Singleton, Factory]
    A --> C[FastAPI<br/>Dependency Injection]
    A --> D[SQLAlchemy<br/>Factory, Adapter]
    A --> E[Pydantic<br/>Builder, Strategy]
    A --> F[Requests<br/>Adapter, Facade]
    
    B --> G[Settings<br/>Logger]
    C --> H[Depends<br/>Роутеры]
    D --> I[Engine<br/>ORM]
    E --> J[Валидация<br/>Модели]
    F --> K[HTTP<br/>Сессии]
    
    style A fill:#4dabf7
```

---

## 🏭 Creational Patterns в действии

### 🔧 Singleton Pattern

#### Django Settings
**Где:** `django.conf.settings`
**Зачем:** Глобальный доступ к настройкам приложения

```python
# Упрощенная версия из Django
class LazySettings:
    def __init__(self):
        self._wrapped = None

    def _setup(self):
        # Настройка выполняется только один раз
        if self._wrapped is None:
            settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
            self._wrapped = Settings(settings_module)

    def __getattr__(self, name):
        if self._wrapped is None:
            self._setup()
        return getattr(self._wrapped, name)

# Глобальный экземпляр
settings = LazySettings()
```

**Почему именно Singleton:**
- **Единая точка конфигурации** для всего приложения
- **Ленивая загрузка** - настройки читаются только при первом обращении
- **Предотвращение конфликтов** - все модули используют одни настройки

#### logging.getLogger()
**Где:** Стандартная библиотека Python
**Зачем:** Управление логгерами по именам

```python
import logging

# Возвращает тот же экземпляр для одного имени
logger1 = logging.getLogger('myapp')
logger2 = logging.getLogger('myapp')
print(logger1 is logger2)  # True

# Внутри используется словарь для хранения экземпляров
class LoggerDict(dict):
    def __getitem__(self, key):
        if key not in self:
            self[key] = Logger(key)
        return super().__getitem__(key)
```

**Почему Singleton подходит:**
- **Избежание дублирования** логгеров с одним именем
- **Централизованное управление** конфигурацией логирования
- **Иерархическая структура** логгеров

### 🏗 Factory Pattern

#### SQLAlchemy Engine
**Где:** `sqlalchemy.create_engine()`
**Зачем:** Создание подключений к разным типам БД

```python
# SQLAlchemy использует Factory для создания Engine
def create_engine(url, **kwargs):
    strategy = strategies.DefaultEngineStrategy()
    return strategy.create(*args, **kwargs)

class DefaultEngineStrategy:
    def create(self, name_or_url, **kwargs):
        # Определяет тип БД из URL
        u = url.make_url(name_or_url)
        
        if u.drivername == 'postgresql':
            return PostgreSQLEngine(u, **kwargs)
        elif u.drivername == 'mysql':
            return MySQLEngine(u, **kwargs)
        elif u.drivername == 'sqlite':
            return SQLiteEngine(u, **kwargs)

# Использование
engine = create_engine('postgresql://user:pass@localhost/db')
```

**Преимущества Factory в SQLAlchemy:**
- **Абстракция создания** - клиент не знает о конкретных классах Engine
- **Расширяемость** - легко добавить поддержку новых БД
- **Унифицированный интерфейс** для разных типов баз данных

#### requests.Session
**Где:** `requests.Session()`
**Зачем:** Фабрика для HTTP-сессий с переиспользованием соединений

```python
class Session:
    def __init__(self):
        self.adapters = {}
        self.mount('https://', HTTPAdapter())
        self.mount('http://', HTTPAdapter())
    
    def mount(self, prefix, adapter):
        """Регистрация адаптеров для разных протоколов"""
        self.adapters[prefix] = adapter
    
    def get_adapter(self, url):
        """Factory Method для выбора адаптера"""
        for prefix, adapter in self.adapters.items():
            if url.startswith(prefix):
                return adapter

# Автоматический выбор адаптера
session = Session()
response = session.get('https://api.github.com')  # Использует HTTPS адаптер
```

### 🧱 Builder Pattern

#### Django ORM QuerySet
**Где:** Django QuerySet API
**Зачем:** Пошаговое построение SQL-запросов

```python
# Django QuerySet использует Fluent Builder
class QuerySet:
    def __init__(self, model):
        self.model = model
        self._filters = []
        self._order_by = []
        self._limit = None
    
    def filter(self, **kwargs):
        new_qs = self._clone()
        new_qs._filters.append(kwargs)
        return new_qs
    
    def order_by(self, *fields):
        new_qs = self._clone()
        new_qs._order_by = list(fields)
        return new_qs
    
    def limit(self, n):
        new_qs = self._clone()
        new_qs._limit = n
        return new_qs

# Fluent interface в действии
users = User.objects.filter(age__gte=18).order_by('-created_at')[:10]
```

**Почему Builder подходит Django ORM:**
- **Читаемость** - код выглядит как естественный язык
- **Гибкость** - можно комбинировать условия в любом порядке
- **Ленивость** - SQL не выполняется до фактического использования

#### SQLAlchemy Query Builder
**Где:** SQLAlchemy Core
**Зачем:** Построение сложных SQL-запросов

```python
from sqlalchemy import select, and_, or_

# Builder для SQL-запросов
query = (select([users.c.name, users.c.email])
         .where(and_(users.c.age >= 18, 
                     users.c.active == True))
         .order_by(users.c.name)
         .limit(10))
```

---

## 🔗 Structural Patterns в действии

### 🔌 Adapter Pattern

#### Django Database Backends
**Где:** Django database backends
**Зачем:** Унификация интерфейса для разных БД

```python
# Django адаптирует разные DB-API к единому интерфейсу
class BaseDatabaseWrapper:
    def __init__(self, settings_dict):
        self.settings_dict = settings_dict
    
    def connect(self):
        # Переопределяется в конкретных адаптерах
        raise NotImplementedError()

class PostgreSQLWrapper(BaseDatabaseWrapper):
    def connect(self):
        import psycopg2
        return psycopg2.connect(**self.connection_params)

class MySQLWrapper(BaseDatabaseWrapper):
    def connect(self):
        import MySQLdb
        return MySQLdb.connect(**self.connection_params)

# Django скрывает различия между БД
connection = connections['default']  # Может быть любая БД
cursor = connection.cursor()
cursor.execute("SELECT * FROM users")
```

**Зачем нужен Adapter:**
- **Единый интерфейс** для разных библиотек БД
- **Изоляция изменений** - замена БД не затрагивает основной код
- **Совместимость** с различными DB-API драйверами

#### requests.adapters
**Где:** HTTP адаптеры в requests
**Зачем:** Адаптация разных протоколов и транспортов

```python
class HTTPAdapter:
    def send(self, request, **kwargs):
        """Адаптирует urllib3 к интерфейсу requests"""
        conn = self.get_connection(request.url)
        return conn.urlopen(method=request.method, 
                           url=request.url, 
                           body=request.body)

# Пользовательские адаптеры
class TimeoutHTTPAdapter(HTTPAdapter):
    def send(self, request, timeout=None, **kwargs):
        # Добавляет логику таймаутов
        return super().send(request, timeout=timeout or 10, **kwargs)
```

### 🎨 Decorator Pattern

#### Django Middleware
**Где:** Django middleware система
**Зачем:** Добавление функциональности к обработке запросов

```python
# Django middleware работает как цепочка декораторов
class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Обработка до view
        request = self.process_request(request)
        
        response = self.get_response(request)
        
        # Обработка после view
        response = self.process_response(request, response)
        return response
    
    def process_response(self, request, response):
        response['X-Frame-Options'] = 'DENY'
        return response

# Middleware как декораторы
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
]
```

**Преимущества Decorator в Django:**
- **Модульность** - каждый middleware отвечает за одну функцию
- **Переиспользование** - middleware можно применять к любому проекту
- **Порядок выполнения** - важен порядок в списке MIDDLEWARE

#### Python @functools.wraps
**Где:** Стандартная библиотека Python
**Зачем:** Сохранение метаданных декорируемых функций

```python
import functools

def my_decorator(func):
    @functools.wraps(func)  # Decorator для Decorator!
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(name):
    """Greets a person"""
    return f"Hello, {name}!"

print(greet.__name__)  # 'greet' (без @wraps было бы 'wrapper')
print(greet.__doc__)   # 'Greets a person'
```

### 🏢 Facade Pattern

#### Django ORM
**Где:** Django Model API
**Зачем:** Упрощение работы с базой данных

```python
# Django ORM скрывает сложность SQL за простым API
class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    
    @classmethod
    def get_active_users(cls):
        # Facade скрывает сложные SQL-запросы
        return cls.objects.filter(is_active=True).prefetch_related('profile')

# Простое использование сложной функциональности
users = User.get_active_users()  # Вместо сложного SQL

# Внутри Django выполняет:
# SELECT * FROM users WHERE is_active = TRUE;
# SELECT * FROM profiles WHERE user_id IN (...);
```

**Зачем Facade в ORM:**
- **Скрытие сложности SQL** - разработчики работают с Python-объектами
- **Автоматическая оптимизация** - ORM генерирует эффективные запросы
- **Переносимость** - один код работает с разными БД

#### requests library
**Где:** Публичный API requests
**Зачем:** Упрощение HTTP-запросов

```python
# requests.get() - это Facade над сложной HTTP-машинерией
def get(url, **kwargs):
    # Facade создает Session, настраивает адаптеры, 
    # обрабатывает cookies, redirects, encoding и т.д.
    with Session() as session:
        return session.request('GET', url, **kwargs)

# Простое использование
response = requests.get('https://api.github.com/users/octocat')

# Вместо:
# session = Session()
# adapter = HTTPAdapter()
# request = PreparedRequest()
# request.prepare(method='GET', url='...', headers=headers, ...)
# response = adapter.send(request)
```

---

## 🎭 Behavioral Patterns в действии

### 👁 Observer Pattern

#### Django Signals
**Где:** Django signals система
**Зачем:** Уведомление о событиях в приложении

```python
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

# Django использует Observer для уведомлений о событиях модели
@receiver(post_save, sender=User)
def user_created_handler(sender, instance, created, **kwargs):
    if created:
        # Отправка welcome email
        send_welcome_email(instance.email)
        
        # Создание профиля пользователя
        Profile.objects.create(user=instance)
        
        # Логирование
        logger.info(f"New user created: {instance.email}")

# Signals отправляются автоматически при сохранении
user = User.objects.create(email='test@example.com')  
# Автоматически вызывается user_created_handler
```

**Преимущества Observer в Django:**
- **Слабая связанность** - обработчики не знают о существовании друг друга
- **Расширяемость** - легко добавить новые обработчики
- **Модульность** - каждый обработчик в отдельном файле/приложении

#### asyncio Event Loop
**Где:** Python asyncio
**Зачем:** Обработка асинхронных событий

```python
import asyncio

# asyncio.Event работает как Observer
async def waiter(event):
    print('Ожидание события...')
    await event.wait()
    print('Событие произошло!')

async def setter(event):
    await asyncio.sleep(2)
    event.set()  # Уведомляет всех наблюдателей
    print('Событие установлено')

# Несколько наблюдателей могут ждать одно событие
async def main():
    event = asyncio.Event()
    
    await asyncio.gather(
        waiter(event),
        waiter(event),  # Второй наблюдатель
        setter(event)
    )
```

### 🎯 Strategy Pattern

#### Django Storage Backends
**Где:** Django file storage
**Зачем:** Разные способы хранения файлов

```python
# Django использует Strategy для разных способов хранения файлов
class FileSystemStorage:
    def save(self, name, content):
        # Сохранение в локальную файловую систему
        with open(self.path(name), 'wb') as f:
            f.write(content.read())
        return name

class S3Storage:
    def save(self, name, content):
        # Сохранение в Amazon S3
        self.bucket.upload_fileobj(content, name)
        return name

# В settings.py можно переключить стратегию
DEFAULT_FILE_STORAGE = 'myapp.storage.S3Storage'

# Код остается одинаковым
def upload_file(request):
    from django.core.files.storage import default_storage
    storage = default_storage  # Strategy выбирается из настроек
    filename = storage.save('uploads/file.pdf', request.FILES['file'])
```

**Зачем Strategy в Django Storage:**
- **Гибкость деплоя** - локальная разработка, S3 в продакшене
- **Переключение без изменения кода** - через настройки
- **Расширяемость** - легко добавить новые хранилища

#### logging formatters
**Где:** Python logging
**Зачем:** Разные форматы логов

```python
import logging

# Strategy для форматирования логов
class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            'timestamp': record.created,
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module
        })

class SimpleFormatter(logging.Formatter):
    def format(self, record):
        return f"{record.levelname}: {record.getMessage()}"

# Выбор стратегии форматирования
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())  # или SimpleFormatter()
```

### 🔗 Chain of Responsibility Pattern

#### Django Middleware (опять!)
**Где:** Django middleware система
**Зачем:** Последовательная обработка запросов

```python
# Middleware в Django образуют цепочку ответственности
class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Пытаемся аутентифицировать пользователя
        if self.authenticate(request):
            request.user = self.get_user(request)
        else:
            request.user = AnonymousUser()
        
        # Передаем дальше по цепочке
        return self.get_response(request)

class PermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Проверяем права доступа
        if not request.user.has_perm(request.path):
            return HttpResponseForbidden()
        
        # Передаем дальше
        return self.get_response(request)
```

#### logging.Handler hierarchy
**Где:** Python logging
**Зачем:** Иерархическая обработка логов

```python
# Логгеры образуют цепочку ответственности
root_logger = logging.getLogger()  # Корневой логгер
app_logger = logging.getLogger('myapp')  # Логгер приложения
module_logger = logging.getLogger('myapp.module')  # Логгер модуля

# Сообщение проходит по цепочке: module -> app -> root
module_logger.error("Something went wrong")

# Каждый логгер может обработать или передать дальше
class CustomHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            # Обрабатываем ошибки
            send_to_monitoring(record)
        # Остальное передаем дальше (через parent logger)
```

### 🏛 Template Method Pattern

#### Django Generic Views
**Где:** Django Class-Based Views
**Зачем:** Общий алгоритм с кастомизацией деталей

```python
class ListView:
    """Template Method для отображения списков объектов"""
    
    def get(self, request):
        # Общий алгоритм (Template Method)
        queryset = self.get_queryset()      # Хук 1
        queryset = self.filter_queryset(queryset)  # Хук 2
        context = self.get_context_data(queryset)  # Хук 3
        return self.render_to_response(context)     # Хук 4
    
    def get_queryset(self):
        # Абстрактный метод - должен быть переопределен
        raise NotImplementedError()
    
    def filter_queryset(self, queryset):
        # Хук с реализацией по умолчанию
        return queryset
    
    def get_context_data(self, queryset):
        return {'object_list': queryset}

# Конкретная реализация
class UserListView(ListView):
    def get_queryset(self):
        return User.objects.filter(is_active=True)
    
    def filter_queryset(self, queryset):
        # Кастомная фильтрация
        search = self.request.GET.get('search')
        if search:
            return queryset.filter(name__icontains=search)
        return queryset
```

**Преимущества Template Method в Django:**
- **Переиспользование логики** - общий алгоритм в базовом классе
- **Кастомизация** - переопределение только нужных частей
- **Консистентность** - все view следуют одному шаблону

---

## 📊 Архитектурные паттерны

### 🏗 MVC в Django

Django использует модификацию MVC - паттерн MVT (Model-View-Template):

```python
# Model - данные и бизнес-логика
class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    def get_absolute_url(self):
        return reverse('article-detail', kwargs={'pk': self.pk})

# View - контроллер (в Django терминологии)
class ArticleDetailView(DetailView):
    model = Article
    template_name = 'article_detail.html'

# URLs - маршрутизация (дополнительный слой)
urlpatterns = [
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article-detail'),
]
```

**Template - представление** (`article_detail.html`):

```html
<h1>{{ article.title }}</h1>
<p>{{ article.content }}</p>
```

**Преимущества MVT в Django:**
- **Разделение ответственностей** - данные, логика, представление
- **Переиспользование** - одна модель, много представлений
- **Тестируемость** - каждый слой тестируется отдельно

### 🔌 Dependency Injection в Flask

Flask использует DI через свою систему расширений:

```python
# Flask-SQLAlchemy использует DI паттерн
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()  # Зависимость

def create_app():
    app = Flask(__name__)
    db.init_app(app)  # Внедрение зависимости
    return app

# Тестирование с подменой зависимостей
def test_create_app():
    test_db = SQLAlchemy()  # Тестовая база
    app = Flask(__name__)
    test_db.init_app(app)   # Внедряем тестовую зависимость
```

---

## 🔍 Анализ выбора паттернов

### Почему именно эти паттерны?

#### Django выбрал Observer (Signals) потому что:
- **Веб-приложения событийно-ориентированные** - много событий (создание пользователя, покупка, комментарий)
- **Модульность** - разные приложения могут реагировать на события
- **Расширяемость** - плагины могут подписаться на события

#### SQLAlchemy использует Strategy для движков БД потому что:
- **Множество СУБД** с разными особенностями
- **Единый интерфейс** для разных баз
- **Оптимизации** специфичные для каждой СУБД

#### requests применяет Adapter потому что:
- **Стандартизация HTTP** - разные транспорты, один интерфейс
- **Расширяемость** - пользователи могут добавить свои адаптеры
- **Тестирование** - mock-адаптеры для тестов

### Антипаттерны, которые избежали

#### Django НЕ использует Singleton для моделей потому что:
- **Конфликты при тестировании** - состояние переносится между тестами
- **Многопоточность** - проблемы с race conditions
- **Масштабируемость** - узкие места в высоконагруженных системах

#### Flask НЕ использует глобальные фабрики потому что:
- **Тестируемость** - сложно подменять зависимости
- **Изоляция** - разные приложения должны быть независимы
- **Конфигурация** - разные настройки для разных экземпляров

---

## 🎯 Практические рекомендации

### Как выбирать паттерны как в популярных библиотеках

#### 1. Анализируйте домен

Если много событий - используйте Observer:

```python
# Django: пользователь создан, заказ оплачен, файл загружен
from django.dispatch import Signal

user_created = Signal()
order_paid = Signal()
file_uploaded = Signal()

# Обработчики подписываются на события
user_created.connect(send_welcome_email)
order_paid.connect(update_inventory)
```

Если много стратегий - используйте Strategy:

```python
# SQLAlchemy: PostgreSQL, MySQL, SQLite, Oracle
from sqlalchemy import create_engine

# Разные стратегии для разных БД
postgres_engine = create_engine('postgresql://...')
mysql_engine = create_engine('mysql://...')
sqlite_engine = create_engine('sqlite:///...')
```

Если сложное создание - используйте Factory/Builder:

```python
# requests: разные адаптеры, настройки, аутентификация
from requests import Session
from requests.adapters import HTTPAdapter

session = Session()
adapter = HTTPAdapter(max_retries=3)
session.mount('https://', adapter)
```

#### 2. Думайте о расширяемости
```python
# Хорошо: пользователи могут добавить свои стратегии
class CustomStorage(BaseStorage):
    def save(self, name, content):
        # Пользовательская логика
        pass

# Плохо: жестко зашитые варианты
if storage_type == 'filesystem':
    # ...
elif storage_type == 's3':
    # ...
# Нельзя добавить новый тип
```

#### 3. Учитывайте тестирование
```python
# Хорошо: зависимости можно подменить
def send_email(message, sender=None):
    sender = sender or get_email_sender()  # DI
    sender.send(message)

# В тестах
mock_sender = MockEmailSender()
send_email("test", sender=mock_sender)

# Плохо: жестко зашитые зависимости
def send_email(message):
    smtp = smtplib.SMTP('localhost')  # Нельзя подменить в тестах
    smtp.send(message)
```

### Паттерны для разных типов приложений

#### Web Applications (Django, Flask, FastAPI)
- **Observer** для событий (пользователи, заказы)
- **Strategy** для разных способов оплаты, хранения
- **Template Method** для обработки запросов
- **Decorator** для middleware, аутентификации

#### CLI Applications (Click, argparse)
- **Command** для операций
- **Chain of Responsibility** для обработки аргументов
- **Factory** для создания команд

#### Data Processing (pandas, NumPy)
- **Iterator** для обработки больших данных
- **Strategy** для разных алгоритмов
- **Template Method** для pipelines

#### API Clients (requests, httpx)
- **Adapter** для разных протоколов
- **Facade** для упрощения API
- **Builder** для сложных запросов

---

## 🧪 Тестирование паттернов

### Как популярные библиотеки тестируют паттерны

#### Django тестирует Signals (Observer)
```python
# Django создает временные обработчики для тестов
from django.test import TestCase
from django.db.models.signals import post_save

class SignalTest(TestCase):
    def test_user_created_signal(self):
        called = []
        
        def handler(sender, **kwargs):
            called.append(kwargs['instance'])
        
        # Временно подключаем обработчик
        post_save.connect(handler, sender=User)
        
        user = User.objects.create(email='test@example.com')
        
        self.assertEqual(len(called), 1)
        self.assertEqual(called[0], user)
        
        # Отключаем обработчик
        post_save.disconnect(handler, sender=User)
```

#### requests тестирует Adapters
```python
# requests использует mock-адаптеры для тестов
import requests
from requests.adapters import HTTPAdapter
from requests import Session

class MockAdapter(HTTPAdapter):
    def __init__(self, response_text):
        super().__init__()
        self.response_text = response_text
    
    def send(self, request, **kwargs):
        response = Response()
        response._content = self.response_text.encode()
        response.status_code = 200
        return response

# В тестах подменяем адаптер
def test_api_call():
    session = Session()
    session.mount('http://test.com', MockAdapter('{"result": "ok"}'))
    
    response = session.get('http://test.com/api')
    assert response.json() == {"result": "ok"}
```

#### SQLAlchemy тестирует Strategy (Engine)
```python
# SQLAlchemy тестирует каждый тип Engine
class TestEngineStrategy:
    def test_postgresql_engine(self):
        engine = create_engine('postgresql://test')
        assert isinstance(engine.dialect, PostgreSQLDialect)
    
    def test_sqlite_engine(self):
        engine = create_engine('sqlite:///test.db')
        assert isinstance(engine.dialect, SQLiteDialect)
    
    def test_custom_engine(self):
        # Тестирование пользовательских Engine
        engine = create_engine('custom://test', strategy=MyCustomStrategy)
        assert isinstance(engine, MyCustomEngine)
```

---

## 📈 Performance и паттерны

### Как паттерны влияют на производительность

#### Observer может быть медленным
```python
# Django оптимизирует signals через weak references
from django.dispatch import Signal

# Плохо: держим сильные ссылки на обработчики
signal = Signal()
handlers = []  # Обработчики не удаляются из памяти

# Хорошо: weak references в Django
signal.connect(handler, weak=True)  # По умолчанию weak=True
```

#### Strategy может кэшироваться
```python
# SQLAlchemy кэширует стратегии
_strategies_cache = {}

def get_strategy(name):
    if name not in _strategies_cache:
        _strategies_cache[name] = create_strategy(name)
    return _strategies_cache[name]
```

#### Singleton может быть узким местом
```python
# Плохо: все потоки конкурируют за один объект
class DatabaseConnection:  # Singleton
    def query(self, sql):
        with self._lock:  # Блокировка на каждый запрос
            return self._connection.execute(sql)

# Хорошо: пул соединений вместо Singleton
class ConnectionPool:
    def get_connection(self):
        return self._pool.get()  # Без глобальной блокировки
```

---

## 🎓 Заключение и выводы

### Что мы узнали из анализа популярных библиотек

1. **Паттерны решают реальные проблемы** - каждый паттерн в production-коде имеет четкую мотивацию

2. **Контекст важнее теории** - один и тот же паттерн может применяться по-разному в зависимости от задач

3. **Простота превосходит сложность** - популярные библиотеки избегают over-engineering

4. **Тестируемость критична** - выбор паттерна часто зависит от удобства тестирования

5. **Производительность имеет значение** - паттерны должны масштабироваться

### Рекомендации для ваших проектов

#### ✅ Делайте как популярные библиотеки:
- **Анализируйте домен** перед выбором паттерна
- **Думайте о расширяемости** и плагинах
- **Проектируйте для тестирования**
- **Измеряйте производительность**
- **Документируйте архитектурные решения**

#### ❌ Избегайте типичных ошибок:
- Не применяйте паттерны "потому что модно"
- Не усложняйте простые решения
- Не игнорируйте производительность
- Не забывайте о тестировании

### Дальнейшее изучение

1. **Читайте код популярных библиотек** - лучший способ увидеть паттерны в действии
2. **Анализируйте мотивацию** - почему выбран именно этот паттерн?
3. **Экспериментируйте** - попробуйте разные подходы к одной задаче
4. **Тестируйте паттерны** - проверяйте как они ведут себя под нагрузкой

---

## 🚀 Следующие шаги

!!! success "Что вы узнали"
    - ✅ Как паттерны применяются в Django, FastAPI, SQLAlchemy
    - ✅ Почему разработчики выбирают конкретные паттерны
    - ✅ Как анализировать архитектурные решения в open-source
    - ✅ Примеры из реальных production-проектов

!!! tip "Практика"
    Откройте исходный код своей любимой библиотеки и найдите применение паттернов. Попробуйте понять, почему был выбран именно этот паттерн.

Теперь вы готовы к **[Практике паттернов](08-patterns-practice.md)** - создадим реальные проекты с применением паттернов!

!!! info "Дополнительные ресурсы"
    - [Django source code](https://github.com/django/django) - отличные примеры паттернов
    - [SQLAlchemy source](https://github.com/sqlalchemy/sqlalchemy) - сложные архитектурные решения
    - [Requests source](https://github.com/psf/requests) - простота и элегантность
    - [Flask source](https://github.com/pallets/flask) - минимализм и расширяемость








