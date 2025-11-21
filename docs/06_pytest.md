# Pytest: Мощный фреймворк тестирования

## 🎯 Почему pytest?

Pytest — это де-факто стандарт тестирования в Python сообществе. Он сочетает простоту использования с мощными возможностями и является идеальным инструментом для TDD.

### Преимущества pytest:
- 🎯 **Простой синтаксис** — используйте обычные `assert`
- 🔧 **Автообнаружение** тестов
- 🏗 **Мощные fixtures** для настройки тестов
- 📊 **Детальные отчеты** о падениях
- 🔌 **Богатая экосистема** плагинов
- ⚡ **Параллельное выполнение** тестов
- 📈 **Покрытие кода** из коробки

## 🚀 Начало работы с pytest

### Установка
```bash
uv add pytest
uv add pytest-cov      # Покрытие кода
uv add pytest-mock     # Мокирование
uv add pytest-xdist    # Параллельные тесты
```

### Первый тест
```python
# test_hello.py
def test_hello_world():
    assert "hello" == "hello"

def test_math():
    assert 2 + 2 == 4
```

### Запуск тестов
```bash
# Запуск всех тестов
uv run pytest

# Подробный вывод
uv run pytest -v

# Остановка на первом падении
uv run pytest -x

# Запуск конкретного файла
uv run pytest test_hello.py

# Запуск конкретного теста
uv run pytest test_hello.py::test_math
```

## 🏗 Fixtures: Основа pytest

Fixtures — это функции, которые предоставляют данные или ресурсы для тестов.

### Базовые fixtures

```python
import pytest

@pytest.fixture
def sample_data():
    """Возвращает тестовые данные."""
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30
    }

def test_user_creation(sample_data):
    """Тест создания пользователя с fixture."""
    user = User(sample_data["name"], sample_data["email"])
    assert user.name == sample_data["name"]
    assert user.email == sample_data["email"]
```

### Fixtures с очисткой

```python
import tempfile
import shutil

@pytest.fixture
def temp_directory():
    """Создает временную директорию."""
    # Setup
    temp_dir = tempfile.mkdtemp()
    
    # Возвращаем ресурс
    yield temp_dir
    
    # Teardown (выполняется после теста)
    shutil.rmtree(temp_dir)

def test_file_operations(temp_directory):
    """Тест операций с файлами."""
    file_path = os.path.join(temp_directory, "test.txt")
    
    with open(file_path, "w") as f:
        f.write("Hello World")
    
    assert os.path.exists(file_path)
    # temp_directory будет автоматически удален
```

### Scope fixtures

```python
@pytest.fixture(scope="function")  # По умолчанию, создается для каждого теста
def function_fixture():
    return "function level"

@pytest.fixture(scope="class")  # Один на весь класс тестов
def class_fixture():
    return "class level"

@pytest.fixture(scope="module")  # Один на весь модуль
def module_fixture():
    return "module level"

@pytest.fixture(scope="session")  # Один на всю сессию тестирования
def session_fixture():
    return "session level"
```

### Автоиспользуемые fixtures

```python
@pytest.fixture(autouse=True)
def reset_database():
    """Автоматически очищает БД перед каждым тестом."""
    database.clear()
    yield
    database.clear()

# Этот fixture будет использован автоматически
def test_user_creation():
    user = create_user("test@example.com")
    assert user.id is not None
```

## 📋 Конфигурация conftest.py

Файл `conftest.py` содержит общие fixtures и конфигурацию для тестов.

```python
# conftest.py
import pytest
from myapp import create_app, db
from myapp.models import User

@pytest.fixture(scope="session")
def app():
    """Создает приложение для тестирования."""
    app = create_app(testing=True)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Создает тестового клиента."""
    return app.test_client()

@pytest.fixture
def sample_user(app):
    """Создает тестового пользователя в БД."""
    with app.app_context():
        user = User(email="test@example.com", name="Test User")
        db.session.add(user)
        db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()

@pytest.fixture
def auth_headers(sample_user):
    """Создает заголовки авторизации."""
    token = generate_token(sample_user)
    return {"Authorization": f"Bearer {token}"}
```

## 📊 Параметризация тестов

### Базовая параметризация

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (3, 9),
    (4, 16),
    (5, 25),
])
def test_square(input, expected):
    """Тест функции квадрата."""
    assert square(input) == expected
