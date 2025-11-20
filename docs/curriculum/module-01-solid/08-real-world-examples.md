# 🌍 SOLID в реальных библиотеках Python

## 🎯 Цели урока

После изучения этого урока вы сможете:
- ✅ Видеть применение SOLID принципов в популярных библиотеках
- ✅ Понимать, как крупные проекты используют SOLID
- ✅ Применять паттерны из реальных библиотек в своих проектах

## 📚 Примеры из популярных библиотек

### 1. FastAPI - Применение DIP и SRP

**FastAPI** - современный веб-фреймворк, который отлично демонстрирует SOLID принципы.

#### Пример: Dependency Injection (DIP)

```python
from fastapi import FastAPI, Depends
from typing import Protocol

# ✅ DIP: Абстракция (Protocol)
class UserRepository(Protocol):
    def get_user(self, user_id: int) -> dict: ...

# ✅ DIP: Конкретная реализация
class DatabaseUserRepository:
    def get_user(self, user_id: int) -> dict:
        # Логика работы с БД
        return {"id": user_id, "name": "Alice"}

# ✅ DIP: Dependency Injection через Depends()
app = FastAPI()

def get_repository() -> UserRepository:
    return DatabaseUserRepository()

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    repo: UserRepository = Depends(get_repository)  # DIP в действии!
):
    return repo.get_user(user_id)
```

**Почему это DIP?**
- Контроллер зависит от абстракции `UserRepository`, а не от конкретной реализации
- Легко заменить `DatabaseUserRepository` на `InMemoryUserRepository` для тестов
- FastAPI автоматически инжектирует зависимости через `Depends()`

#### Пример: Single Responsibility (SRP)

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel

# ✅ SRP: Каждый роутер отвечает за одну область
users_router = APIRouter(prefix="/users", tags=["users"])
orders_router = APIRouter(prefix="/orders", tags=["orders"])

# ✅ SRP: Модели данных отделены от бизнес-логики
class UserCreate(BaseModel):
    name: str
    email: str

# ✅ SRP: Валидация отделена от обработки
@users_router.post("/", response_model=UserCreate)
async def create_user(user: UserCreate):
    # Только обработка запроса
    return user

app = FastAPI()
app.include_router(users_router)  # Разделение по ответственности
app.include_router(orders_router)
```

---

### 2. SQLAlchemy - Применение OCP и ISP

**SQLAlchemy** - ORM для работы с базами данных, демонстрирует OCP и ISP.

#### Пример: Open/Closed Principle (OCP)

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# ✅ OCP: Базовый класс закрыт для модификации
class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    
    def to_dict(self):
        """Базовый метод - не изменяется"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# ✅ OCP: Расширение через наследование (открыт для расширения)
class User(BaseModel):
    __tablename__ = 'users'
    
    name = Column(String(50))
    email = Column(String(100))
    
    # Новый функционал без изменения BaseModel
    def get_full_info(self):
        return f"{self.name} ({self.email})"

class Product(BaseModel):
    __tablename__ = 'products'
    
    title = Column(String(100))
    price = Column(Integer)
    
    # Другое расширение без изменения базового класса
    def get_price_formatted(self):
        return f"${self.price / 100:.2f}"
```

**Почему это OCP?**
- `BaseModel` закрыт для модификации - его не нужно менять
- Новые модели расширяют функциональность через наследование
- Каждая модель добавляет свои методы без изменения базового класса

#### Пример: Interface Segregation (ISP)

```python
from sqlalchemy.orm import Session
from typing import Protocol

# ✅ ISP: Разделение интерфейсов по ответственности

class ReadableRepository(Protocol):
    """Только чтение - для отчетов"""
    def get_by_id(self, session: Session, id: int): ...
    def get_all(self, session: Session): ...

class WritableRepository(Protocol):
    """Только запись - для администраторов"""
    def create(self, session: Session, data: dict): ...
    def update(self, session: Session, id: int, data: dict): ...
    def delete(self, session: Session, id: int): ...

# ✅ ISP: Клиенты используют только нужные интерфейсы
class ReportService:
    def __init__(self, repo: ReadableRepository):  # Только чтение!
        self.repo = repo
    
    def generate_report(self, session: Session):
        return self.repo.get_all(session)

class AdminService:
    def __init__(self, repo: WritableRepository):  # Только запись!
        self.repo = repo
    
    def create_item(self, session: Session, data: dict):
        return self.repo.create(session, data)
```

---

### 3. Pydantic - Применение SRP и LSP

**Pydantic** - библиотека для валидации данных, отличный пример SRP и LSP.

#### Пример: Single Responsibility (SRP)

```python
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional

# ✅ SRP: Модель отвечает только за валидацию данных
class UserCreate(BaseModel):
    name: str
    email: EmailStr  # Requires email-validator package (install: pydantic[email])
    age: int
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Age must be between 0 and 150')
        return v

# ✅ SRP: Отдельный класс для обновления
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None

# ✅ SRP: Отдельный класс для ответа
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Для работы с SQLAlchemy моделями
    
    id: int
    name: str
    email: str
```

!!! note "Pydantic v1 vs v2"
    В Pydantic v1 использовался `class Config: orm_mode = True`. 
    В Pydantic v2 это заменено на `model_config = ConfigDict(from_attributes=True)`.
    Также `@validator` заменён на `@field_validator` с декоратором `@classmethod`.

