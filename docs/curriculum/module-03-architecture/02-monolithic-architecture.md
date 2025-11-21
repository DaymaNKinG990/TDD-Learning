# 🏛 Урок 2: Монолитная архитектура

## 🎯 Цели урока

После изучения этого урока вы сможете:
- ✅ Проектировать монолитные приложения с правильной структурой
- ✅ Понимать преимущества и недостатки монолитного подхода
- ✅ Оптимизировать монолит для высокой производительности
- ✅ Принимать решение о переходе к микросервисам

## 📖 Что такое монолитная архитектура?

!!! quote "Определение монолита"
    **Монолитная архитектура** - это архитектурный стиль, при котором все компоненты приложения объединены в единое целое и развертываются как один процесс.

### 💡 Простыми словами

**Аналогия**: Один большой дом
- Все комнаты (модули) в одном здании
- Одна входная дверь (один процесс)
- Одна система отопления (одна база данных)
- Легко перейти из комнаты в комнату (быстрые вызовы)
- Но если нужно расшириться - нужно строить весь дом заново

**В программировании:**
- Все компоненты в одном приложении
- Одна база данных для всего
- Простое развертывание (один файл)
- Быстрая разработка для MVP

### 📊 Визуализация монолита

```mermaid
graph TB
    A[Монолитное приложение] --> B[UI Layer<br/>Frontend]
    A --> C[Business Logic<br/>Services]
    A --> D[Data Layer<br/>Database]
    
    B --> E[Все в одном<br/>процессе]
    C --> E
    D --> E
    
    E --> F[Простое<br/>развертывание]
    
    style A fill:#51cf66
    style E fill:#ffd43b
    style F fill:#74c0fc
```

### Ключевые характеристики

1. **Единое приложение** - все компоненты в одном codebase
2. **Единая база данных** - общая БД для всех компонентов
3. **Единый процесс** - все работает в одном процессе
4. **Простое развертывание** - один артефакт для развертывания

## 🏗 Структура монолитного приложения

### Типичная структура

```
📁 monolithic-app/
├── 📁 src/
│   ├── 📁 models/          # Модели данных
│   ├── 📁 services/        # Бизнес-логика
│   ├── 📁 controllers/     # HTTP обработчики
│   ├── 📁 repositories/    # Доступ к данным
│   ├── 📁 middleware/      # Промежуточное ПО
│   ├── 📁 utils/          # Утилиты
│   └── 📁 config/         # Конфигурация
├── 📁 tests/
├── 📁 migrations/
├── 📁 docs/
└── 📁 scripts/
```

### Пример на Python (FastAPI)

```python
# models.py
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime)

class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: str
```

```python
# repositories/user_repository.py
from sqlalchemy.orm import Session
from models import User, UserCreate
from typing import Optional, List

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserCreate) -> User:
        hashed_password = self._hash_password(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def _hash_password(self, password: str) -> str:
        # Реальная хэшировка пароля
        return f"hashed_{password}"
```

```python
# services/user_service.py
from repositories.user_repository import UserRepository
from models import User, UserCreate
from typing import Optional, List
import smtplib

class UserService:
    def __init__(self, user_repo: UserRepository, email_service):
        self.user_repo = user_repo
        self.email_service = email_service

    def register_user(self, user_data: UserCreate) -> User:
        # Проверка существования пользователя
        if self.user_repo.get_user_by_email(user_data.email):
            raise ValueError("User with this email already exists")

        if self.user_repo.get_user_by_username(user_data.username):
            raise ValueError("Username already taken")

        # Создание пользователя
        user = self.user_repo.create_user(user_data)

        # Отправка приветственного email
        self.email_service.send_welcome_email(user.email, user.username)

        return user

    def get_user_profile(self, user_id: int) -> Optional[User]:
        return self.user_repo.get_user_by_id(user_id)

    def get_all_users(self, page: int = 1, per_page: int = 20) -> List[User]:
        skip = (page - 1) * per_page
        return self.user_repo.get_all_users(skip=skip, limit=per_page)
```

