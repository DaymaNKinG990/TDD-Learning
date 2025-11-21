# Основы тестирования в Python

## 🎯 Цели главы

В этой главе вы изучите:
- Основные типы тестов в Python (unit, integration, e2e)
- Структуру хорошего теста (AAA паттерн)
- Различные типы assertions
- Подготовку к работе с unittest и pytest

Python предоставляет мощные инструменты для тестирования "из коробки". В этой главе мы изучим основы написания тестов в Python, познакомимся со стандартным модулем `unittest` и подготовимся к работе с более продвинутым `pytest`.

## 🧪 Типы тестов в Python

### 1. Unit Tests (Модульные тесты)
**Тестируют отдельные функции/методы изолированно**

```python
def test_calculate_tax():
    """Тест функции расчета налога."""
    result = calculate_tax(1000)
    assert result == 130  # 13% налог
```

### 2. Integration Tests (Интеграционные тесты)
**Тестируют взаимодействие компонентов**

```python
def test_user_registration_sends_email():
    """Тест интеграции регистрации и email сервиса."""
    user_service = UserService()
    email_service = EmailService()
    
    user = user_service.register("user@example.com")
    
    assert email_service.was_sent(user.email)
```

### 3. End-to-End Tests (E2E тесты)
**Тестируют полный пользовательский сценарий**

```python
def test_complete_purchase_flow():
    """Тест полного процесса покупки."""
    # Имитируем действия пользователя от начала до конца
    response = client.post("/login", data={"email": "user@test.com"})
    response = client.post("/add-to-cart", data={"product_id": 1})
    response = client.post("/checkout")
    
    assert "Payment successful" in response.data
```

## 📋 Анатомия хорошего теста

### Структура AAA (Arrange-Act-Assert)

```python
def test_bank_account_withdraw():
    # Arrange (Подготовка)
    account = Account(initial_balance=100)
    withdraw_amount = 30
    
    # Act (Действие)
    account.withdraw(withdraw_amount)
    
    # Assert (Проверка)
    assert account.balance == 70
```

### Принципы именования тестов

#### ✅ Хорошие имена:
```python
def test_deposit_positive_amount_increases_balance():
    """Пополнение положительной суммой увеличивает баланс."""
    pass

def test_withdraw_more_than_balance_raises_exception():
    """Снятие суммы больше баланса вызывает исключение."""
    pass

def test_new_user_has_empty_shopping_cart():
    """У нового пользователя пустая корзина."""
    pass
```

#### ❌ Плохие имена:
```python
def test_user():  # Что именно тестируем?
    pass

def test_1():  # Неинформативно
    pass

def test_method():  # Какой метод?
    pass
```

### Шаблон именования: `test_[unit]_[scenario]_[expected_behavior]`

```python
def test_calculator_divide_by_zero_raises_exception():
    """calculator.divide() при делении на ноль вызывает исключение."""
    
def test_user_login_with_valid_credentials_returns_token():
    """user.login() с валидными данными возвращает токен."""
    
def test_shopping_cart_add_item_increases_total_count():
    """shopping_cart.add_item() увеличивает общее количество."""
```

## 🔧 Assertions в Python

### Базовые assert выражения

```python
def test_basic_assertions():
    # Равенство
    assert 2 + 2 == 4
    assert "hello" == "hello"
    
    # Неравенство  
    assert 3 != 4
    assert "cat" != "dog"
    
    # Логические значения
    assert True
    assert not False
    
    # Принадлежность
    assert "a" in "abc"
    assert 1 in [1, 2, 3]
    assert "key" in {"key": "value"}
    
    # Сравнения
    assert 5 > 3
    assert 2 < 10
    assert 5 >= 5
    assert 3 <= 3
    
    # Типы
    assert isinstance("hello", str)
    assert isinstance(42, int)
```

### Проверка исключений