> **Note:** `EmailStr` requires the `email-validator` package. Install it with:
> ```bash
> uv add "pydantic[email]"
> ```
> 
> **Fallback options** (if you can't install `email-validator`):
> - Use a plain `str` field with a `@validator` to check email format
> - Use Pydantic's `constr` with a regex pattern as an alternative

**Почему это SRP?**
- `UserCreate` - только создание и валидация
- `UserUpdate` - только обновление (частичное)
- `UserResponse` - только представление данных
- Каждый класс имеет одну ответственность

#### Пример: Liskov Substitution (LSP)

```python
from pydantic import BaseModel

# ✅ LSP: Базовый класс
class BaseUser(BaseModel):
    name: str
    email: str
    
    def get_display_name(self) -> str:
        return f"{self.name} ({self.email})"

# ✅ LSP: Наследник полностью заменяет родителя
class AdminUser(BaseUser):
    role: str = "admin"
    
    def get_display_name(self) -> str:
        # Усиливает поведение, но не нарушает контракт
        return f"[ADMIN] {super().get_display_name()}"

# ✅ LSP: Функция работает с любым наследником
def display_user(user: BaseUser):
    print(user.get_display_name())  # Работает для обоих типов!

# Использование
admin = AdminUser(name="Alice", email="alice@example.com")
regular = BaseUser(name="Bob", email="bob@example.com")

display_user(admin)   # ✅ Работает
display_user(regular) # ✅ Работает
```

---

### 4. Django - Применение всех SOLID принципов

**Django** - полнофункциональный веб-фреймворк, демонстрирует комплексное применение SOLID.

#### Пример: SRP в Django Models

```python
from django.db import models
from django.core.validators import EmailValidator

# ✅ SRP: Модель отвечает только за структуру данных
class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()])
    created_at = models.DateTimeField(auto_now_add=True)

# ✅ SRP: Менеджер отвечает только за запросы
class UserManager(models.Manager):
    def active_users(self):
        return self.filter(is_active=True)
    
    def by_email(self, email):
        return self.filter(email=email)

# ✅ SRP: Сервис отвечает только за бизнес-логику
class UserService:
    def __init__(self, user_model):
        self.user_model = user_model
    
    def create_user(self, name: str, email: str):
        # Бизнес-логика создания пользователя
        return self.user_model.objects.create(name=name, email=email)
```

#### Пример: DIP в Django Views

```python
from django.http import JsonResponse
from typing import Protocol

# ✅ DIP: Абстракция
class UserRepository(Protocol):
    def get_user(self, user_id: int): ...
    def create_user(self, data: dict): ...

# ✅ DIP: Реализация
class DjangoUserRepository:
    def __init__(self, user_model):
        self.user_model = user_model
    
    def get_user(self, user_id: int):
        return self.user_model.objects.get(id=user_id)
    
    def create_user(self, data: dict):
        return self.user_model.objects.create(**data)

# ✅ DIP: View зависит от абстракции
class UserView:
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    def get(self, request, user_id: int):
        user = self.repository.get_user(user_id)
        return JsonResponse({"id": user.id, "name": user.name})
```

---

### 5. Requests - Применение OCP

**Requests** - библиотека для HTTP запросов, демонстрирует OCP через адаптеры.

```python
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.util import Timeout

# ✅ OCP: Requests открыт для расширения через адаптеры
class CustomAdapter(HTTPAdapter):
    """Customizes connection/read timeouts and connection pool sizing/logging without altering Requests core behavior"""
    
    def init_poolmanager(self, *args, **kwargs):
        # Кастомная логика инициализации с логированием и настройками
        logger = logging.getLogger(__name__)
        
        # Настройка таймаутов
        kwargs.setdefault('timeout', Timeout(connect=10, read=30))
        
        # Настройка параметров пула соединений
        pool_kwargs = kwargs.get('pool_kwargs', {})
        pool_kwargs.setdefault('maxsize', 50)  # Максимальный размер пула
        pool_kwargs.setdefault('block', False)  # Не блокировать при переполнении
        kwargs['pool_kwargs'] = pool_kwargs
        
        # Логирование параметров инициализации
        logger.info(
            f"Initializing pool manager with timeout={kwargs.get('timeout')}, "
            f"pool_kwargs={pool_kwargs}"
        )
        
        # Вызов родительского метода с настроенными параметрами
        super().init_poolmanager(*args, **kwargs)

# ✅ OCP: Добавление нового функционала без изменения кода Requests
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)  # Расширение без изменения Requests
session.mount("https://", adapter)
```

---

## 🎯 Ключевые выводы

1. **Популярные библиотеки следуют SOLID** - это не случайность, а необходимость для масштабируемости
2. **SRP** - разделение моделей, сервисов, репозиториев
3. **OCP** - расширение через наследование и адаптеры
4. **LSP** - корректное наследование моделей
5. **ISP** - разделение интерфейсов по клиентам
6. **DIP** - dependency injection везде

## 🚀 Практическое задание

Изучите исходный код одной из библиотек:
- FastAPI: `fastapi/dependencies`
- SQLAlchemy: `sqlalchemy/orm`
- Pydantic: `pydantic/main.py`

Найдите примеры применения каждого принципа SOLID и опишите их.

---

!!! tip "Практический совет"
    При изучении новых библиотек обращайте внимание на применение SOLID принципов. Это поможет вам лучше понять архитектуру и применять те же паттерны в своих проектах.