```python
# infrastructure/email_service.py
class EmailService:
    """Service for sending emails - infrastructure layer component."""
    
    def send_welcome_email(self, email: str, username: str) -> None:
        # Implementation would send actual email via SMTP or email service
        print(f"Sending welcome email to {email} for user {username}")
        # In production: smtp.send_email(...)
```

```python
# controllers/user_controller.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.user_service import UserService
from repositories.user_repository import UserRepository
from infrastructure.email_service import EmailService
from models import UserCreate, UserResponse
from typing import List

router = APIRouter()

def get_db():
    # Dependency для получения сессии БД
    pass

def get_user_service(db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    email_service = EmailService()
    return UserService(user_repo, email_service)

@router.post("/users/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    try:
        db_user = user_service.register_user(user)
        return UserResponse(
            id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            created_at=db_user.created_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users/", response_model=List[UserResponse])
async def get_users(
    page: int = 1,
    per_page: int = 20,
    user_service: UserService = Depends(get_user_service)
):
    users = user_service.get_all_users(page=page, per_page=per_page)
    return [
        UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            created_at=user.created_at.isoformat()
        )
        for user in users
    ]
```

## 🎨 Лучшие практики монолитной архитектуры

### 1. **Четкое разделение ответственности**

```python
# ❌ Плохо: Все в одном классе
class UserManager:
    def create_user(self, user_data):
        # Валидация
        # Сохранение в БД
        # Отправка email
        # Логирование
        pass

# ✅ Хорошо: Разделение на слои
class UserController:
    def create_user(self, request):
        # Только HTTP обработка
        pass

class UserService:
    def create_user(self, user_data):
        # Только бизнес-логика
        pass

class UserRepository:
    def save(self, user):
        # Только доступ к данным
        pass
```

### 2. **Организация по функциональным областям**

```
📁 src/
├── 📁 user_management/
│   ├── 📄 models.py
│   ├── 📄 service.py
│   ├── 📄 repository.py
│   └── 📄 controller.py
├── 📁 product_catalog/
│   ├── 📄 models.py
│   ├── 📄 service.py
│   ├── 📄 repository.py
│   └── 📄 controller.py
└── 📁 order_processing/
    ├── 📄 models.py
    ├── 📄 service.py
    ├── 📄 repository.py
    └── 📄 controller.py
```

### 3. **Использование паттернов**

```python
# Repository Pattern
class OrderRepository:
    def save(self, order):
        pass

    def find_by_id(self, order_id):
        pass

    def find_by_user(self, user_id):
        pass

# Service Layer Pattern
class OrderService:
    def __init__(self, order_repo, payment_service, notification_service):
        self.order_repo = order_repo
        self.payment_service = payment_service
        self.notification_service = notification_service

    def place_order(self, order_data):
        # Оркестрация создания заказа
        pass

# Dependency Injection
class OrderController:
    def __init__(self, order_service):
        self.order_service = order_service
```

### 4. **Обработка ошибок**

```python
# Глобальный обработчик ошибок
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)}
    )

@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

# Кастомные исключения
class UserNotFoundError(Exception):
    pass

class InsufficientFundsError(Exception):
    pass

class OrderService:
    def get_user_orders(self, user_id):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        return self.order_repo.find_by_user(user_id)
```

## ⚡ Оптимизация производительности

### 1. **Кэширование**

```python
from functools import lru_cache
import redis
import json

class CacheService:
    def __init__(self):
        self.redis = redis.Redis()

    def get(self, key: str):
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def set(self, key: str, value, ttl: int = 3600):
        self.redis.setex(key, ttl, json.dumps(value))

class ProductService:
    def __init__(self, product_repo, cache_service):
        self.product_repo = product_repo
        self.cache = cache_service

    @lru_cache(maxsize=100)
    def get_product(self, product_id: int):
        # Кэширование в памяти
        return self.product_repo.find_by_id(product_id)

    def get_popular_products(self):
        cache_key = "popular_products"
        products = self.cache.get(cache_key)

        if not products:
            products = self.product_repo.find_popular()
            self.cache.set(cache_key, products, ttl=1800)  # 30 минут

        return products
```