```python
import pytest

def test_division_by_zero():
    """Деление на ноль должно вызывать ZeroDivisionError."""
    with pytest.raises(ZeroDivisionError):
        10 / 0

def test_invalid_email_raises_value_error():
    """Невалидный email должен вызывать ValueError."""
    with pytest.raises(ValueError, match="Invalid email"):
        User(email="invalid-email")

def test_exception_message():
    """Проверка конкретного сообщения исключения."""
    with pytest.raises(ValueError) as exc_info:
        validate_age(-5)
    
    assert "Age cannot be negative" in str(exc_info.value)
```

### Приблизительные сравнения

```python
import pytest

def test_floating_point_calculations():
    """Работа с числами с плавающей точкой."""
    result = 0.1 + 0.2
    
    # ❌ Может не работать из-за точности
    # assert result == 0.3
    
    # ✅ Правильный способ
    assert result == pytest.approx(0.3)
    
    # С указанием точности
    assert result == pytest.approx(0.3, abs=1e-6)
```

## 🏗 Настройка и очистка тестов

### Setup и Teardown паттерны

```python
import pytest
import tempfile
import os

class TestFileProcessor:
    
    def setup_method(self):
        """Вызывается перед каждым тестом."""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = FileProcessor(self.temp_dir)
    
    def teardown_method(self):
        """Вызывается после каждого теста."""
        shutil.rmtree(self.temp_dir)
    
    def test_process_file_creates_output(self):
        # Тест использует self.processor и self.temp_dir
        pass
```

### Использование fixtures (pytest)

```python
@pytest.fixture
def sample_user():
    """Создает тестового пользователя."""
    user = User("test@example.com", "Test User")
    yield user  # Возвращаем пользователя для теста
    # Код после yield выполнится после теста
    user.cleanup()

@pytest.fixture
def database():
    """Создает тестовую базу данных."""
    db = Database(":memory:")  # SQLite в памяти
    db.create_tables()
    yield db
    db.close()

def test_user_can_create_post(sample_user, database):
    """Пользователь может создать пост."""
    post = sample_user.create_post("Hello World!", database)
    
    assert post.title == "Hello World!"
    assert post.author == sample_user
```

## 🎯 Практические примеры

### Пример 1: Класс Calculator

```python
# calculator.py
from typing import Union

Number = Union[int, float]

class Calculator:
    """Простой калькулятор с базовыми операциями."""
    
    def add(self, a: Number, b: Number) -> Number:
        """Сложение двух чисел."""
        return a + b
    
    def subtract(self, a: Number, b: Number) -> Number:
        """Вычитание второго числа из первого."""
        return a - b
    
    def multiply(self, a: Number, b: Number) -> Number:
        """Умножение двух чисел."""
        return a * b
    
    def divide(self, a: Number, b: Number) -> float:
        """Деление первого числа на второе."""
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return a / b
```

```python
# test_calculator.py
import pytest
from calculator import Calculator

class TestCalculator:
    """Тесты для класса Calculator."""
    
    def setup_method(self):
        """Создаем калькулятор для каждого теста."""
        self.calc = Calculator()
    
    def test_add_positive_numbers(self):
        """Сложение положительных чисел."""
        result = self.calc.add(2, 3)
        assert result == 5
    
    def test_add_negative_numbers(self):
        """Сложение отрицательных чисел."""
        result = self.calc.add(-2, -3)
        assert result == -5
    
    def test_add_mixed_numbers(self):
        """Сложение положительного и отрицательного числа."""
        result = self.calc.add(5, -3)
        assert result == 2
    
    def test_subtract_numbers(self):
        """Вычитание чисел."""
        result = self.calc.subtract(10, 4)
        assert result == 6
    
    def test_multiply_numbers(self):
        """Умножение чисел."""
        result = self.calc.multiply(3, 4)
        assert result == 12
    
    def test_multiply_by_zero(self):
        """Умножение на ноль."""
        result = self.calc.multiply(5, 0)
        assert result == 0
    
    def test_divide_numbers(self):
        """Деление чисел."""
        result = self.calc.divide(10, 2)
        assert result == 5.0
    
    def test_divide_with_remainder(self):
        """Деление с остатком."""
        result = self.calc.divide(10, 3)
        assert result == pytest.approx(3.333333, rel=1e-5)
    
    def test_divide_by_zero_raises_exception(self):
        """Деление на ноль вызывает исключение."""
        with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
            self.calc.divide(10, 0)
```

