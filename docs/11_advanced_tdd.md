# Продвинутые техники TDD

## 🎯 Введение в продвинутые техники

После освоения базовых принципов TDD настало время изучить более сложные и специализированные техники. В этой главе мы рассмотрим BDD, архитектурные тесты, тестирование производительности и другие продвинутые подходы.

## 🎭 Behavior-Driven Development (BDD)

BDD расширяет TDD, фокусируясь на поведении системы с точки зрения пользователя.

### Gherkin синтаксис

```gherkin
# features/user_registration.feature
Feature: User Registration
  As a visitor
  I want to register an account
  So that I can access the application

  Scenario: Successful registration
    Given I am on the registration page
    When I fill in the registration form with valid data
    And I submit the form
    Then I should see a success message
    And I should receive a confirmation email

  Scenario: Registration with invalid email
    Given I am on the registration page
    When I fill in the registration form with invalid email
    And I submit the form
    Then I should see an error message
    And I should not receive a confirmation email
```

### Реализация с behave

```bash
uv add behave
```

```python
# features/steps/user_registration.py
from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By

@given('I am on the registration page')
def step_on_registration_page(context):
    context.driver = webdriver.Chrome()
    context.driver.get('http://localhost:8000/register')

@when('I fill in the registration form with valid data')
def step_fill_valid_data(context):
    context.driver.find_element(By.NAME, 'email').send_keys('test@example.com')
    context.driver.find_element(By.NAME, 'password').send_keys('password123')
    context.driver.find_element(By.NAME, 'confirm_password').send_keys('password123')

@when('I submit the form')
def step_submit_form(context):
    context.driver.find_element(By.XPATH, "//button[@type='submit']").click()

@then('I should see a success message')
def step_see_success_message(context):
    success_element = context.driver.find_element(By.CLASS_NAME, 'success-message')
    assert 'Registration successful' in success_element.text
```

### BDD с pytest-bdd

```bash
uv add pytest-bdd
```

```python
# tests/bdd/test_user_registration.py
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from myapp import create_app
from myapp.models import User

scenarios('features/user_registration.feature')

@pytest.fixture
def app():
    return create_app({'TESTING': True})

@pytest.fixture
def client(app):
    return app.test_client()

@given('I am a new user')
def new_user():
    return {'email': 'test@example.com', 'password': 'password123'}

@when(parsers.parse('I register with email "{email}"'))
def register_user(client, email):
    return client.post('/register', data={
        'email': email,
        'password': 'password123'
    })

@then('I should be successfully registered')
def check_registration(response):
    assert response.status_code == 201
    user = User.query.filter_by(email='test@example.com').first()
    assert user is not None
```

## 🏛 Архитектурные тесты

Тесты, которые проверяют соблюдение архитектурных принципов.

### Тестирование зависимостей

```python
# tests/architecture/test_dependencies.py
import ast
import os
from pathlib import Path

def test_domain_has_no_infrastructure_dependencies():
    """Доменный слой не должен зависеть от инфраструктуры."""
    domain_path = Path('src/domain')
    
    for python_file in domain_path.glob('**/*.py'):
        with open(python_file, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith('infrastructure'), \
                        f"Domain module {python_file} imports infrastructure: {alias.name}"
            
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith('infrastructure'):
                    raise AssertionError(
                        f"Domain module {python_file} imports from infrastructure: {node.module}"
                    )

def test_no_circular_dependencies():
    """Проверка отсутствия циклических зависимостей."""
    import_graph = {}
    
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                module_path = os.path.join(root, file)
                imports = extract_imports(module_path)
                module_name = path_to_module_name(module_path)
                import_graph[module_name] = imports
    
    # Проверяем циклы
    visited = set()
    rec_stack = set()
    
    def has_cycle(node):
        if node in rec_stack:
            return True
        if node in visited:
            return False
        
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in import_graph.get(node, []):
            if has_cycle(neighbor):
                return True
        
        rec_stack.remove(node)
        return False
    
    for module in import_graph:
        assert not has_cycle(module), f"Circular dependency detected involving {module}"
```

### Тестирование принципов SOLID