### 2. **Lazy Loading**

```python
# Модель с lazy loading
class Order:
    def __init__(self, order_id):
        self.order_id = order_id
        self._items = None
        self._user = None

    @property
    def items(self):
        if self._items is None:
            self._items = self._load_items()
        return self._items

    @property
    def user(self):
        if self._user is None:
            self._user = self._load_user()
        return self._user

    def _load_items(self):
        # Загрузка товаров при первом обращении
        pass

    def _load_user(self):
        # Загрузка пользователя при первом обращении
        pass
```

### 3. **Connection Pooling**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Настройка пула соединений
engine = create_engine(
    "postgresql://user:password@localhost/db",
    pool_size=10,        # Размер пула
    max_overflow=20,     # Максимальное переполнение
    pool_timeout=30,     # Таймаут ожидания
    pool_recycle=3600    # Время жизни соединения
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 4. **Асинхронная обработка**

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
import aiohttp

class AsyncService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def process_heavy_task(self, data):
        # Выполнение тяжелой задачи в пуле потоков
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._heavy_computation,
            data
        )

    def _heavy_computation(self, data):
        # Тяжелые вычисления
        return sum(i * i for i in range(data))

    async def fetch_external_data(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()
```

## 🔧 Масштабирование монолита

### 1. **Вертикальное масштабирование**

```python
# Увеличение ресурсов сервера
# - CPU cores
# - RAM
# - Disk I/O
# - Network bandwidth
```

### 2. **Горизонтальное масштабирование**

```python
# Load Balancer + Multiple Instances
# Nginx, HAProxy, AWS ELB

upstream backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. **Database Scaling**

```sql
-- Read Replicas
-- Master-Slave replication
-- Connection pooling
-- Query optimization
-- Indexing strategy
```

### 4. **Кэширование на уровне приложения**

```python
# Multi-level caching strategy
class CacheManager:
    def __init__(self):
        self.l1_cache = {}  # In-memory (fastest)
        self.l2_cache = RedisCache()  # Redis (fast)
        self.l3_cache = DatabaseCache()  # Database (slowest)

    def get(self, key):
        # L1 Cache
        if key in self.l1_cache:
            return self.l1_cache[key]

        # L2 Cache
        value = self.l2_cache.get(key)
        if value:
            self.l1_cache[key] = value  # Promote to L1
            return value

        # L3 Cache (Database)
        value = self.l3_cache.get(key)
        if value:
            self.l2_cache.set(key, value)  # Promote to L2
            self.l1_cache[key] = value     # Promote to L1

        return value
```

## 🚨 Когда монолит становится проблемой?

### Признаки необходимости рефакторинга

1. **Долгое время развертывания** (> 30 минут)
2. **Частые конфликты при слиянии** (> 5 конфликтов в день)
3. **Низкая скорость разработки** новых функций
4. **Проблемы с масштабированием** под нагрузкой
5. **Разные требования** к разным частям системы
6. **Команда > 20 разработчиков**

### Метрики для оценки

```python
class MonolithHealthMetrics:
    @staticmethod
    def deployment_frequency():
        """Частота развертываний"""
        # Идеально: несколько раз в день
        # Проблема: реже раза в неделю
        pass

    @staticmethod
    def lead_time_for_changes():
        """Время от коммита до продакшена"""
        # Идеально: < 1 часа
        # Проблема: > 1 дня
        pass

    @staticmethod
    def change_failure_rate():
        """Процент неудачных развертываний"""
        # Идеально: < 5%
        # Проблема: > 20%
        pass

    @staticmethod
    def team_size_vs_productivity():
        """Продуктивность команды"""
        # Идеально: растет линейно
        # Проблема: падает с ростом команды
        pass
```

## 🎯 Преимущества монолитной архитектуры

### Для стартапов и MVP
✅ **Быстрый запуск** - недели вместо месяцев  
✅ **Простота** - один codebase, одна БД  
✅ **Консистентность** - ACID транзакции  
✅ **Легкость разработки** - нет сетевых вызовов  

### Для небольших команд
✅ **Меньше overhead** - нет микросервисной инфраструктуры  
✅ **Легче отлаживать** - один процесс  
✅ **Простое тестирование** - нет интеграционных тестов  
✅ **Быстрое обучение** - меньше технологий  

### Для простых доменов
✅ **Ясная структура** - все в одном месте  
✅ **Легче поддерживать** - меньше moving parts  
✅ **Быстрые изменения** - нет координации между сервисами  

## 🎮 Практические упражнения

### Упражнение 1: Проектирование монолита

**Задание:** Спроектируйте монолитное приложение для системы управления задачами.

### Упражнение 2: Оптимизация производительности

**Задание:** Оптимизируйте монолитное приложение для высокой нагрузки.

## 🎯 Ключевые выводы

1. **Монолит - отличная стартовая точка** для большинства проектов
2. **Хороший монолит** имеет четкую структуру и разделение ответственности
3. **Масштабирование монолита** возможно, но имеет пределы
4. **Монолит vs Микросервисы** - это не бинарный выбор
5. **Миграция** с монолита на микросервисы должна быть постепенной

## 🚀 Следующие шаги

!!! success "Что вы узнали"
    - ✅ Что такое монолитная архитектура и когда ее использовать
    - ✅ Как правильно структурировать монолитное приложение
    - ✅ Преимущества и недостатки монолитного подхода
    - ✅ Когда стоит переходить от монолита к микросервисам

!!! tip "Практика"
    Создайте простое монолитное приложение (например, TODO-лист) с правильной структурой слоев. Это поможет понять основы организации кода.

Теперь вы готовы изучить **[Микросервисную архитектуру](03-microservices-architecture.md)** - современный подход к созданию масштабируемых систем!

---

!!! tip "Практический совет"
    Даже если планируете микросервисы, начните с хорошо структурированного монолита. Это позволит быстрее получить feedback и лучше понять домен.

!!! info "Дополнительные ресурсы"
    - [Building Microservices by Sam Newman](https://samnewman.io/books/building_microservices/)
    - [Clean Architecture by Robert Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

## 🧪 Проверьте свои знания: Монолитная архитектура

<div class="quiz-container" id="monolithic-architecture-quiz">
<script type="application/json">
{
  "title": "Монолитная архитектура",
  "description": "Проверьте понимание монолитного подхода к разработке",
  "icon": "🏛️",
  "questions": [
    {
      "question": "Что такое монолитная архитектура?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "Приложение, состоящее из независимых сервисов", "correct": false},
        {"text": "Приложение, где все компоненты объединены в единое целое", "correct": true},
        {"text": "Приложение, работающее на одном сервере", "correct": false},
        {"text": "Приложение без базы данных", "correct": false}
      ],
      "explanation": "Монолит - это единое приложение со всеми компонентами в одном codebase"
    },
    {
      "question": "Преимущества монолитной архитектуры:",
      "type": "multiple",
      "points": 2,
      "options": [
        {"text": "Простота развертывания", "correct": true},
        {"text": "Легкость разработки", "correct": true},
        {"text": "Консистентность данных", "correct": true},
        {"text": "Высокая масштабируемость", "correct": false},
        {"text": "Технологическая гибкость", "correct": false}
      ],
      "explanation": "Монолит прост в разработке и развертывании, но имеет ограничения в масштабировании"
    },
    {
      "question": "Как масштабировать монолитное приложение?",
      "type": "multiple",
      "points": 2,
      "options": [
        {"text": "Вертикальное масштабирование (больше ресурсов)", "correct": true},
        {"text": "Горизонтальное масштабирование (несколько экземпляров)", "correct": true},
        {"text": "Read replicas для базы данных", "correct": true},
        {"text": "Разделение на микросервисы", "correct": false},
        {"text": "Использование разных технологий", "correct": false}
      ],
      "explanation": "Монолит можно масштабировать, но есть естественные пределы"
    },
    {
      "question": "Признаки того, что монолит становится проблемой:",
      "type": "multiple",
      "points": 2,
      "options": [
        {"text": "Долгое время развертывания", "correct": true},
        {"text": "Частые конфликты при слиянии кода", "correct": true},
        {"text": "Команда больше 20 разработчиков", "correct": true},
        {"text": "Использование разных технологий", "correct": false},
        {"text": "Высокая нагрузка", "correct": false}
      ],
      "explanation": "Эти признаки указывают на необходимость рассмотрения микросервисной архитектуры"
    },
    {
      "question": "Как организовать код в монолитном приложении?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "Все в одном файле", "correct": false},
        {"text": "По функциональным областям (services, controllers, models)", "correct": true},
        {"text": "По алфавиту", "correct": false},
        {"text": "Случайным образом", "correct": false}
      ],
      "explanation": "Хороший монолит имеет четкую организацию кода по ответственностям"
    },
    {
      "question": "Что такое 'Repository Pattern' в монолитной архитектуре?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "Способ хранения кода в Git", "correct": false},
        {"text": "Паттерн для абстракции доступа к данным", "correct": true},
        {"text": "Паттерн для создания репозиториев Docker", "correct": false},
        {"text": "Способ организации файловой системы", "correct": false}
      ],
      "explanation": "Repository Pattern абстрагирует работу с данными от бизнес-логики"
    },
    {
      "question": "Как оптимизировать производительность монолитного приложения?",
      "type": "multiple",
      "points": 2,
      "options": [
        {"text": "Использование кэширования", "correct": true},
        {"text": "Connection pooling для базы данных", "correct": true},
        {"text": "Асинхронная обработка", "correct": true},
        {"text": "Разделение на микросервисы", "correct": false},
        {"text": "Использование разных языков программирования", "correct": false}
      ],
      "explanation": "Монолит можно оптимизировать стандартными методами"
    },
    {
      "question": "Когда монолитная архитектура - лучший выбор?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "Для стартапов и MVP", "correct": true},
        {"text": "Для систем с миллионами пользователей", "correct": false},
        {"text": "Для команд из 100+ разработчиков", "correct": false},
        {"text": "Для систем с жесткими требованиями к latency", "correct": false}
      ],
      "explanation": "Монолит идеален для быстрого старта и MVP проектов"
    }
  ]
}
</script>
</div>

