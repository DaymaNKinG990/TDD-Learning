# Инструменты и фреймворки для TDD в Python

## 🎯 Обзор экосистемы

Python предоставляет богатую экосистему инструментов для эффективного применения TDD. В этой главе мы рассмотрим основные инструменты, их назначение и способы интеграции в рабочий процесс.

## 🧪 Фреймворки тестирования

### 1. pytest - Король тестирования

**Почему pytest?**
- Простой и понятный синтаксис
- Богатая экосистема плагинов
- Автообнаружение тестов
- Мощные fixtures
- Отличная отчетность

```bash
# Установка
uv add pytest

# Основные плагины
uv add pytest-cov pytest-mock pytest-xdist pytest-html
```

#### Ключевые особенности:
```python
# Простые assertions
def test_simple():
    assert 2 + 2 == 4

# Fixtures для переиспользования
@pytest.fixture
def user():
    return User("test@example.com")

# Параметризация тестов
@pytest.mark.parametrize("input,expected", [
    (1, 2), (2, 3), (3, 4)
])
def test_increment(input, expected):
    assert increment(input) == expected
```

### 2. unittest - Стандартная библиотека

**Когда использовать:**
- Корпоративные проекты с строгими требованиями
- Миграция с Java/C# проектов
- Необходимость использовать только стандартную библиотеку

```python
import unittest

class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()
    
    def test_add(self):
        result = self.calc.add(2, 3)
        self.assertEqual(result, 5)
    
    def test_divide_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            self.calc.divide(10, 0)

if __name__ == '__main__':
    unittest.main()
```

### 3. doctest - Тестирование в документации

**Применение:**
- Простые примеры в документации
- Проверка актуальности примеров кода
- Быстрые smoke тесты

```python
def add(a, b):
    """
    Складывает два числа.
    
    >>> add(2, 3)
    5
    >>> add(-1, 1)
    0
    >>> add(0, 0)
    0
    """
    return a + b

# Запуск doctest
if __name__ == "__main__":
    import doctest
    doctest.testmod()
```

## 📊 Инструменты анализа покрытия

### 1. coverage.py + pytest-cov

```bash
uv add pytest-cov
```

#### Базовое использование:
```bash
# Запуск с покрытием
uv run pytest --cov=src

# HTML отчет
uv run pytest --cov=src --cov-report=html

# Проверка минимального покрытия
uv run pytest --cov=src --cov-fail-under=80

# Исключение файлов
uv run pytest --cov=src --cov-report=html --cov-config=.coveragerc
```

#### Конфигурация .coveragerc:
```ini
[run]
source = src
omit = 
    */tests/*
    */venv/*
    */migrations/*
    */settings/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError

[html]
directory = htmlcov
```

### 2. diff-cover для инкрементального покрытия

```bash
uv add diff-cover

# Покрытие только измененных строк
uv run diff-cover coverage.xml --compare-branch=main --fail-under=90
```

## 🃏 Инструменты мокирования

### 1. unittest.mock (встроенный)

```python
from unittest.mock import Mock, patch, MagicMock

def test_api_call():
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {'status': 'success'}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = fetch_user_data('123')
        
        assert result['status'] == 'success'
        mock_get.assert_called_once_with('/api/users/123')
```

### 2. pytest-mock

```bash
uv add pytest-mock
```

```python
def test_with_pytest_mock(mocker):
    # Более удобный синтаксис
    mock_db = mocker.patch('myapp.database.save')
    mock_email = mocker.patch('myapp.email.send')
    
    user_service = UserService()
    user = user_service.create_user('test@example.com')
    
    mock_db.assert_called_once()
    mock_email.assert_called_once()
```

### 3. responses для HTTP мокирования

```bash
uv add responses
```

```python
import responses
import requests

@responses.activate
def test_api_integration():
    responses.add(
        responses.GET,
        'https://api.example.com/users/123',
        json={'id': 123, 'name': 'John'},
        status=200
    )
    
    result = fetch_user_from_api('123')
    
    assert result['name'] == 'John'
```

## 🏗 Fixtures и тестовые данные

### 1. factory_boy для создания тестовых объектов

```bash
uv add factory-boy
```

```python
import factory
from myapp.models import User, Post

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    name = factory.Faker('name')
    age = factory.Faker('pyint', min_value=18, max_value=80)

class PostFactory(factory.Factory):
    class Meta:
        model = Post
    
    title = factory.Faker('sentence', nb_words=4)
    content = factory.Faker('text')
    author = factory.SubFactory(UserFactory)

# Использование в тестах
def test_user_can_create_post():
    user = UserFactory()
    post = PostFactory(author=user)
    
    assert post.author == user
    assert len(post.title) > 0
```