```python
def test_interface_segregation_principle():
    """Интерфейсы должны быть сфокированными."""
    from domain.interfaces import UserRepository
    
    methods = [method for method in dir(UserRepository) 
               if not method.startswith('_')]
    
    # Проверяем что интерфейс не слишком большой
    assert len(methods) <= 10, f"UserRepository interface too large: {len(methods)} methods"
    
    # Проверяем что методы логически связаны
    user_methods = [m for m in methods if 'user' in m.lower()]
    assert len(user_methods) / len(methods) >= 0.8, "Interface not cohesive"

def test_dependency_inversion_principle():
    """Высокоуровневые модули не должны зависеть от низкоуровневых."""
    import inspect
    from domain.services import UserService
    
    # Получаем зависимости конструктора
    signature = inspect.signature(UserService.__init__)
    
    for param_name, param in signature.parameters.items():
        if param_name != 'self':
            # Проверяем что зависимость - это абстракция (интерфейс)
            assert hasattr(param.annotation, '__abstractmethods__'), \
                f"UserService depends on concrete class: {param.annotation}"
```

## ⚡ Тестирование производительности

### Базовые тесты производительности

```python
import time
import pytest
from memory_profiler import profile

def test_user_creation_performance():
    """Тест производительности создания пользователя."""
    from domain.services import UserService
    
    service = UserService()
    
    start_time = time.time()
    
    # Создаем 1000 пользователей
    for i in range(1000):
        service.create_user(f"user{i}@example.com", f"User {i}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Должно выполниться менее чем за 5 секунд
    assert duration < 5.0, f"User creation too slow: {duration}s"

@profile
def test_memory_usage():
    """Тест использования памяти."""
    data = []
    
    # Создаем большой объем данных
    for i in range(100000):
        data.append({'id': i, 'name': f'Item {i}'})
    
    # Обрабатываем данные
    processed = [item for item in data if item['id'] % 2 == 0]
    
    assert len(processed) == 50000

def test_database_query_performance(db_session):
    """Тест производительности запросов к БД."""
    from models import User
    
    # Создаем тестовые данные
    users = [User(email=f"user{i}@example.com") for i in range(1000)]
    db_session.bulk_save_objects(users)
    db_session.commit()
    
    # Тестируем производительность запроса
    start_time = time.time()
    
    result = db_session.query(User).filter(
        User.email.like('%100%')
    ).all()
    
    end_time = time.time()
    duration = end_time - start_time
    
    assert duration < 0.1, f"Query too slow: {duration}s"
    assert len(result) > 0
```

### Профилирование с pytest-benchmark

```python
import pytest

def fibonacci(n):
    """Функция для тестирования производительности."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def fibonacci_optimized(n, memo=None):
    """Оптимизированная версия."""
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci_optimized(n-1, memo) + fibonacci_optimized(n-2, memo)
    return memo[n]

def test_fibonacci_performance(benchmark):
    """Тест производительности fibonacci."""
    result = benchmark(fibonacci, 20)
    assert result == 6765

def test_fibonacci_optimized_performance(benchmark):
    """Тест оптимизированной версии."""
    result = benchmark(fibonacci_optimized, 20)
    assert result == 6765

def test_compare_algorithms(benchmark):
    """Сравнение алгоритмов."""
    @benchmark
    def run_fibonacci():
        return fibonacci(15)
    
    result = run_fibonacci
    assert result == 610

# Запуск: uv run pytest --benchmark-compare
```

## 🔧 Property-Based Testing

Тестирование свойств с помощью Hypothesis.

```bash
uv add hypothesis
```