```

### Множественная параметризация

```python
@pytest.mark.parametrize("base", [2, 3, 5])
@pytest.mark.parametrize("exponent", [2, 3, 4])
def test_power(base, exponent):
    """Тест функции возведения в степень."""
    result = power(base, exponent)
    expected = base ** exponent
    assert result == expected
```

### Параметризация с pytest.param

```python
@pytest.mark.parametrize("test_input,expected", [
    pytest.param(
        "valid@email.com", 
        True, 
        id="valid_email"
    ),
    pytest.param(
        "invalid-email", 
        False, 
        id="invalid_email"
    ),
    pytest.param(
        "edge@case.co.uk", 
        True, 
        id="complex_domain",
        marks=pytest.mark.slow
    ),
])
def test_email_validation(test_input, expected):
    """Тест валидации email."""
    assert is_valid_email(test_input) == expected
```

### Параметризация fixtures

```python
@pytest.fixture(params=[
    "sqlite:///:memory:",
    "postgresql://test:test@localhost/test_db"
])
def database_url(request):
    """Тестирование с разными БД."""
    return request.param

def test_user_creation(database_url):
    """Тест создания пользователя в разных БД."""
    db = Database(database_url)
    user = db.create_user("test@example.com")
    assert user.id is not None
```

## 🏷 Маркеры (Markers)

Маркеры позволяют группировать и фильтровать тесты.

### Встроенные маркеры

```python
import pytest

@pytest.mark.skip(reason="Не реализовано")
def test_future_feature():
    """Этот тест будет пропущен."""
    pass

@pytest.mark.skipif(sys.version_info < (3, 12), reason="Требует Python 3.12+")
def test_new_syntax():
    """Пропускается на старых версиях Python."""
    pass

@pytest.mark.xfail(reason="Известный баг")
def test_known_bug():
    """Тест ожидаемо падает."""
    assert False

@pytest.mark.xfail(strict=True)
def test_should_fail():
    """Тест должен падать, иначе ошибка."""
    pass
```

### Кастомные маркеры

```python
# pytest.ini или pyproject.toml
[tool.pytest.ini_options]
markers = [
    "slow: медленные тесты",
    "integration: интеграционные тесты",
    "unit: модульные тесты",
    "api: тесты API",
    "smoke: дымовые тесты"
]
```

```python
import pytest

@pytest.mark.unit
def test_fast_function():
    """Быстрый unit тест."""
    assert add(2, 3) == 5

@pytest.mark.slow
@pytest.mark.integration  
def test_database_connection():
    """Медленный интеграционный тест."""
    db = connect_to_database()
    assert db.is_connected()

@pytest.mark.api
def test_user_endpoint():
    """Тест API endpoint."""
    response = client.get("/api/users")
    assert response.status_code == 200
```

### Запуск тестов по маркерам

```bash
# Только unit тесты
uv run pytest -m unit

# Исключить медленные тесты
uv run pytest -m "not slow"

# Комбинация маркеров
uv run pytest -m "unit and not slow"

# API тесты или интеграционные
uv run pytest -m "api or integration"
```

## 🔧 Плагины pytest

### pytest-cov: Покрытие кода

```bash
uv add pytest-cov

# Запуск с покрытием
uv run pytest --cov=src

# HTML отчет
uv run pytest --cov=src --cov-report=html

# Минимальный процент покрытия
uv run pytest --cov=src --cov-fail-under=90
```

### pytest-mock: Мокирование

```bash
uv add pytest-mock
```

```python
def test_api_call(mocker):
    """Тест с мокированием API вызова."""
    # Мокируем внешний API
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"status": "success"}
    mock_response.status_code = 200
    
    mocker.patch("requests.get", return_value=mock_response)
    
    # Тестируем нашу функцию
    result = fetch_user_data("123")
    assert result["status"] == "success"

def test_database_save(mocker):
    """Тест с мокированием БД."""
    mock_db = mocker.patch("myapp.database.save")
    
    user = User("test@example.com")
    user.save()
    
    mock_db.assert_called_once_with(user)
```

### pytest-xdist: Параллельные тесты

```bash
uv add pytest-xdist

# Запуск в 4 процесса
uv run pytest -n 4

# Автоматический выбор количества процессов
uv run pytest -n auto
```

### pytest-benchmark: Тесты производительности

```bash
uv add pytest-benchmark
```

```python
def test_sorting_performance(benchmark):
    """Тест производительности сортировки."""
    data = list(range(1000, 0, -1))
    
    result = benchmark(sorted, data)
    
    assert result == list(range(1, 1001))