### 2. Faker для генерации данных

```bash
uv add faker
```

```python
from faker import Faker

fake = Faker(['en_US', 'ru_RU'])  # Поддержка локализации

@pytest.fixture
def sample_user_data():
    return {
        'email': fake.email(),
        'name': fake.name(),
        'phone': fake.phone_number(),
        'address': fake.address(),
        'birth_date': fake.date_of_birth(minimum_age=18, maximum_age=80)
    }

def test_user_creation(sample_user_data):
    user = User(**sample_user_data)
    assert user.email == sample_user_data['email']
```

### 3. model_bakery для Django моделей

```bash
uv add model-bakery
```

```python
from model_bakery import baker

def test_django_model():
    # Автоматическое создание объектов
    user = baker.make('auth.User')
    post = baker.make('blog.Post', author=user)
    
    assert post.author == user
    assert post.pk is not None
```

## 🚀 Параллельное выполнение тестов

### 1. pytest-xdist

```bash
uv add pytest-xdist

# Запуск в несколько процессов
uv run pytest -n 4

# Автоматический выбор количества процессов
uv run pytest -n auto

# Запуск на разных машинах
uv run pytest -d --tx socket=192.168.1.10//python
```

### 2. pytest-parallel

```bash
uv add pytest-parallel

# Параллельность внутри процесса
uv run pytest --workers 4
```

## 📈 Инструменты анализа производительности

### 1. pytest-benchmark

```bash
uv add pytest-benchmark
```

```python
def test_sorting_performance(benchmark):
    data = list(range(1000, 0, -1))
    
    result = benchmark(sorted, data)
    
    assert result == list(range(1, 1001))

def test_custom_algorithm_performance(benchmark):
    @benchmark
    def run_algorithm():
        return complex_algorithm(large_dataset)
    
    result = run_algorithm
    assert result is not None
```

### 2. pytest-profiling

```bash
uv add pytest-profiling

# Профилирование тестов
uv run pytest --profile
```

### 3. memory_profiler

```bash
uv add memory-profiler psutil
```

```python
from memory_profiler import profile

@profile
def test_memory_usage():
    large_list = [i for i in range(1000000)]
    del large_list
```

## 🎨 Инструменты качества кода

### 1. Black - форматирование кода

```bash
uv add black

# Форматирование
uv run black src/ tests/

# Проверка без изменений
uv run black --check src/ tests/
```

### 2. isort - сортировка импортов

```bash
uv add isort

# Сортировка импортов
uv run isort src/ tests/

# Интеграция с black
uv run isort --profile black src/ tests/
```

### 3. flake8 - линтер

```bash
uv add flake8

# Проверка кода
uv run flake8 src/ tests/
```

### 4. mypy - статическая типизация

```bash
uv add mypy

# Проверка типов
uv run mypy src/
```

### 5. pre-commit - хуки перед коммитом

```bash
uv add pre-commit

# Установка хуков
uv run pre-commit install
```

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8

  - repo: local
    hooks:
      - id: tests
        name: tests
        entry: uv run pytest
        language: system
        pass_filenames: false
        always_run: true
```

## 🌐 Веб-тестирование

### 1. Selenium для E2E тестирования

```bash
uv add selenium webdriver-manager
```

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    
    driver = webdriver.Chrome(
        ChromeDriverManager().install(),
        options=options
    )
    yield driver
    driver.quit()

def test_login_flow(driver):
    driver.get("http://localhost:8000/login")
    
    email_input = driver.find_element(By.NAME, "email")
    password_input = driver.find_element(By.NAME, "password")
    
    email_input.send_keys("test@example.com")
    password_input.send_keys("password")
    
    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    submit_button.click()
    
    assert "Dashboard" in driver.title
```

### 2. Playwright (современная альтернатива)

```bash
uv add playwright pytest-playwright

# Установка браузеров
uv run playwright install
```

```python
def test_login_with_playwright(page):
    page.goto("http://localhost:8000/login")
    
    page.fill("input[name='email']", "test@example.com")
    page.fill("input[name='password']", "password")
    page.click("button[type='submit']")
    
    expect(page).to_have_title("Dashboard")
```

### 3. requests для API тестирования