```python
from hypothesis import given, strategies as st
import pytest

def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

@given(st.integers(), st.integers())
def test_add_commutative(a, b):
    """Сложение коммутативно."""
    assert add(a, b) == add(b, a)

@given(st.integers(), st.integers(), st.integers())
def test_add_associative(a, b, c):
    """Сложение ассоциативно."""
    assert add(add(a, b), c) == add(a, add(b, c))

@given(st.integers())
def test_add_identity(a):
    """Ноль - нейтральный элемент сложения."""
    assert add(a, 0) == a
    assert add(0, a) == a

@given(st.text())
def test_string_operations(s):
    """Тестирование операций со строками."""
    # Длина не изменяется при конкатенации с пустой строкой
    assert len(s + "") == len(s)
    
    # Обращение дважды возвращает исходную строку
    assert s[::-1][::-1] == s

@given(st.lists(st.integers()))
def test_sort_properties(lst):
    """Свойства сортировки."""
    sorted_lst = sorted(lst)
    
    # Длина не изменяется
    assert len(sorted_lst) == len(lst)
    
    # Все элементы сохраняются
    assert sorted(lst) == sorted(sorted_lst)
    
    # Результат отсортирован
    for i in range(len(sorted_lst) - 1):
        assert sorted_lst[i] <= sorted_lst[i + 1]

# Тестирование пользовательских типов
class BankAccount:
    def __init__(self, balance=0):
        self.balance = balance
    
    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.balance += amount
    
    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount

@given(st.floats(min_value=0.01, max_value=1000000))
def test_account_deposit_increases_balance(amount):
    """Пополнение увеличивает баланс."""
    account = BankAccount(100)
    initial_balance = account.balance
    
    account.deposit(amount)
    
    assert account.balance == initial_balance + amount

@given(
    st.floats(min_value=100, max_value=1000),
    st.floats(min_value=1, max_value=99)
)
def test_account_withdraw_decreases_balance(initial_balance, amount):
    """Снятие уменьшает баланс."""
    account = BankAccount(initial_balance)
    
    account.withdraw(amount)
    
    assert account.balance == initial_balance - amount
```

## 🧪 Mutation Testing

Тестирование качества тестов путем введения мутаций в код.

```bash
uv add mutmut
```

```python
# src/calculator.py
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b

# tests/test_calculator.py
import pytest
from src.calculator import add, subtract, multiply, divide

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 0) == 0
    assert subtract(-1, -1) == 0

def test_multiply():
    assert multiply(3, 4) == 12
    assert multiply(0, 5) == 0
    assert multiply(-2, 3) == -6

def test_divide():
    assert divide(10, 2) == 5
    assert divide(7, 2) == 3.5
    
def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

```bash
# Запуск mutation testing
uv run mutmut run --paths-to-mutate src/

# Просмотр результатов
uv run mutmut results

# Просмотр конкретной мутации
uv run mutmut show 1
```

## 🔄 Contract Testing

Тестирование контрактов между сервисами.

```python
# contracts/user_service_contract.py
from abc import ABC, abstractmethod
from typing import List, Optional

class UserServiceContract(ABC):
    """Контракт для сервиса пользователей."""
    
    @abstractmethod
    def create_user(self, email: str, name: str) -> 'User':
        """Создание пользователя."""
        pass
    
    @abstractmethod
    def find_user_by_email(self, email: str) -> Optional['User']:
        """Поиск пользователя по email."""
        pass
    
    @abstractmethod
    def get_all_users(self) -> List['User']:
        """Получение всех пользователей."""
        pass

# tests/contract_tests.py
import pytest
from contracts.user_service_contract import UserServiceContract

class ContractTestSuite:
    """Базовый набор тестов для контракта."""
    
    @pytest.fixture
    def service(self) -> UserServiceContract:
        """Реализация сервиса для тестирования."""
        raise NotImplementedError("Subclasses must implement this")
    
    def test_create_user(self, service):
        """Тест создания пользователя."""
        user = service.create_user("test@example.com", "Test User")
        
        assert user is not None
        assert user.email == "test@example.com"
        assert user.name == "Test User"
    
    def test_find_user_by_email(self, service):
        """Тест поиска пользователя."""
        # Создаем пользователя
        created_user = service.create_user("test@example.com", "Test User")
        
        # Находим его
        found_user = service.find_user_by_email("test@example.com")
        
        assert found_user is not None
        assert found_user.email == created_user.email
    
    def test_find_nonexistent_user(self, service):
        """Тест поиска несуществующего пользователя."""
        user = service.find_user_by_email("nonexistent@example.com")
        assert user is None

class TestDatabaseUserService(ContractTestSuite):
    """Тесты для реализации с БД."""
    
    @pytest.fixture
    def service(self):
        from implementations.database_user_service import DatabaseUserService
        return DatabaseUserService(test_database_url)

class TestMemoryUserService(ContractTestSuite):
    """Тесты для реализации в памяти."""
    
    @pytest.fixture
    def service(self):
        from implementations.memory_user_service import MemoryUserService
        return MemoryUserService()
