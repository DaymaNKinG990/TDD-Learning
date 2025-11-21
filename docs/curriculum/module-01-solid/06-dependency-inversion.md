# 🔄 Урок 6: Dependency Inversion Principle (DIP)

## 🎯 Цели урока

После изучения этого урока вы сможете:
- ✅ Понимать концепцию инверсии зависимостей
- ✅ Создавать слабо связанные системы
- ✅ Применять dependency injection
- ✅ Писать тестируемый код

## 📖 Определение DIP

!!! quote "Принцип инверсии зависимостей"
    **Модули высокого уровня не должны зависеть от модулей низкого уровня. Оба типа модулей должны зависеть от абстракций.**

    **Абстракции не должны зависеть от деталей. Детали должны зависеть от абстракций.**

### 💡 Простыми словами:

Представьте зарядку телефона:
- ❌ **Плохо**: Телефон привязан к конкретной розетке (если розетка сломается, телефон не работает)
- ✅ **Хорошо**: Телефон работает через универсальный разъем (USB-C), можно подключить к любой зарядке

В программировании:
- **Высокий уровень** (бизнес-логика) не должен зависеть от **низкого уровня** (БД, файлы)
- **Оба зависят от абстракций** (интерфейсов, протоколов)
- **Можно легко заменить** реализацию без изменения бизнес-логики

### Что это значит на практике?

```python
# ❌ БЕЗ DIP: бизнес-логика зависит от конкретной БД
class UserService:
    def __init__(self):
        self.db = SQLiteConnection()  # Жесткая зависимость!

# ✅ С DIP: бизнес-логика зависит от абстракции
class UserService:
    def __init__(self, repository: UserRepository):  # Абстракция!
        self.repository = repository

# Теперь можно использовать любую БД:
service1 = UserService(SQLiteRepository())      # SQLite
service2 = UserService(PostgreSQLRepository()) # PostgreSQL
service3 = UserService(InMemoryRepository())   # Для тестов
```

**Термины:**
- **Высокий уровень** - бизнес-логика, use cases, сервисы
- **Низкий уровень** - инфраструктура, БД, внешние API
- **Абстракции** - интерфейсы, протоколы, абстрактные классы

### Почему это важно?

Без DIP:
- Код сложно тестировать (зависимости от реальных сервисов)
- Сложно заменять реализации (жесткие зависимости)
- Высокая связанность компонентов
- Проблемы с поддержкой и развитием

## 🔍 Как распознать нарушение DIP?

### Признаки нарушения

1. **Прямые импорты низкоуровневых модулей**
2. **Создание экземпляров в конструкторах**
3. **Жесткие зависимости от конкретных реализаций**
4. **Сложность тестирования без mock объектов**

## ❌ Пример нарушения DIP

```python
import sqlite3
from dataclasses import dataclass
from typing import List


@dataclass
class User:
    """Модель пользователя"""
    id: int
    name: str
    email: str


class UserRepository:
    """❌ Репозиторий - зависит от конкретной БД"""

    def __init__(self):
        # Прямая зависимость от SQLite
        self.connection = sqlite3.connect("users.db")
        self.create_table()

    def create_table(self) -> None:
        """Создает таблицу пользователей"""
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """)
        self.connection.commit()

    def save(self, user: User) -> None:
        """Сохраняет пользователя в БД"""
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
            (user.id, user.name, user.email)
        )
        self.connection.commit()

    def find_by_id(self, user_id: int) -> User | None:
        """Находит пользователя по ID"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return User(id=row[0], name=row[1], email=row[2])
        return None

    def find_all(self) -> List[User]:
        """Находит всех пользователей"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, name, email FROM users")
        rows = cursor.fetchall()
        return [User(id=row[0], name=row[1], email=row[2]) for row in rows]


class UserService:
    """❌ Сервис - зависит от конкретного репозитория"""

    def __init__(self):
        # Прямая зависимость от конкретного репозитория
        self.repository = UserRepository()

    def create_user(self, name: str, email: str) -> User:
        """Создает нового пользователя"""
        user = User(id=self._generate_id(), name=name, email=email)
        self.repository.save(user)
        return user

    def get_user(self, user_id: int) -> User | None:
        """Получает пользователя по ID"""
        return self.repository.find_by_id(user_id)

    def get_all_users(self) -> List[User]:
        """Получает всех пользователей"""
        return self.repository.find_all()

    def _generate_id(self) -> int:
        """Генерирует ID пользователя"""
        users = self.repository.find_all()
        return max([user.id for user in users], default=0) + 1


# Использование
service = UserService()
user = service.create_user("Иван", "ivan@example.com")
print(f"Создан пользователь: {user.name}")
```