```python
import requests

@pytest.fixture
def api_client():
    return requests.Session()

def test_user_api(api_client):
    # Создание пользователя
    response = api_client.post('/api/users', json={
        'email': 'test@example.com',
        'name': 'Test User'
    })
    
    assert response.status_code == 201
    user_data = response.json()
    
    # Получение пользователя
    response = api_client.get(f'/api/users/{user_data["id"]}')
    assert response.status_code == 200
    assert response.json()['email'] == 'test@example.com'
```

## 🗄 Тестирование баз данных

### 1. pytest-postgresql

```bash
uv add pytest-postgresql
```

```python
import pytest
from pytest_postgresql import factories

postgresql_proc = factories.postgresql_proc(
    port=None, unixsocketdir='/tmp'
)
postgresql = factories.postgresql('postgresql_proc')

def test_database_operations(postgresql):
    cursor = postgresql.cursor()
    cursor.execute("CREATE TABLE test (id serial PRIMARY KEY, name text)")
    cursor.execute("INSERT INTO test (name) VALUES ('test_name')")
    
    cursor.execute("SELECT name FROM test WHERE id = 1")
    result = cursor.fetchone()
    
    assert result[0] == 'test_name'
```

### 2. SQLAlchemy с тестовой БД

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def engine():
    return create_engine("sqlite:///:memory:")

@pytest.fixture
def db_session(engine):
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)

def test_user_repository(db_session):
    repo = UserRepository(db_session)
    
    user = User(email="test@example.com", name="Test")
    saved_user = repo.save(user)
    
    assert saved_user.id is not None
    
    found_user = repo.find_by_email("test@example.com")
    assert found_user.name == "Test"
```

## 🔧 CI/CD интеграция

### 1. GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11, 3.12]

    steps:
    - uses: actions/checkout@v3
    
    - name: Install uv
      uses: astral-sh/setup-uv@v1
      
    - name: Set up Python ${{ python_version_matrix }}
      run: uv python install ${{ python_version_matrix }}
      
    - name: Install dependencies
      run: uv sync
      
    - name: Run tests
      run: |
        uv run pytest --cov=src --cov-report=xml
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### 2. GitLab CI

```yaml
# .gitlab-ci.yml
image: python:3.11

stages:
  - test
  - quality

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - .venv/

before_script:
  - curl -LsSf https://astral.sh/uv/install.sh | sh
  - export PATH="$HOME/.cargo/bin:$PATH"
  - uv sync

test:
  stage: test
  script:
    - uv run pytest --cov=src --cov-report=xml --cov-report=html
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    paths:
      - htmlcov/

quality:
  stage: quality
  script:
    - uv run black --check src/ tests/
    - uv run isort --check-only src/ tests/
    - uv run flake8 src/ tests/
    - uv run mypy src/
```

## 📊 Отчетность и мониторинг

### 1. pytest-html для HTML отчетов

```bash
uv add pytest-html

# Генерация HTML отчета
uv run pytest --html=report.html --self-contained-html
```

### 2. allure для красивых отчетов

```bash
uv add allure-pytest

# Генерация данных для allure
uv run pytest --alluredir=allure-results

# Просмотр отчета
allure serve allure-results
```

```python
import allure

@allure.feature("User Management")
@allure.story("User Registration")
def test_user_registration():
    with allure.step("Create user data"):
        user_data = {"email": "test@example.com", "name": "Test"}
    
    with allure.step("Register user"):
        user = register_user(user_data)
    
    with allure.step("Verify user is created"):
        assert user.id is not None
        assert user.email == user_data["email"]
```

## 🎯 Рекомендуемый стек инструментов

### Для небольших проектов:
```bash
uv add pytest pytest-cov black isort
```

### Для средних проектов:
```bash
uv add pytest pytest-cov pytest-mock pytest-xdist
uv add black isort flake8 mypy
uv add factory-boy faker
```

### Для крупных проектов:
```bash
# Тестирование
uv add pytest pytest-cov pytest-mock pytest-xdist pytest-html
uv add factory-boy faker responses

# Качество кода  
uv add black isort flake8 mypy pre-commit

# Производительность
uv add pytest-benchmark pytest-profiling

# Веб-тестирование
uv add selenium playwright pytest-playwright