```

## 🎭 Test Doubles Patterns

Продвинутые паттерны тестовых дублеров.

### Builder Pattern для сложных моков

```python
class MockHttpResponseBuilder:
    """Строитель для HTTP ответов."""
    
    def __init__(self):
        self.mock_response = Mock()
        self.mock_response.status_code = 200
        self.mock_response.headers = {}
        self.mock_response.json.return_value = {}
    
    def status(self, code):
        self.mock_response.status_code = code
        return self
    
    def json_data(self, data):
        self.mock_response.json.return_value = data
        return self
    
    def header(self, key, value):
        self.mock_response.headers[key] = value
        return self
    
    def build(self):
        return self.mock_response

def test_api_client_with_builder(mocker):
    """Тест с использованием builder для мока."""
    mock_response = (MockHttpResponseBuilder()
                     .status(201)
                     .json_data({"id": 123, "name": "Test User"})
                     .header("Content-Type", "application/json")
                     .build())
    
    mocker.patch('requests.post', return_value=mock_response)
    
    client = APIClient()
    result = client.create_user("test@example.com", "Test User")
    
    assert result["id"] == 123
    assert result["name"] == "Test User"
```

### Fake с реалистичным поведением

```python
class FakeEmailService:
    """Реалистичная подделка email сервиса."""
    
    def __init__(self):
        self.sent_emails = []
        self.failure_rate = 0  # Процент неудач
        self.delay = 0  # Задержка в секундах
    
    def set_failure_rate(self, rate):
        """Установить процент неудач."""
        self.failure_rate = rate
    
    def set_delay(self, seconds):
        """Установить задержку отправки."""
        self.delay = seconds
    
    def send_email(self, to, subject, body):
        """Отправка email с реалистичным поведением."""
        import random
        import time
        
        # Имитируем задержку
        time.sleep(self.delay)
        
        # Имитируем случайные неудачи
        if random.random() < self.failure_rate:
            raise EmailSendError("Failed to send email")
        
        # Имитируем валидацию email
        if "@" not in to:
            raise EmailValidationError("Invalid email address")
        
        # Сохраняем отправленный email
        self.sent_emails.append({
            'to': to,
            'subject': subject,
            'body': body,
            'timestamp': time.time()
        })
        
        return True
    
    def get_sent_emails(self, to=None):
        """Получить отправленные emails."""
        if to:
            return [email for email in self.sent_emails if email['to'] == to]
        return self.sent_emails

def test_email_service_reliability():
    """Тест надежности email сервиса."""
    fake_email = FakeEmailService()
    fake_email.set_failure_rate(0.1)  # 10% неудач
    
    notification_service = NotificationService(fake_email)
    
    successes = 0
    failures = 0
    
    for i in range(100):
        try:
            notification_service.send_welcome_email(f"user{i}@example.com")
            successes += 1
        except EmailSendError:
            failures += 1
    
    # Проверяем что сервис справляется с неудачами
    assert successes > 80  # Большинство отправок успешны
    assert failures > 0    # Но есть и неудачи