## 💻 Практическое задание: Проектирование монолитного приложения

{{ create_exercise_form(
    "monolithic_design",
    "Проектирование монолитного приложения для системы управления контентом",
    "Спроектируйте монолитное приложение для системы управления контентом (CMS) с правильной архитектурой, оптимизацией производительности и готовностью к будущему масштабированию.",
    """# Задание: Проектирование монолитного CMS

Создайте архитектуру монолитного приложения для системы управления контентом со следующими требованиями:

## Бизнес-требования

### Функциональность:
- **Управление контентом**: Создание, редактирование, публикация статей
- **Категории и теги**: Организация контента
- **Пользователи**: Авторизация, роли (админ, редактор, автор)
- **Комментарии**: Система комментариев к статьям
- **SEO**: Метатеги, URL slugs, sitemap
- **Аналитика**: Просмотры, популярность статей

### Технические требования:
- **Язык**: Python + FastAPI
- **База данных**: PostgreSQL
- **Кэширование**: Redis
- **Поиск**: Elasticsearch (опционально)
- **Файлы**: Локальное хранение или S3
- **Тестирование**: Полный coverage
- **Документация**: Автоматическая генерация API docs

## Архитектурные требования

### Структура приложения:
```
📁 cms-monolith/
├── 📁 src/
│   ├── 📁 api/           # HTTP API слой
│   ├── 📁 core/          # Бизнес-логика
│   ├── 📁 infrastructure/ # Внешние зависимости
│   ├── 📁 domain/        # Доменные модели
│   └── 📁 shared/        # Общие компоненты
├── 📁 tests/
├── 📁 migrations/
└── 📁 docs/
```

### Принципы проектирования:
1. **SOLID принципы** - правильное разделение ответственности
2. **Domain-Driven Design** - моделирование домена
3. **Clean Architecture** - независимость от фреймворков
4. **Repository Pattern** - абстракция данных
5. **CQRS Pattern** - разделение чтения и записи (опционально)

## Задачи для реализации

### 1. Доменные модели (Domain Models)

```python
# TODO: Создайте доменные модели
class Article:
    '''Доменная модель статьи'''
    def __init__(self, title: str, content: str, author_id: int):
        self.id: Optional[int] = None
        self.title = title
        self.content = content
        self.slug = self._generate_slug(title)
        self.author_id = author_id
        self.status = ArticleStatus.DRAFT
        self.created_at = datetime.utcnow()
        self.published_at: Optional[datetime] = None
        self.tags: List[Tag] = []
        self.category: Optional[Category] = None

    def publish(self) -> None:
        '''Бизнес-логика публикации'''
        if self.status != ArticleStatus.DRAFT:
            raise ValueError("Only draft articles can be published")

        self.status = ArticleStatus.PUBLISHED
        self.published_at = datetime.utcnow()

        # Генерация событий (Event Sourcing)
        # TODO: Добавить генерацию доменных событий

    def _generate_slug(self, title: str) -> str:
        '''Генерация URL-friendly slug'''
        # TODO: Реализовать генерацию slug
        pass

class User:
    '''Доменная модель пользователя'''
    def __init__(self, email: str, username: str):
        self.id: Optional[int] = None
        self.email = email
        self.username = username
        self.role = UserRole.AUTHOR
        self.is_active = True
        self.created_at = datetime.utcnow()

class Comment:
    '''Доменная модель комментария'''
    def __init__(self, content: str, article_id: int, author_id: int):
        self.id: Optional[int] = None
        self.content = content
        self.article_id = article_id
        self.author_id = author_id
        self.created_at = datetime.utcnow()
        self.is_moderated = False

# TODO: Создайте перечисления
class ArticleStatus:
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class UserRole:
    ADMIN = "admin"
    EDITOR = "editor"
    AUTHOR = "author"
```

### 2. Репозитории (Repository Pattern)

```python
# TODO: Создайте абстракции репозиториев
class IArticleRepository(ABC):
    @abstractmethod
    def save(self, article: Article) -> Article:
        pass

    @abstractmethod
    def find_by_id(self, article_id: int) -> Optional[Article]:
        pass

    @abstractmethod
    def find_by_author(self, author_id: int) -> List[Article]:
        pass

    @abstractmethod
    def find_published(self, page: int = 1, per_page: int = 20) -> List[Article]:
        pass

    @abstractmethod
    def search(self, query: str) -> List[Article]:
        pass

# TODO: Реализуйте SQLAlchemy репозиторий
class SQLArticleRepository(IArticleRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, article: Article) -> Article:
        # TODO: Сохранить статью в БД
        pass

    def find_by_id(self, article_id: int) -> Optional[Article]:
        # TODO: Найти статью по ID
        pass

    # TODO: Реализовать остальные методы

# TODO: Создайте репозитории для User и Comment
```

### 3. Сервисы (Service Layer)

```python
# TODO: Создайте сервисы бизнес-логики
class ArticleService:
    def __init__(self, article_repo: IArticleRepository, user_repo, event_publisher):
        self.article_repo = article_repo
        self.user_repo = user_repo
        self.event_publisher = event_publisher

    def create_article(self, title: str, content: str, author_id: int) -> Article:
        '''Создание новой статьи'''
        # TODO: Валидация данных
        # TODO: Создание статьи
        # TODO: Публикация события
        pass

    def publish_article(self, article_id: int, user_id: int) -> Article:
        '''Публикация статьи'''
        # TODO: Проверка прав пользователя
        # TODO: Изменение статуса статьи
        # TODO: Публикация события
        pass

    def search_articles(self, query: str, page: int = 1) -> List[Article]:
        '''Поиск статей'''
        # TODO: Реализовать поиск с кэшированием
        pass

class CommentService:
    def __init__(self, comment_repo, article_repo, moderation_service):
        self.comment_repo = comment_repo
        self.article_repo = article_repo
        self.moderation_service = moderation_service

    def add_comment(self, article_id: int, content: str, author_id: int) -> Comment:
        '''Добавление комментария'''
        # TODO: Проверка существования статьи
        # TODO: Модерация контента
        # TODO: Создание комментария
        pass

# TODO: Создайте остальные сервисы
```

### 4. API слой (Controllers)

```python
# TODO: Создайте FastAPI роутеры
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List

router = APIRouter()

# TODO: Создайте dependency injection
def get_article_service() -> ArticleService:
    # TODO: Настройка зависимостей
    pass

@router.post("/articles/", response_model=ArticleResponse)
async def create_article(
    request: CreateArticleRequest,
    current_user: User = Depends(get_current_user),
    article_service: ArticleService = Depends(get_article_service)
):
    '''Создание новой статьи'''
    try:
        article = article_service.create_article(
            title=request.title,
            content=request.content,
            author_id=current_user.id
        )
        return ArticleResponse.from_domain(article)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/articles/", response_model=List[ArticleSummary])
async def list_articles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    article_service: ArticleService = Depends(get_article_service)
):
    '''Получение списка статей'''
    if search:
        articles = article_service.search_articles(search, page)
    else:
        articles = article_service.get_published_articles(page, per_page)

    return [ArticleSummary.from_domain(article) for article in articles]

@router.put("/articles/{article_id}/publish")
async def publish_article(
    article_id: int,
    current_user: User = Depends(get_current_user),
    article_service: ArticleService = Depends(get_article_service)
):
    '''Публикация статьи'''
    # TODO: Проверка прав (только автор или админ)
    # TODO: Публикация статьи
    pass

# TODO: Создайте остальные эндпоинты
```

### 5. Кэширование и оптимизация

```python
# TODO: Реализуйте кэширование
from functools import lru_cache
import redis
from typing import Optional

class CacheService:
    def __init__(self):
        self.redis = redis.Redis()
        self.ttl = 3600  # 1 час

    def get(self, key: str) -> Optional[str]:
        return self.redis.get(key)

    def set(self, key: str, value: str) -> None:
        self.redis.setex(key, self.ttl, value)

    def delete(self, key: str) -> None:
        self.redis.delete(key)

class CachedArticleService(ArticleService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = CacheService()

    @lru_cache(maxsize=100)
    def get_article_by_id(self, article_id: int) -> Optional[Article]:
        '''Кэширование статей в памяти'''
        return super().get_article_by_id(article_id)

    def get_popular_articles(self) -> List[Article]:
        '''Кэширование популярных статей в Redis'''
        cache_key = "popular_articles"
        cached = self.cache.get(cache_key)

        if cached:
            # TODO: Десериализация из JSON
            pass

        articles = super().get_popular_articles()

        # TODO: Сериализация в JSON и кэширование
        return articles

# TODO: Добавьте асинхронную обработку тяжелых задач
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncArticleService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def generate_seo_metadata(self, article: Article) -> Dict[str, str]:
        '''Асинхронная генерация SEO метаданных'''
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._generate_metadata_sync,
            article
        )

    def _generate_metadata_sync(self, article: Article) -> Dict[str, str]:
        # TODO: Генерация метаданных (тяжелая операция)
        pass
```

### 6. Тестирование

```python
# TODO: Создайте тесты
import pytest
from unittest.mock import Mock, MagicMock

class TestArticleService:
    def setup_method(self):
        self.mock_repo = Mock()
        self.mock_user_repo = Mock()
        self.mock_event_publisher = Mock()

        self.service = ArticleService(
            self.mock_repo,
            self.mock_user_repo,
            self.mock_event_publisher
        )

    def test_create_article_success(self):
        # TODO: Тест успешного создания статьи
        pass

    def test_create_article_validation_error(self):
        # TODO: Тест валидации данных
        pass

    def test_publish_article_by_author(self):
        # TODO: Тест публикации статьи автором
        pass

    def test_publish_article_by_non_author(self):
        # TODO: Тест запрета публикации чужой статьи
        pass

# TODO: Создайте интеграционные тесты
class TestArticleAPI:
    def test_create_article_endpoint(self):
        # TODO: Тест API эндпоинта
        pass

    def test_list_articles_pagination(self):
        # TODO: Тест пагинации
        pass
```

### 7. Конфигурация и развертывание

```python
# TODO: Создайте конфигурацию приложения
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://localhost/cms"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # JWT
    jwt_secret: str = "your-secret-key"
    jwt_expiration: int = 3600

    # Application
    debug: bool = False
    api_prefix: str = "/api/v1"

    class Config:
        env_file = ".env"

# TODO: Создайте Docker конфигурацию
# Dockerfile
# docker-compose.yml
# Скрипты развертывания

# TODO: Настройте CI/CD pipeline
# GitHub Actions или аналог
# Автоматическое тестирование
# Автоматическое развертывание
```

## Ожидаемый результат

Создайте полноценное монолитное приложение со:

1. **Четкой архитектурой** - разделение на слои
2. **Доменными моделями** - чистая бизнес-логика
3. **Repository Pattern** - абстракция данных
4. **Service Layer** - оркестрация бизнес-процессов
5. **REST API** - внешний интерфейс
6. **Кэшированием** - оптимизация производительности
7. **Тестированием** - полный coverage
8. **Документацией** - автоматическая генерация

## Расширения для продвинутого уровня

### CQRS (Command Query Responsibility Segregation)
```python
# TODO: Разделить команды и запросы
class ArticleCommands:
    def create_article(self, command: CreateArticleCommand) -> int:
        pass

    def publish_article(self, command: PublishArticleCommand) -> None:
        pass

class ArticleQueries:
    def get_article(self, article_id: int) -> ArticleView:
        pass

    def list_articles(self, filters: ArticleFilters) -> List[ArticleSummary]:
        pass
```

### Event Sourcing
```python
# TODO: Добавить хранение событий
class EventStore:
    def save_event(self, event: DomainEvent) -> None:
        pass

    def get_events(self, aggregate_id: str) -> List[DomainEvent]:
        pass

class ArticleAggregate:
    def __init__(self):
        self.events: List[DomainEvent] = []

    def create(self, title: str, content: str) -> None:
        event = ArticleCreatedEvent(title, content)
        self.events.append(event)
        self._apply(event)

    def publish(self) -> None:
        event = ArticlePublishedEvent(self.id)
        self.events.append(event)
        self._apply(event)

    def _apply(self, event: DomainEvent) -> None:
        # TODO: Применение события к агрегату
        pass
```

---

*Помните: Хороший монолит - это не просто код в одном репозитории, а хорошо структурированная система с четким разделением ответственности, готовностью к тестированию и возможностью будущего масштабирования.*""",
    [
        "Спроектировать архитектуру монолитного приложения",
        "Реализовать доменные модели и бизнес-логику",
        "Создать Repository и Service слои",
        "Разработать REST API с FastAPI",
        "Добавить кэширование и оптимизацию производительности",
        "Написать unit и integration тесты",
        "Настроить CI/CD и Docker"
    ]
) }}