def test_custom_function_performance(benchmark):
    """Тест производительности кастомной функции."""
    @benchmark
    def complex_calculation():
        return sum(i**2 for i in range(1000))
    
    result = complex_calculation
    assert result > 0
```

## 🔍 Отладка и анализ

### Подробная информация о падениях

```bash
# Подробный traceback
uv run pytest --tb=long

# Короткий traceback
uv run pytest --tb=short

# Только последняя строка
uv run pytest --tb=line

# Без traceback
uv run pytest --tb=no
```

### Отладка с pdb

```python
def test_complex_logic():
    data = prepare_data()
    
    # Точка останова
    import pdb; pdb.set_trace()
    
    result = process_data(data)
    assert result is not None
```

```bash
# Автоматический pdb при падении
uv run pytest --pdb

# pdb при первом падении
uv run pytest -x --pdb
```

### Вывод print statements

```bash
# Показать print даже в прошедших тестах
uv run pytest -s

# Захват вывода
uv run pytest --capture=no
```

## 📈 Анализ производительности

### Время выполнения тестов

```bash
# Топ 10 самых медленных тестов
uv run pytest --durations=10

# Все тесты с временем
uv run pytest --durations=0
```

### Профилирование тестов

```python
import pytest
import cProfile

def test_with_profiling():
    """Тест с профилированием."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Тестируемый код
    result = expensive_function()
    
    profiler.disable()
    profiler.dump_stats("test_profile.prof")
    
    assert result is not None
```

## 🎯 Практический пример: API тестирование

```python
# conftest.py
import pytest
from myapp import create_app

@pytest.fixture(scope="session")
def app():
    app = create_app(testing=True)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_token(client):
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password"
    })
    return response.json["token"]

@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
```

```python
# test_api.py
import pytest

class TestUserAPI:
    """Тесты пользовательского API."""
    
    def test_get_users_unauthorized(self, client):
        """Запрос без авторизации возвращает 401."""
        response = client.get("/api/users")
        assert response.status_code == 401
    
    def test_get_users_authorized(self, client, auth_headers):
        """Авторизованный запрос возвращает список пользователей."""
        response = client.get("/api/users", headers=auth_headers)
        
        assert response.status_code == 200
        assert "users" in response.json
        assert isinstance(response.json["users"], list)
    
    @pytest.mark.parametrize("email,expected_status", [
        ("valid@email.com", 201),
        ("invalid-email", 400),
        ("", 400),
    ])
    def test_create_user(self, client, auth_headers, email, expected_status):
        """Тест создания пользователя с разными email."""
        response = client.post("/api/users", 
                             headers=auth_headers,
                             json={"email": email, "name": "Test User"})
        
        assert response.status_code == expected_status
    
    @pytest.mark.integration
    def test_user_lifecycle(self, client, auth_headers):
        """Полный жизненный цикл пользователя."""
        # Создание
        create_response = client.post("/api/users",
                                    headers=auth_headers,
                                    json={"email": "lifecycle@test.com", 
                                         "name": "Lifecycle User"})
        assert create_response.status_code == 201
        user_id = create_response.json["id"]
        
        # Получение
        get_response = client.get(f"/api/users/{user_id}",
                                headers=auth_headers)
        assert get_response.status_code == 200
        assert get_response.json["email"] == "lifecycle@test.com"
        
        # Обновление
        update_response = client.put(f"/api/users/{user_id}",
                                   headers=auth_headers,
                                   json={"name": "Updated Name"})
        assert update_response.status_code == 200
        
        # Удаление
        delete_response = client.delete(f"/api/users/{user_id}",
                                      headers=auth_headers)
        assert delete_response.status_code == 204
        
        # Проверка удаления
        final_get = client.get(f"/api/users/{user_id}",
                             headers=auth_headers)
        assert final_get.status_code == 404
```

## 🎯 Следующие шаги

В следующей главе мы изучим практические примеры TDD и создадим несколько проектов с нуля, применяя все изученные техники.

## 💡 Ключевые выводы

1. **Pytest** — мощный и гибкий фреймворк
2. **Fixtures** — основа переиспользуемых тестов
3. **Параметризация** избавляет от дублирования
4. **Маркеры** помогают организовать тесты
5. **Плагины** расширяют возможности pytest

## 🧪 Проверьте свои знания

<div class="quiz-container" id="pytest-quiz">
<script type="application/json">
{
  "title": "Pytest фреймворк",
  "description": "Проверьте знание возможностей pytest",
  "icon": "⚡",
  "questions": [
    {
      "question": "Какие преимущества у pytest по сравнению с unittest? (выберите все правильные)",
      "type": "multiple",
      "options": [
        {"text": "Простой синтаксис assert вместо self.assertEqual", "correct": true},
        {"text": "Автоматическое обнаружение тестов", "correct": true},
        {"text": "Богатая система fixtures", "correct": true},
        {"text": "Параметризация тестов", "correct": true},
        {"text": "Обязательное наследование от TestCase", "correct": false}
      ],
      "explanation": "Pytest предлагает простой синтаксис, автообнаружение тестов, fixtures и параметризацию. Наследование от TestCase не требуется (это недостаток unittest).",
      "points": 2
    },
    {
      "question": "Что такое fixture в pytest?",
      "type": "single",
      "options": [
        {"text": "Файл с тестовыми данными", "correct": false},
        {"text": "Функция для подготовки тестового окружения", "correct": true},
        {"text": "Декоратор для маркировки тестов", "correct": false},
        {"text": "Конфигурационный файл", "correct": false}
      ],
      "explanation": "Fixture в pytest - это функция, которая подготавливает тестовое окружение и может передавать данные в тесты через dependency injection.",
      "points": 1
    },
    {
      "question": "Какой scope у fixture 'session'?",
      "type": "single",
      "options": [
        {"text": "Создается для каждого теста", "correct": false},
        {"text": "Создается для каждого класса тестов", "correct": false},
        {"text": "Создается один раз на всю сессию тестирования", "correct": true},
        {"text": "Создается для каждого модуля", "correct": false}
      ],
      "explanation": "Scope 'session' означает, что fixture создается один раз в начале сессии и используется всеми тестами. Это самый долгоживущий scope.",
      "points": 1
    },
    {
      "question": "Как правильно параметризовать тест в pytest?",
      "type": "single",
      "options": [
        {"text": "@pytest.parametrize('input,expected', [(1, 2), (2, 3)])", "correct": true},
        {"text": "@pytest.params(input=[1, 2], expected=[2, 3])", "correct": false},
        {"text": "@pytest.data_provider([(1, 2), (2, 3)])", "correct": false},
        {"text": "@pytest.with_params(input=1, expected=2)", "correct": false}
      ],
      "explanation": "Правильный синтаксис: @pytest.mark.parametrize('param_names', [param_values]). Это создает отдельный тест для каждого набора параметров.",
      "points": 1
    },
    {
      "question": "Какая команда запустит только медленные тесты?",
      "type": "single",
      "options": [
        {"text": "uv run pytest --slow", "correct": false},
        {"text": "uv run pytest -m slow", "correct": true},
        {"text": "uv run pytest --marker=slow", "correct": false},
        {"text": "uv run pytest --filter slow", "correct": false}
      ],
      "explanation": "Команда 'pytest -m slow' запускает тесты, помеченные маркером @pytest.mark.slow. Это стандартный способ фильтрации по маркерам.",
      "points": 1
    },
    {
      "question": "Для чего используется файл conftest.py?",
      "type": "multiple",
      "options": [
        {"text": "Определение общих fixtures для всего проекта", "correct": true},
        {"text": "Настройка конфигурации pytest", "correct": true},
        {"text": "Определение hooks для расширения pytest", "correct": true},
        {"text": "Хранение тестовых данных", "correct": false},
        {"text": "Настройка виртуального окружения", "correct": false}
      ],
      "explanation": "conftest.py используется для определения общих fixtures, настройки конфигурации и hooks. Pytest автоматически находит и использует этот файл.",
      "points": 2
    }
  ]
}
</script>
</div>

---

## 🔗 Связанные темы

- **[Основы тестирования в Python](04_python_testing_basics.md)** - структура тестов и assertions
- **[Unittest модуль](05_unittest.md)** - сравнение с pytest
- **[Цикл Red-Green-Refactor](03_red_green_refactor.md)** - применение pytest в TDD
- **[Практические примеры](07_practical_examples.md)** - реальные примеры с pytest
- **[Mock объекты](08_mocking.md)** - использование моков с pytest
- **[Интеграционное тестирование](09_integration_testing.md)** - pytest для интеграционных тестов
- **[Лучшие практики](12_best_practices.md)** - рекомендации по использованию pytest

**Следующая глава:** [Практические примеры TDD](07_practical_examples.md)

*⚡ Инструменты освоены — пора к практике!*