```

## 🎯 Следующие шаги

Теперь у вас есть знания о продвинутых техниках TDD! В следующей главе мы изучим лучшие практики и типичные антипаттерны.

## 🧪 Проверьте свои знания

<div class="quiz-container" id="advanced-tdd-quiz">
<script type="application/json">
{
  "title": "Продвинутые техники TDD",
  "description": "Проверьте знание BDD, архитектурных тестов и продвинутых паттернов",
  "icon": "🚀",
  "questions": [
    {
      "question": "Что означает аббревиатура BDD?",
      "type": "single",
      "options": [
        {"text": "Big Data Development", "correct": false},
        {"text": "Behavior-Driven Development", "correct": true},
        {"text": "Backend Development Design", "correct": false},
        {"text": "Binary Decision Diagrams", "correct": false}
      ],
      "explanation": "BDD расшифровывается как Behavior-Driven Development - методология разработки, основанная на поведении, которая расширяет TDD, фокусируясь на понимании поведения системы.",
      "points": 1
    },
    {
      "question": "Какие ключевые слова используются в Gherkin синтаксисе? (выберите все правильные)",
      "type": "multiple",
      "options": [
        {"text": "Given - предварительные условия", "correct": true},
        {"text": "When - действие пользователя", "correct": true},
        {"text": "Then - ожидаемый результат", "correct": true},
        {"text": "And/But - дополнительные условия", "correct": true},
        {"text": "If/Else - условные операторы", "correct": false}
      ],
      "explanation": "Gherkin использует Given (дано), When (когда), Then (тогда), And/But (и/но) для описания сценариев. If/Else не являются ключевыми словами Gherkin.",
      "points": 2
    },
    {
      "question": "Что такое Property-Based Testing?",
      "type": "single",
      "options": [
        {"text": "Тестирование свойств объектов", "correct": false},
        {"text": "Автоматическая генерация тестовых данных для проверки инвариантов", "correct": true},
        {"text": "Тестирование недвижимости", "correct": false},
        {"text": "Проверка конфигурационных файлов", "correct": false}
      ],
      "explanation": "Property-Based Testing автоматически генерирует множество тестовых случаев для проверки, что определенные свойства (инварианты) системы выполняются для широкого спектра входных данных.",
      "points": 1
    },
    {
      "question": "Какие техники относятся к архитектурному тестированию?",
      "type": "multiple",
      "options": [
        {"text": "Проверка зависимостей между модулями", "correct": true},
        {"text": "Тестирование соблюдения слоевой архитектуры", "correct": true},
        {"text": "Проверка метрик качества кода", "correct": true},
        {"text": "Валидация API контрактов", "correct": true},
        {"text": "Тестирование UI компонентов", "correct": false}
      ],
      "explanation": "Архитектурное тестирование включает проверку зависимостей, слоев, метрик кода и API контрактов. UI тестирование относится к функциональному тестированию.",
      "points": 2
    },
    {
      "question": "Что измеряет Mutation Testing?",
      "type": "single",
      "options": [
        {"text": "Скорость выполнения тестов", "correct": false},
        {"text": "Качество тестов через внесение мутаций в код", "correct": true},
        {"text": "Покрытие кода тестами", "correct": false},
        {"text": "Количество багов в коде", "correct": false}
      ],
      "explanation": "Mutation Testing вносит небольшие изменения (мутации) в код и проверяет, обнаруживают ли тесты эти изменения. Это помогает оценить качество тестов.",
      "points": 1
    },
    {
      "question": "Какие преимущества дает Hypothesis в Python тестировании?",
      "type": "multiple",
      "options": [
        {"text": "Автоматическая генерация тестовых данных", "correct": true},
        {"text": "Минимизация падающих примеров", "correct": true},
        {"text": "Обнаружение крайних случаев", "correct": true},
        {"text": "Статистический анализ тестов", "correct": true},
        {"text": "Автоматическое написание тестов", "correct": false}
      ],
      "explanation": "Hypothesis автогенерирует данные, минимизирует падающие примеры, находит edge cases и предоставляет статистику. Но не пишет тесты автоматически - это делает разработчик.",
      "points": 2
    }
  ]
}
</script>
</div>

## 🚀 Интерактивная практика

### 🧪 Property-Based тестирование с Hypothesis

Давайте освоим продвинутые техники тестирования на практике!

{{ create_exercise_form(
    "hypothesis_testing",
    "Property-Based тестирование",
    "Создайте property-based тесты с использованием Hypothesis для проверки математических свойств.",
    """# Установите Hypothesis
# uv add hypothesis

# Создайте модуль math_ops.py
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

# Создайте тесты test_properties.py
from hypothesis import given, strategies as st
from math_ops import add, multiply

@given(a=st.integers(), b=st.integers())
def test_add_commutative(a, b):
    assert add(a, b) == add(b, a)

@given(a=st.integers())
def test_multiply_by_zero(a):
    assert multiply(a, 0) == 0

# Запустите: uv run pytest test_properties.py -v""",
    [
        "Установите Hypothesis",
        "Создайте модуль с математическими функциями",
        "Напишите property-based тесты",
        "Запустите тесты и изучите генерацию данных"
    ]
) }}

---

## 🔗 Связанные темы

- **[TDD в веб-разработке](10_web_development_tdd.md)** - применение продвинутых техник в веб-приложениях
- **[Лучшие практики](12_best_practices.md)** - когда использовать продвинутые техники
- **[TDD и архитектура](19_tdd_architecture.md)** - архитектурные тесты и BDD
- **[Метрики покрытия кода](16_code_coverage_metrics.md)** - измерение качества продвинутых тестов
- **[Инструменты и фреймворки](13_tools_frameworks.md)** - инструменты для продвинутых техник
- **[CI/CD и автоматизация](14_ci_cd_automation.md)** - автоматизация продвинутых тестов

**Следующая глава:** [Лучшие практики и антипаттерны](12_best_practices.md)

*🚀 Продвинутые техники освоены — применяйте их мудро!*