### Анализ проблем

| Проблема | Последствия |
|----------|-------------|
| **Жесткие зависимости** | Невозможно заменить БД |
| **Сложность тестирования** | Нужна реальная БД для тестов |
| **Высокая связанность** | Изменения в БД влияют на сервис |
| **Отсутствие гибкости** | Зафиксирована конкретная реализация |

## ✅ Правильное применение DIP

### Шаг 1: Создание абстракций

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Protocol


@dataclass
class User:
    """Модель пользователя"""
    id: int
    name: str
    email: str


class UserRepository(Protocol):
    """Протокол репозитория пользователей - абстракция"""

    def save(self, user: User) -> None:
        """Сохраняет пользователя"""
        ...

    def find_by_id(self, user_id: int) -> User | None:
        """Находит пользователя по ID"""
        ...

    def find_all(self) -> List[User]:
        """Находит всех пользователей"""
        ...
```

### Шаг 2: Конкретные реализации

```python
class SQLiteUserRepository:
    """Реализация репозитория для SQLite"""

    def __init__(self, db_path: str = "users.db"):
        import sqlite3
        self.connection = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self) -> None:
        """Создает таблицу пользователей"""
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """)
        self.connection.commit()

    def save(self, user: User) -> None:
        """Сохраняет пользователя в БД"""
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
            (user.id, user.name, user.email)
        )
        self.connection.commit()

    def find_by_id(self, user_id: int) -> User | None:
        """Находит пользователя по ID"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return User(id=row[0], name=row[1], email=row[2])
        return None

    def find_all(self) -> List[User]:
        """Находит всех пользователей"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, name, email FROM users")
        rows = cursor.fetchall()
        return [User(id=row[0], name=row[1], email=row[2]) for row in rows]


class InMemoryUserRepository:
    """Реализация репозитория в памяти - для тестирования"""

    def __init__(self):
        self.users: List[User] = []

    def save(self, user: User) -> None:
        """Сохраняет пользователя в память"""
        self.users.append(user)

    def find_by_id(self, user_id: int) -> User | None:
        """Находит пользователя по ID"""
        for user in self.users:
            if user.id == user_id:
                return user
        return None

    def find_all(self) -> List[User]:
        """Находит всех пользователей"""
        return self.users.copy()
```

### Шаг 3: Dependency Injection

```python
class UserService:
    """✅ Сервис - зависит от абстракции, не от конкретной реализации"""

    def __init__(self, repository: UserRepository):
        # Зависимость инжектируется через конструктор
        self.repository = repository

    def create_user(self, name: str, email: str) -> User:
        """Создает нового пользователя"""
        user = User(id=self._generate_id(), name=name, email=email)
        self.repository.save(user)
        return user

    def get_user(self, user_id: int) -> User | None:
        """Получает пользователя по ID"""
        return self.repository.find_by_id(user_id)

    def get_all_users(self) -> List[User]:
        """Получает всех пользователей"""
        return self.repository.find_all()

    def _generate_id(self) -> int:
        """Генерирует ID пользователя"""
        users = self.repository.find_all()
        return max([user.id for user in users], default=0) + 1
```

### Шаг 4: Композиция зависимостей

```python
# Создание зависимостей
sqlite_repo = SQLiteUserRepository("production.db")
memory_repo = InMemoryUserRepository()

# Инъекция зависимостей
prod_service = UserService(sqlite_repo)    # Для продакшена
test_service = UserService(memory_repo)    # Для тестирования

# Использование
user = prod_service.create_user("Иван", "ivan@example.com")
print(f"Создан пользователь: {user.name}")
```

## 🎯 Стратегии применения DIP

### 1. **Constructor Injection**

```python
# Самый распространенный способ
class OrderService:
    def __init__(self, repository: OrderRepository, payment: PaymentService):
        self.repository = repository
        self.payment = payment
```

### 2. **Method Injection**

```python
from typing import Protocol, Optional


class DataFetcher(Protocol):
    """Protocol for data fetching operations"""
    
    def fetch(self, source: str) -> dict:
        """Fetches data from the specified source"""
        ...


class DefaultDataFetcher:
    """Default implementation of DataFetcher"""
    
    def fetch(self, source: str) -> dict:
        """Fetches data from source (default implementation)"""
        return {"source": source, "data": "default data"}


# Для опциональных зависимостей
class ReportGenerator:
    def generate_report(self, data_fetcher: Optional[DataFetcher] = None):
        if data_fetcher is None:
            data_fetcher = DefaultDataFetcher()
        # Использование data_fetcher
        data = data_fetcher.fetch("report_source")
        return f"Report generated with data: {data}"
```

### 3. **Property Injection**

```python
# Для конфигурационных зависимостей
class Logger:
    def __init__(self):
        self.formatter = None  # Будет установлено позже

    def set_formatter(self, formatter: LogFormatter):
        self.formatter = formatter
```

### 4. **Factory Pattern**

```python
# Для создания сложных зависимостей
class ServiceFactory:
    @staticmethod
    def create_user_service() -> UserService:
        db_config = DatabaseConfig.from_env()
        repository = SQLiteUserRepository(db_config.path)
        return UserService(repository)

    @staticmethod
    def create_test_user_service() -> UserService:
        repository = InMemoryUserRepository()
        return UserService(repository)
```

## 🛠 Простые инструменты DIP

### **DI Container - базовая идея**

```python
# Простейший контейнер для управления зависимостями
class Container:
    def __init__(self):
        self.services = {}
    
    def register(self, name: str, service):
        self.services[name] = service
    
    def get(self, name: str):
        return self.services[name]

# Использование
container = Container()
container.register('repo', SQLiteUserRepository("users.db"))
container.register('service', UserService(container.get('repo')))

# Получение готового сервиса
service = container.get('service')
```

## 🎮 Практические упражнения

### Упражнение 1: Рефакторинг жестких зависимостей

**Исходный код:**
```python
class PaymentService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.api = PaymentAPI()
        self.logger = FileLogger()

    def process_payment(self, amount, card_info):
        # Использование всех зависимостей
        pass
```

**Задание:**
1. Создайте абстракции для всех зависимостей
2. Реализуйте dependency injection
3. Создайте тестовые реализации

**💡 Подсказки для решения:**
> **Проблема DIP:** PaymentService жестко зависит от конкретных реализаций
>
> **Нужно создать:**
> - 📋 **3 Protocol**: `DatabaseConnection`, `PaymentAPI`, `Logger`
> - 🔧 **6 реализаций**: по 2 для каждой зависимости (реальная + тестовая)
> - 🎯 **1 рефакторинг**: PaymentService принимает зависимости через конструктор
>
> **Результат DIP:** Сервис зависит от абстракций, легко тестируется

### Упражнение 2: Создание DI контейнера

**Задание:** Реализуйте простой dependency injection контейнер со следующими возможностями:

```python
class DIContainer:
    def register(self, interface, implementation):
        # Регистрация зависимостей
        pass

    def register_singleton(self, interface, implementation):
        # Регистрация синглтона
        pass

    def resolve(self, interface):
        # Получение зависимости
        pass

    def create_scope(self):
        # Создание скоупа для временных зависимостей
        pass
```

**💡 Жизненные циклы зависимостей:**

| Тип | Жизненный цикл | Когда использовать |
|-----|----------------|-------------------|
| **Transient** | Новый экземпляр каждый раз | Легковесные объекты без состояния |
| **Singleton** | Один на все приложение | Конфигурация, кеш, логгеры |
| **Scoped** | Один в пределах области | HTTP запрос, транзакция БД, пользовательская сессия |

### 🔍 **Временные зависимости (Scoped) - детально:**

```python
# Пример из веб-приложения
class DatabaseConnection:
    """Подключение к БД должно жить только в пределах одного HTTP запроса"""
    def __init__(self):
        self.connection = create_db_connection()
        print(f"🔌 DB connection created: {id(self)}")
    
    def close(self):
        self.connection.close()
        print(f"❌ DB connection closed: {id(self)}")

class UserRepository:
    """Репозиторий использует scoped соединение"""
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def get_user(self, user_id: int):
        return self.db.connection.execute(f"SELECT * FROM users WHERE id={user_id}")

class OrderRepository:
    """Тот же scoped connection для согласованности данных"""
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def get_orders(self, user_id: int):
        return self.db.connection.execute(f"SELECT * FROM orders WHERE user_id={user_id}")

# Пример работы со scoped зависимостями
def handle_web_request(request):
    """Один HTTP запрос = один scope"""
    
    # Создаем scope для этого запроса
    with container.create_scope() as scope:
        # В пределах scope одно соединение используется везде
        user_repo = scope.resolve(UserRepository)  # Создает DB connection
        order_repo = scope.resolve(OrderRepository) # Использует ТО ЖЕ соединение!
        
        user = user_repo.get_user(request.user_id)
        orders = order_repo.get_orders(request.user_id)
        
        return {"user": user, "orders": orders}
    # При выходе из scope соединение автоматически закрывается
```

### **🎯 Зачем нужны Scoped зависимости?**

#### **1. Согласованность данных**
```python
# ❌ БЕЗ scope - разные соединения, возможны проблемы
def transfer_money(from_user, to_user, amount):
    user_service = UserService(DatabaseConnection())  # Соединение 1
    account_service = AccountService(DatabaseConnection())  # Соединение 2
    
    # Проблема: между операциями данные могут измениться!
    user_service.debit(from_user, amount)
    account_service.credit(to_user, amount)

# ✅ СО scope - одно соединение, транзакционность
def transfer_money(from_user, to_user, amount):
    with container.create_scope() as scope:
        # Все сервисы используют ОДНО соединение = одна транзакция
        user_service = scope.resolve(UserService)
        account_service = scope.resolve(AccountService)
        
        user_service.debit(from_user, amount)
        account_service.credit(to_user, amount)
        # Транзакция закрывается автоматически
```

#### **2. Управление ресурсами**
```python
# Веб-сервер обрабатывает запросы
class WebServer:
    def handle_request(self, request):
        # Каждый запрос = отдельный scope
        with self.container.create_scope() as request_scope:
            
            # Эти объекты живут только в пределах запроса
            session = request_scope.resolve(UserSession)  # Данные пользователя
            cache = request_scope.resolve(RequestCache)   # Кеш запроса
            logger = request_scope.resolve(RequestLogger) # Логи запроса
            
            # Используем сервисы
            result = self.process_request(request, session, cache, logger)
            
            return result
        # Все ресурсы автоматически очищаются
```

**💡 Подсказки для реализации:**
> **Цель:** Автоматизировать управление зависимостями с разными жизненными циклами
>
> **Нужно реализовать:**
> - 📋 **Словарь сервисов** для хранения зависимостей
> - 🔧 **register()** - transient регистрация (каждый раз новый)
> - 🏠 **register_singleton()** - ленивое создание одиночек
> - ⚡ **resolve()** - получение с проверкой существования
> - 🔄 **create_scope()** - контекстный менеджер для временных зависимостей
>
> **Scope должен:**
> - Создавать объекты при первом обращении
> - Возвращать тот же объект при повторных запросах в scope
> - Очищать все объекты при выходе из scope

### Упражнение 3: Интеграционное тестирование

**Задание:** Создайте тесты для `UserService` с использованием разных реализаций репозитория.

```python
def test_user_service_with_memory_repo():
    """Тест с in-memory репозиторием"""
    # Создайте UserService с InMemoryUserRepository
    # Протестируйте создание и получение пользователей
    pass

def test_user_service_with_sqlite_repo():
    """Тест с SQLite репозиторием"""
    # Создайте UserService с SQLiteUserRepository
    # Протестируйте создание и получение пользователей
    pass
```

**💡 Подсказки для решения:**
> **Цель DIP в тестах:** Легкая замена реализаций для разных сценариев
>
> **Тестовая стратегия:**
> - 📋 **InMemoryRepository** - быстрые unit-тесты
> - 🔧 **SQLiteRepository** - интеграционные тесты с БД
> - 🎯 **Один и тот же UserService** работает с любой реализацией
>
> **Проверки:** create_user(), get_user(), бизнес-логика одинакова в обоих тестах

## 🎯 Ключевые выводы

1. **DIP - основа тестируемой архитектуры**
2. **Абстракции разрывают жесткие связи**
3. **Dependency injection повышает гибкость**
4. **Тестирование становится проще**
5. **Код становится более поддерживаемым**

## 🚀 Следующие шаги

!!! success "Что вы узнали"
    - ✅ Модули высокого уровня не должны зависеть от низкого уровня
    - ✅ Оба должны зависеть от абстракций
    - ✅ Dependency Injection делает код тестируемым и гибким

!!! tip "Практика"
    Найдите класс, который создает зависимости внутри себя. Попробуйте передать их через конструктор (Dependency Injection).

Теперь вы готовы изучить **[SOLID на практике](07-solid-in-practice.md)** - комплексное применение всех принципов в реальных проектах!

---

!!! tip "Практический совет"
    Применяйте SOLID принципы постепенно. Начните с малого - выберите один класс в вашем проекте и примените все пять принципов к нему. Это даст вам практический опыт и уверенность.

## 🧪 Проверьте свои знания: DIP

<div class="quiz-container" id="dip-quiz">
<script type="application/json">
{
  "title": "Dependency Inversion Principle",
  "description": "Проверьте понимание принципа инверсии зависимостей",
  "icon": "🔄",
  "questions": [
    {
      "question": "Что означает принцип Инверсии Зависимостей (DIP)?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "Модули высокого уровня не должны зависеть от модулей низкого уровня", "correct": true},
        {"text": "Все зависимости должны быть жесткими", "correct": false},
        {"text": "Низкоуровневые модули должны зависеть от высокоуровневых", "correct": false},
        {"text": "Зависимости должны быть односторонними", "correct": false}
      ],
      "explanation": "DIP говорит о зависимости от абстракций, а не от конкретных реализаций"
    },
    {
      "question": "Что такое Dependency Injection?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "Способ создания зависимостей внутри класса", "correct": false},
        {"text": "Способ передачи зависимостей извне в класс", "correct": true},
        {"text": "Способ автоматического разрешения зависимостей", "correct": false},
        {"text": "Способ клонирования объектов", "correct": false}
      ],
      "explanation": "Dependency Injection - это паттерн, когда зависимости передаются в класс извне"
    },
    {
      "question": "Какой код нарушает DIP?",
      "type": "single",
      "points": 1,
      "code": "# Вариант A: Нарушение DIP\nclass UserService:\n    def __init__(self):\n        self.repo = SQLiteUserRepository()  # Жесткая зависимость\n\n# Вариант B: Правильное применение DIP\nclass UserService:\n    def __init__(self, repo: UserRepository):\n        self.repo = repo  # Зависимость от абстракции",
      "options": [
        {"text": "Вариант A - жесткая зависимость", "correct": true},
        {"text": "Вариант B - dependency injection", "correct": false}
      ],
      "explanation": "Вариант A создает конкретную реализацию внутри класса, что нарушает DIP"
    },
    {
      "question": "Что такое 'инверсия' в DIP?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "Изменение направления зависимостей", "correct": true},
        {"text": "Создание обратных зависимостей", "correct": false},
        {"text": "Удаление всех зависимостей", "correct": false},
        {"text": "Создание циклических зависимостей", "correct": false}
      ],
      "explanation": "Инверсия означает изменение направления - высокоуровневые модули не зависят от низкоуровневых"
    },
    {
      "question": "Какой способ Dependency Injection является наиболее распространенным?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "Constructor Injection", "correct": true},
        {"text": "Property Injection", "correct": false},
        {"text": "Method Injection", "correct": false},
        {"text": "Global Variable Injection", "correct": false}
      ],
      "explanation": "Constructor Injection наиболее распространен и рекомендуется"
    },
    {
      "question": "Что такое 'абстракция' в контексте DIP?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "Абстрактный класс или интерфейс", "correct": true},
        {"text": "Конкретная реализация", "correct": false},
        {"text": "Базовый класс", "correct": false},
        {"text": "Глобальная переменная", "correct": false}
      ],
      "explanation": "Абстракция - это интерфейс или абстрактный класс, не зависящий от деталей"
    },
    {
      "question": "Какой код демонстрирует правильное применение DIP?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "class UserService: def __init__(self): self.db = Database()", "correct": false},
        {"text": "class UserService: def __init__(self, db: Database): self.db = db", "correct": true},
        {"text": "class UserService: def __init__(self, db: IDatabase): self.db = db", "correct": true},
        {"text": "class UserService: def create_user(self, db: Database): pass", "correct": false}
      ],
      "explanation": "Правильное применение DIP - зависимости от абстракций через конструктор"
    },
    {
      "question": "Что является преимуществом соблюдения DIP?",
      "type": "multiple",
      "points": 2,
      "options": [
        {"text": "Код становится более тестируемым", "correct": true},
        {"text": "Увеличивается связность между модулями", "correct": false},
        {"text": "Упрощается замена реализаций", "correct": true},
        {"text": "Уменьшается количество интерфейсов", "correct": false},
        {"text": "Улучшается поддерживаемость кода", "correct": true}
      ],
      "explanation": "DIP улучшает тестируемость, заменяемость и поддерживаемость"
    },
    {
      "question": "Что такое DI контейнер?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "Контейнер для хранения данных", "correct": false},
        {"text": "Фреймворк для автоматического разрешения зависимостей", "correct": true},
        {"text": "База данных для зависимостей", "correct": false},
        {"text": "Кеш для объектов", "correct": false}
      ],
      "explanation": "DI контейнер автоматически разрешает и инжектирует зависимости"
    },
    {
      "question": "Какой паттерн часто используется вместе с DIP?",
      "type": "multiple",
      "points": 2,
      "options": [
        {"text": "Abstract Factory", "correct": true},
        {"text": "Singleton", "correct": false},
        {"text": "Strategy", "correct": true},
        {"text": "Template Method", "correct": false},
        {"text": "Observer", "correct": false}
      ],
      "explanation": "Abstract Factory и Strategy паттерны хорошо работают с DIP"
    }
  ]
}
</script>
</div>