# Отчетность
uv add allure-pytest
```

## 🎯 Следующие шаги

В заключительной главе мы подведем итоги курса и предоставим ресурсы для дальнейшего изучения TDD.

## 🧪 Проверьте свои знания

<div class="quiz-container" id="tools-frameworks-quiz">
<script type="application/json">
{
  "title": "Инструменты и фреймворки TDD",
  "description": "Проверьте знание экосистемы инструментов для TDD в Python",
  "icon": "🔧",
  "questions": [
    {
      "question": "Какие инструменты входят в современный стек качества кода? (выберите все правильные)",
      "type": "multiple",
      "options": [
        {"text": "ruff - быстрый линтер и форматер", "correct": true},
        {"text": "mypy - проверка типов", "correct": true},
        {"text": "pre-commit - git хуки", "correct": true},
        {"text": "pytest-cov - покрытие кода", "correct": true},
        {"text": "pylint - альтернативный линтер", "correct": false}
      ],
      "explanation": "Современный стек включает ruff (заменяет black+isort+flake8), mypy, pre-commit и pytest-cov. pylint менее популярен в современной разработке.",
      "points": 2
    },
    {
      "question": "Что делает pytest-xdist?",
      "type": "single",
      "options": [
        {"text": "Создает отчеты о покрытии", "correct": false},
        {"text": "Запускает тесты параллельно", "correct": true},
        {"text": "Мокирует внешние зависимости", "correct": false},
        {"text": "Генерирует тестовые данные", "correct": false}
      ],
      "explanation": "pytest-xdist позволяет запускать тесты параллельно на нескольких процессорах или машинах, значительно ускоряя выполнение большого количества тестов.",
      "points": 1
    },
    {
      "question": "Какие библиотеки помогают создавать тестовые данные?",
      "type": "multiple",
      "options": [
        {"text": "factory-boy - фабрики объектов", "correct": true},
        {"text": "faker - генерация реалистичных данных", "correct": true},
        {"text": "responses - мокирование HTTP запросов", "correct": false},
        {"text": "pytest-mock - мокирование объектов", "correct": false}
      ],
      "explanation": "factory-boy создает фабрики для генерации объектов, faker генерирует реалистичные данные (имена, адреса). responses и pytest-mock предназначены для мокирования.",
      "points": 2
    },
    {
      "question": "Что такое pre-commit хуки?",
      "type": "single",
      "options": [
        {"text": "Автоматические тесты после коммита", "correct": false},
        {"text": "Проверки кода перед коммитом в git", "correct": true},
        {"text": "Резервное копирование кода", "correct": false},
        {"text": "Автоматическое форматирование в IDE", "correct": false}
      ],
      "explanation": "Pre-commit хуки автоматически запускают линтеры, форматеры и тесты перед каждым git коммитом, предотвращая попадание некачественного кода в репозиторий.",
      "points": 1
    },
    {
      "question": "Какая команда правильно запускает тесты с покрытием и параллельно?",
      "type": "single",
      "options": [
        {"text": "pytest --cov=src -n auto", "correct": true},
        {"text": "pytest --coverage --parallel", "correct": false},
        {"text": "python -m pytest --cov --xdist", "correct": false},
        {"text": "uv test --coverage --jobs=4", "correct": false}
      ],
      "explanation": "Правильная команда: pytest --cov=src (покрытие для папки src) -n auto (автоматическое определение количества процессов для параллельного выполнения).",
      "points": 1
    },
    {
      "question": "Для чего используется pytest-benchmark?",
      "type": "single",
      "options": [
        {"text": "Тестирование производительности кода", "correct": true},
        {"text": "Сравнение результатов тестов", "correct": false},
        {"text": "Создание бенчмарков для базы данных", "correct": false},
        {"text": "Измерение покрытия кода", "correct": false}
      ],
      "explanation": "pytest-benchmark предоставляет fixture для измерения времени выполнения кода, статистики производительности и сравнения результатов между запусками.",
      "points": 1
    }
  ]
}
</script>
</div>

---

## 🔗 Связанные темы

- **[Настройка окружения](02_environment_setup.md)** - установка инструментов
- **[Pytest фреймворк](06_pytest.md)** - основной инструмент тестирования
- **[Лучшие практики](12_best_practices.md)** - как правильно использовать инструменты
- **[CI/CD и автоматизация](14_ci_cd_automation.md)** - автоматизация с инструментами
- **[Метрики покрытия кода](16_code_coverage_metrics.md)** - инструменты для метрик
- **[Стратегии работы с Legacy Code](17_legacy_code_strategies.md)** - инструменты для legacy кода

**Следующая глава:** [CI/CD и автоматизация](14_ci_cd_automation.md)

*🔧 Инструменты изучены — время применять их в реальных проектах!*