### Пример 2: Система пользователей

```python
# user.py
import re
from datetime import datetime
from typing import Optional

class User:
    """Класс пользователя системы."""
    
    def __init__(self, email: str, name: str):
        self.email = self._validate_email(email)
        self.name = self._validate_name(name)
        self.created_at = datetime.now()
        self.is_active = True
        self._posts = []
    
    def _validate_email(self, email: str) -> str:
        """Валидация email адреса."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError(f"Invalid email address: {email}")
        return email
    
    def _validate_name(self, name: str) -> str:
        """Валидация имени пользователя."""
        if not name or len(name.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")
        return name.strip()
    
    def deactivate(self) -> None:
        """Деактивация пользователя."""
        self.is_active = False
    
    def create_post(self, title: str, content: str) -> 'Post':
        """Создание нового поста."""
        if not self.is_active:
            raise RuntimeError("Inactive user cannot create posts")
        
        post = Post(title, content, self)
        self._posts.append(post)
        return post
    
    @property
    def posts_count(self) -> int:
        """Количество постов пользователя."""
        return len(self._posts)

class Post:
    """Класс поста пользователя."""
    
    def __init__(self, title: str, content: str, author: User):
        self.title = title
        self.content = content
        self.author = author
        self.created_at = datetime.now()
```

```python
# test_user.py
import pytest
from datetime import datetime
from user import User, Post

class TestUser:
    """Тесты для класса User."""
    
    def test_create_user_with_valid_data(self):
        """Создание пользователя с валидными данными."""
        user = User("test@example.com", "Test User")
        
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.is_active == True
        assert isinstance(user.created_at, datetime)
        assert user.posts_count == 0
    
    def test_create_user_with_invalid_email(self):
        """Создание пользователя с невалидным email."""
        with pytest.raises(ValueError, match="Invalid email address"):
            User("invalid-email", "Test User")
    
    @pytest.mark.parametrize("invalid_email", [
        "no-at-sign",
        "@no-local-part.com",
        "no-domain@.com",
        "spaces @example.com",
        "test@",
        "",
    ])
    def test_create_user_with_various_invalid_emails(self, invalid_email):
        """Тест различных невалидных email адресов."""
        with pytest.raises(ValueError):
            User(invalid_email, "Test User")
    
    def test_create_user_with_invalid_name(self):
        """Создание пользователя с невалидным именем."""
        with pytest.raises(ValueError, match="Name must be at least 2 characters"):
            User("test@example.com", "")
    
    def test_create_user_with_short_name(self):
        """Создание пользователя со слишком коротким именем."""
        with pytest.raises(ValueError):
            User("test@example.com", "A")
    
    def test_create_user_trims_name_whitespace(self):
        """Имя пользователя очищается от пробелов."""
        user = User("test@example.com", "  Test User  ")
        assert user.name == "Test User"
    
    def test_deactivate_user(self):
        """Деактивация пользователя."""
        user = User("test@example.com", "Test User")
        user.deactivate()
        
        assert user.is_active == False
    
    def test_active_user_can_create_post(self):
        """Активный пользователь может создать пост."""
        user = User("test@example.com", "Test User")
        post = user.create_post("Test Title", "Test content")
        
        assert isinstance(post, Post)
        assert post.title == "Test Title"
        assert post.content == "Test content"
        assert post.author == user
        assert user.posts_count == 1
    
    def test_inactive_user_cannot_create_post(self):
        """Неактивный пользователь не может создать пост."""
        user = User("test@example.com", "Test User")
        user.deactivate()
        
        with pytest.raises(RuntimeError, match="Inactive user cannot create posts"):
            user.create_post("Test Title", "Test content")
    
    def test_posts_count_increases_with_new_posts(self):
        """Количество постов увеличивается при создании новых."""
        user = User("test@example.com", "Test User")
        
        assert user.posts_count == 0
        
        user.create_post("Post 1", "Content 1")
        assert user.posts_count == 1
        
        user.create_post("Post 2", "Content 2")
        assert user.posts_count == 2

class TestPost:
    """Тесты для класса Post."""
    
    @pytest.fixture
    def sample_user(self):
        """Создает тестового пользователя."""
        return User("test@example.com", "Test User")
    
    def test_create_post(self, sample_user):
        """Создание поста."""
        post = Post("Test Title", "Test content", sample_user)
        
        assert post.title == "Test Title"
        assert post.content == "Test content"
        assert post.author == sample_user
        assert isinstance(post.created_at, datetime)
```

## 📊 Параметризованные тесты

### Базовая параметризация

```python
import pytest

@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (1, 1, 2),
    (-1, 1, 0),
    (0, 0, 0),
])
def test_add_numbers(a, b, expected):
    """Тест сложения различных чисел."""
    calc = Calculator()
    result = calc.add(a, b)
    assert result == expected
```

### Параметризация с именованными тестами

```python
@pytest.mark.parametrize("email,is_valid", [
    ("test@example.com", True),
    ("user.name@domain.co.uk", True),
    ("invalid-email", False),
    ("@domain.com", False),
    ("test@", False),
], ids=[
    "valid_simple",
    "valid_complex", 
    "no_at_sign",
    "no_local_part",
    "no_domain"
])
def test_email_validation(email, is_valid):
    """Тест валидации email адресов."""
    if is_valid:
        user = User(email, "Test User")  # Должно работать
        assert user.email == email
    else:
        with pytest.raises(ValueError):
            User(email, "Test User")
```

### Комбинированная параметризация

```python
@pytest.mark.parametrize("operation", ["add", "subtract"])
@pytest.mark.parametrize("a,b", [(1, 2), (5, 3), (0, 0)])
def test_calculator_operations(operation, a, b):
    """Тест различных операций калькулятора."""
    calc = Calculator()
    
    if operation == "add":
        result = calc.add(a, b)
        expected = a + b
    elif operation == "subtract":
        result = calc.subtract(a, b)
        expected = a - b
    
    assert result == expected
```

## 🎯 Следующие шаги

В следующих главах мы детально изучим:
- Модуль unittest стандартной библиотеки Python
- Фреймворк pytest и его продвинутые возможности
- Практические паттерны тестирования

## 💡 Ключевые выводы

1. **Структура AAA** делает тесты понятными
2. **Хорошие имена тестов** — это документация
3. **Один тест = одна проверка** (в идеале)
4. **Параметризация** помогает избежать дублирования
5. **Fixtures** упрощают настройку тестов

## 🧪 Проверьте свои знания

<div class="quiz-container" id="python-testing-basics-quiz">
<script type="application/json">
{
  "title": "Основы тестирования в Python",
  "description": "Проверьте понимание фундаментальных концепций тестирования Python",
  "icon": "🐍",
  "questions": [
    {
      "question": "Какая структура теста считается лучшей практикой?",
      "type": "single",
      "options": [
        {"text": "AAA (Arrange-Act-Assert)", "correct": true},
        {"text": "Test-Check-Verify", "correct": false},
        {"text": "Setup-Test-Teardown", "correct": false},
        {"text": "Input-Process-Output", "correct": false}
      ],
      "explanation": "AAA структура (Arrange-Act-Assert) является золотым стандартом для написания понятных и поддерживаемых тестов.",
      "points": 1
    },
    {
      "question": "Какие утверждения верны для именования тестов?",
      "type": "multiple",
      "options": [
        {"text": "Имя должно начинаться с test_", "correct": true},
        {"text": "Имя должно описывать тестируемое поведение", "correct": true},
        {"text": "Имя может содержать пробелы", "correct": false},
        {"text": "Имя должно быть максимально коротким", "correct": false},
        {"text": "Имя должно отражать ожидаемый результат", "correct": true}
      ],
      "explanation": "Хорошее имя теста: test_[что_тестируем]_[сценарий]_[ожидаемый_результат]. Имя должно быть описательным и без пробелов.",
      "points": 2
    },
    {
      "question": "Как правильно проверить, что функция вызывает исключение?",
      "type": "single",
      "code": "def divide(a, b):\n    if b == 0:\n        raise ZeroDivisionError('Division by zero')\n    return a / b",
      "options": [
        {"text": "with pytest.raises(ZeroDivisionError): divide(10, 0)", "correct": true},
        {"text": "assert divide(10, 0) == ZeroDivisionError", "correct": false},
        {"text": "try: divide(10, 0); except: pass", "correct": false},
        {"text": "divide(10, 0).should_raise(ZeroDivisionError)", "correct": false}
      ],
      "explanation": "pytest.raises() - это контекстный менеджер для проверки исключений. Он проверяет, что исключение действительно возникло.",
      "points": 1
    },
    {
      "question": "Что делает pytest.approx()?",
      "type": "single",
      "options": [
        {"text": "Проверяет приблизительное равенство чисел с плавающей точкой", "correct": true},
        {"text": "Округляет числа до ближайшего целого", "correct": false},
        {"text": "Создает случайные числа для тестирования", "correct": false},
        {"text": "Преобразует числа в строки", "correct": false}
      ],
      "explanation": "pytest.approx() решает проблему точности чисел с плавающей точкой, которая может привести к неожиданным результатам в тестах.",
      "points": 1
    },
    {
      "question": "Какие методы используются для настройки и очистки в тестах?",
      "type": "multiple",
      "options": [
        {"text": "setup_method() - выполняется перед каждым тестом", "correct": true},
        {"text": "teardown_method() - выполняется после каждого теста", "correct": true},
        {"text": "@pytest.fixture - создает переиспользуемые объекты", "correct": true},
        {"text": "cleanup_method() - удаляет временные файлы", "correct": false},
        {"text": "init_method() - инициализирует тестовый класс", "correct": false}
      ],
      "explanation": "pytest предоставляет setup_method/teardown_method для настройки/очистки, а также мощную систему fixtures для создания переиспользуемых тестовых данных.",
      "points": 2
    },
    {
      "question": "Какой тест написан правильно с точки зрения структуры?",
      "type": "single",
      "code": "# Вариант A:\ndef test_user():\n    u = User('john@test.com')\n    assert u.email == 'john@test.com'\n\n# Вариант B:\ndef test_user_email_validation():\n    '''Тест валидации email пользователя.'''\n    # Arrange\n    user_email = 'john@test.com'\n    # Act\n    user = User(user_email)\n    # Assert\n    assert user.email == user_email\n\n# Вариант C:\ndef test_email():\n    User('john@test.com')",
      "options": [
        {"text": "Вариант A - слишком короткий и непонятный", "correct": false},
        {"text": "Вариант B - правильная структура AAA с описанием", "correct": true},
        {"text": "Вариант C - нет проверки результата", "correct": false},
        {"text": "Все варианты одинаково хороши", "correct": false}
      ],
      "explanation": "Хороший тест должен иметь: описательное имя, докстринг, структуру AAA и проверку результата. Вариант B соответствует всем критериям.",
      "points": 2
    }
  ]
}
</script>
</div>

---

## 🔗 Связанные темы

- **[Основы TDD](01_tdd_basics.md)** - философия и принципы TDD
- **[Цикл Red-Green-Refactor](03_red_green_refactor.md)** - применение основ тестирования в TDD
- **[Unittest модуль](05_unittest.md)** - стандартная библиотека Python для тестирования
- **[Pytest фреймворк](06_pytest.md)** - современный инструмент тестирования
- **[Практические примеры](07_practical_examples.md)** - применение на практике

**Следующая глава:** [Unittest модуль](05_unittest.md)

*🧪 Основы освоены — изучаем инструменты!*
