# Интеграционное тестирование

## 🎯 Что такое интеграционное тестирование?

Интеграционное тестирование — это проверка взаимодействия между различными компонентами системы. В отличие от unit тестов, которые тестируют изолированные части кода, интеграционные тесты проверяют, что компоненты корректно работают вместе.

## 🏗 Уровни интеграционного тестирования

### 1. Component Integration Testing
Тестирование взаимодействия между классами и модулями.

```python
# Тестируем взаимодействие UserService и UserRepository
def test_user_service_repository_integration():
    """Интеграция сервиса пользователей с репозиторием."""
    # Реальные объекты, но с тестовой БД
    repository = UserRepository(test_database_connection)
    service = UserService(repository)
    
    # Тест полного взаимодействия
    user = service.create_user("test@example.com", "Test User")
    found_user = service.find_user_by_email("test@example.com")
    
    assert found_user.email == user.email
    assert found_user.id == user.id
```

### 2. API Integration Testing
Тестирование HTTP API endpoints.

```python
import requests
import pytest

@pytest.fixture
def api_client():
    """HTTP клиент для тестов."""
    return requests.Session()

def test_user_registration_api(api_client):
    """Тест регистрации через API."""
    # Создание пользователя
    response = api_client.post('http://localhost:8000/api/users', json={
        'email': 'test@example.com',
        'name': 'Test User',
        'password': 'securepassword'
    })
    
    assert response.status_code == 201
    user_data = response.json()
    assert 'id' in user_data
    assert user_data['email'] == 'test@example.com'
    
    # Проверка что пользователь создан
    get_response = api_client.get(f'http://localhost:8000/api/users/{user_data["id"]}')
    assert get_response.status_code == 200
    assert get_response.json()['email'] == 'test@example.com'
```

### 3. Database Integration Testing
Тестирование с реальной базой данных.

```python
import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def test_database():
    """Создание тестовой БД для сессии."""
    # Создаем временную БД
    db_fd, db_path = tempfile.mkstemp()
    engine = create_engine(f'sqlite:///{db_path}')
    
    # Создаем таблицы
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Очистка
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def db_session(test_database):
    """Сессия БД для каждого теста."""
    Session = sessionmaker(bind=test_database)
    session = Session()
    
    yield session
    
    session.rollback()
    session.close()

def test_user_crud_operations(db_session):
    """Интеграционный тест CRUD операций."""
    user_repo = UserRepository(db_session)
    
    # Create
    user = User(email="test@example.com", name="Test User")
    created_user = user_repo.save(user)
    
    assert created_user.id is not None
    
    # Read
    found_user = user_repo.find_by_id(created_user.id)
    assert found_user.email == "test@example.com"
    
    # Update
    found_user.name = "Updated Name"
    updated_user = user_repo.save(found_user)
    assert updated_user.name == "Updated Name"
    
    # Delete
    user_repo.delete(updated_user.id)
    deleted_user = user_repo.find_by_id(updated_user.id)
    assert deleted_user is None
```

## 🌐 Тестирование веб-приложений

### Flask приложения

```python
import pytest
from myapp import create_app, db
from myapp.models import User

@pytest.fixture
def app():
    """Создание Flask приложения для тестов."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Тестовый клиент Flask."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Тестовый CLI runner."""
    return app.test_cli_runner()

def test_user_registration_flow(client, app):
    """Тест полного потока регистрации."""
    # Регистрация
    response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    
    assert response.status_code == 302  # Redirect после успешной регистрации
    
    # Проверяем что пользователь создан в БД
    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None
        assert not user.is_confirmed  # Email не подтвержден
    
    # Логин
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 302
    
    # Проверяем доступ к защищенной странице
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'Dashboard' in response.data
```

### Django приложения

```python
import pytest
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

@pytest.fixture
def client():
    """Django тест клиент."""
    return Client()

@pytest.fixture
def user():
    """Тестовый пользователь."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.mark.django_db
def test_user_profile_update(client, user):
    """Тест обновления профиля пользователя."""
    # Логин
    client.login(username='testuser', password='testpass123')
    
    # Обновление профиля
    response = client.post(reverse('profile_update'), {
        'first_name': 'Test',
        'last_name': 'User',
        'bio': 'Test bio'
    })
    
    assert response.status_code == 302
    
    # Проверяем что данные обновились
    user.refresh_from_db()
    assert user.first_name == 'Test'
    assert user.last_name == 'User'

@pytest.mark.django_db
def test_post_creation_and_display(client, user):
    """Тест создания и отображения поста."""
    client.login(username='testuser', password='testpass123')
    
    # Создание поста
    response = client.post(reverse('post_create'), {
        'title': 'Test Post',
        'content': 'This is a test post content.'
    })
    
    assert response.status_code == 302
    
    # Проверяем что пост отображается
    response = client.get(reverse('post_list'))
    assert response.status_code == 200
    assert 'Test Post' in response.content.decode()
```

## 📊 Тестирование с внешними сервисами

### Тестирование API интеграций

```python
import pytest
import responses
import requests

class ExternalAPIClient:
    """Клиент для внешнего API."""
    
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
    
    def get_user_data(self, user_id):
        """Получение данных пользователя."""
        response = requests.get(
            f"{self.base_url}/users/{user_id}",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        response.raise_for_status()
        return response.json()

@responses.activate
def test_external_api_integration():
    """Тест интеграции с внешним API."""
    # Мокируем внешний API
    responses.add(
        responses.GET,
        'https://api.external.com/users/123',
        json={
            'id': 123,
            'name': 'John Doe',
            'email': 'john@example.com'
        },
        status=200
    )
    
    # Тестируем наш клиент
    client = ExternalAPIClient(
        base_url='https://api.external.com',
        api_key='test-key'
    )
    
    user_data = client.get_user_data('123')
    
    assert user_data['name'] == 'John Doe'
    assert user_data['email'] == 'john@example.com'

@responses.activate 
def test_external_api_error_handling():
    """Тест обработки ошибок внешнего API."""
    responses.add(
        responses.GET,
        'https://api.external.com/users/999',
        status=404
    )
    
    client = ExternalAPIClient(
        base_url='https://api.external.com', 
        api_key='test-key'
    )
    
    with pytest.raises(requests.HTTPError):
        client.get_user_data('999')
```

### Тестирование с очередями сообщений

```python
import pytest
from unittest.mock import Mock
import json

class MessageQueueProcessor:
    """Обработчик очереди сообщений."""
    
    def __init__(self, queue_client, user_service):
        self.queue_client = queue_client
        self.user_service = user_service
    
    def process_user_created_message(self, message):
        """Обработка сообщения о создании пользователя."""
        data = json.loads(message)
        user_id = data['user_id']
        
        # Отправляем welcome email
        user = self.user_service.get_user(user_id)
        self.user_service.send_welcome_email(user)
        
        # Подтверждаем обработку сообщения
        self.queue_client.ack_message(message)

def test_message_processing_integration():
    """Интеграционный тест обработки сообщений."""
    # Создаем реальные зависимости (но с тестовыми данными)
    mock_queue = Mock()
    mock_user_service = Mock()
    
    # Настраиваем поведение
    test_user = User(id=123, email="test@example.com")
    mock_user_service.get_user.return_value = test_user
    mock_user_service.send_welcome_email.return_value = True
    
    processor = MessageQueueProcessor(mock_queue, mock_user_service)
    
    # Тестируем обработку сообщения
    message = json.dumps({"user_id": 123, "action": "created"})
    processor.process_user_created_message(message)
    
    # Проверяем взаимодействия
    mock_user_service.get_user.assert_called_once_with(123)
    mock_user_service.send_welcome_email.assert_called_once_with(test_user)
    mock_queue.ack_message.assert_called_once_with(message)
```

## 🔧 Стратегии интеграционного тестирования

### 1. Bottom-Up Testing
Тестирование снизу вверх, начиная с нижних слоев.

```python
def test_data_layer_integration():
    """Тест слоя данных."""
    repository = UserRepository(database)
    user = repository.save(User("test@example.com"))
    assert user.id is not None

def test_service_layer_integration():
    """Тест сервисного слоя."""
    repository = UserRepository(database)
    service = UserService(repository)
    user = service.register_user("test@example.com")
    assert user.is_active == False

def test_api_layer_integration():
    """Тест API слоя."""
    response = client.post('/api/users', json={'email': 'test@example.com'})
    assert response.status_code == 201
```

### 2. Top-Down Testing
Тестирование сверху вниз, начиная с UI/API.

```python
def test_full_user_journey():
    """Полный путь пользователя через систему."""
    # 1. Регистрация через API
    response = client.post('/api/register', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    
    # 2. Подтверждение email (имитируем)
    user_id = response.json()['user_id']
    confirm_response = client.post(f'/api/confirm/{user_id}')
    assert confirm_response.status_code == 200
    
    # 3. Логин
    login_response = client.post('/api/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert login_response.status_code == 200
    token = login_response.json()['token']
    
    # 4. Доступ к защищенному ресурсу
    headers = {'Authorization': f'Bearer {token}'}
    profile_response = client.get('/api/profile', headers=headers)
    assert profile_response.status_code == 200
```

### 3. Sandwich Testing
Комбинация bottom-up и top-down подходов.

```python
class TestUserManagementIntegration:
    """Интеграционные тесты управления пользователями."""
    
    def test_bottom_up_data_flow(self, db_session):
        """Тест потока данных снизу вверх."""
        # Repository layer
        repo = UserRepository(db_session)
        user = repo.create(email="test@example.com")
        assert repo.find_by_id(user.id) == user
        
        # Service layer
        service = UserService(repo)
        service.activate_user(user.id)
        activated_user = repo.find_by_id(user.id)
        assert activated_user.is_active == True
    
    def test_top_down_api_flow(self, client):
        """Тест API потока сверху вниз."""
        # API создает пользователя
        response = client.post('/users', json={'email': 'test@example.com'})
        user_id = response.json()['id']
        
        # API активирует пользователя
        activate_response = client.put(f'/users/{user_id}/activate')
        assert activate_response.status_code == 200
        
        # Проверяем результат
        get_response = client.get(f'/users/{user_id}')
        assert get_response.json()['is_active'] == True
```

## 🐳 Тестирование с Docker

### Docker Compose для интеграционных тестов

```yaml
# docker-compose.test.yml
version: '3.8'
services:
  test-db:
    image: postgres:13
    environment:
      POSTGRES_DB: test_db
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_pass
    ports:
      - "5433:5432"
  
  test-redis:
    image: redis:6
    ports:
      - "6380:6379"
  
  test-app:
    build: .
    depends_on:
      - test-db
      - test-redis
    environment:
      DATABASE_URL: postgresql://test_user:test_pass@test-db:5432/test_db
      REDIS_URL: redis://test-redis:6379/0
    volumes:
      - .:/app
    command: pytest tests/integration/
```

### Pytest с Docker

```python
import pytest
import docker
import time
import psycopg2

@pytest.fixture(scope="session")
def docker_services():
    """Запуск Docker сервисов для тестов."""
    client = docker.from_env()
    
    # Запускаем PostgreSQL
    postgres = client.containers.run(
        "postgres:13",
        environment={
            "POSTGRES_DB": "test_db",
            "POSTGRES_USER": "test_user", 
            "POSTGRES_PASSWORD": "test_pass"
        },
        ports={'5432/tcp': 5433},
        detach=True,
        remove=True
    )
    
    # Ждем готовности БД
    for _ in range(30):
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5433,
                database="test_db",
                user="test_user",
                password="test_pass"
            )
            conn.close()
            break
        except psycopg2.OperationalError:
            time.sleep(1)
    
    yield {
        'postgres': postgres,
        'db_url': 'postgresql://test_user:test_pass@localhost:5433/test_db'
    }
    
    # Cleanup
    postgres.stop()

def test_database_integration(docker_services):
    """Интеграционный тест с реальной БД в Docker."""
    db_url = docker_services['db_url']
    
    # Создаем приложение с реальной БД
    app = create_app(database_url=db_url)
    
    with app.app_context():
        # Создаем таблицы
        db.create_all()
        
        # Тестируем операции
        user = User(email="test@example.com")
        db.session.add(user)
        db.session.commit()
        
        found_user = User.query.filter_by(email="test@example.com").first()
        assert found_user is not None
```

## 📈 Мониторинг интеграционных тестов

### Сбор метрик производительности

```python
import time
import pytest
from dataclasses import dataclass
from typing import List

@dataclass
class TestMetrics:
    test_name: str
    duration: float
    db_queries: int
    api_calls: int

class MetricsCollector:
    def __init__(self):
        self.metrics: List[TestMetrics] = []
    
    def record_test(self, name: str, duration: float, db_queries: int = 0, api_calls: int = 0):
        self.metrics.append(TestMetrics(name, duration, db_queries, api_calls))
    
    def get_slow_tests(self, threshold: float = 1.0) -> List[TestMetrics]:
        return [m for m in self.metrics if m.duration > threshold]

@pytest.fixture
def metrics_collector():
    return MetricsCollector()

def test_user_service_performance(metrics_collector, db_session):
    """Тест производительности сервиса пользователей."""
    start_time = time.time()
    
    service = UserService(db_session)
    
    # Создаем 100 пользователей
    for i in range(100):
        service.create_user(f"user{i}@example.com", f"User {i}")
    
    duration = time.time() - start_time
    
    # Записываем метрики
    metrics_collector.record_test(
        "test_user_service_performance",
        duration,
        db_queries=100  # Приблизительно
    )
    
    # Проверяем производительность
    assert duration < 5.0, f"Тест слишком медленный: {duration}s"
```

## 🎯 Лучшие практики интеграционного тестирования

### 1. Изоляция тестов

```python
@pytest.fixture(autouse=True)
def clean_database(db_session):
    """Очистка БД после каждого теста."""
    yield
    
    # Очищаем все таблицы
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
```

### 2. Управление тестовыми данными

```python
@pytest.fixture
def sample_users(db_session):
    """Создание тестовых пользователей."""
    users = [
        User(email="user1@example.com", name="User 1", role="admin"),
        User(email="user2@example.com", name="User 2", role="user"),
        User(email="user3@example.com", name="User 3", role="user"),
    ]
    
    for user in users:
        db_session.add(user)
    db_session.commit()
    
    return users

def test_user_search(sample_users, client):
    """Тест поиска пользователей."""
    response = client.get('/api/users/search?q=User')
    
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 3
```

### 3. Настройка окружения

```python
import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Настройка окружения для тестов."""
    # Устанавливаем переменные окружения для тестов
    os.environ.update({
        'ENVIRONMENT': 'test',
        'DEBUG': 'False',
        'DATABASE_URL': 'postgresql://test:test@localhost/test_db',
        'REDIS_URL': 'redis://localhost:6380/0',
        'EMAIL_BACKEND': 'console',  # Не отправляем реальные emails
    })
    
    yield
    
    # Очистка после тестов
    for key in ['ENVIRONMENT', 'DEBUG', 'DATABASE_URL', 'REDIS_URL', 'EMAIL_BACKEND']:
        os.environ.pop(key, None)
```

## 🎯 Следующие шаги

В следующей главе мы изучим применение TDD в веб-разработке с конкретными примерами на Django и Flask.

## 🧪 Проверьте свои знания

<div class="quiz-container" id="integration-testing-quiz">
<script type="application/json">
{
  "title": "Интеграционное тестирование",
  "description": "Проверьте знание принципов и техник интеграционного тестирования",
  "icon": "🔗",
  "questions": [
    {
      "question": "В чем основное отличие интеграционных тестов от unit тестов?",
      "type": "single",
      "options": [
        {"text": "Интеграционные тесты быстрее выполняются", "correct": false},
        {"text": "Интеграционные тесты проверяют взаимодействие между компонентами", "correct": true},
        {"text": "Интеграционные тесты не используют mock объекты", "correct": false},
        {"text": "Интеграционные тесты проще в написании", "correct": false}
      ],
      "explanation": "Интеграционные тесты проверяют корректность взаимодействия между различными компонентами системы, в отличие от unit тестов, которые тестируют отдельные модули изолированно.",
      "points": 1
    },
    {
      "question": "Какие стратегии интеграционного тестирования существуют? (выберите все правильные)",
      "type": "multiple",
      "options": [
        {"text": "Big Bang - тестирование всех компонентов сразу", "correct": true},
        {"text": "Bottom-up - снизу вверх от низкоуровневых модулей", "correct": true},
        {"text": "Top-down - сверху вниз от высокоуровневых модулей", "correct": true},
        {"text": "Sandwich/Hybrid - комбинированный подход", "correct": true},
        {"text": "Random - случайное тестирование компонентов", "correct": false}
      ],
      "explanation": "Существует четыре основные стратегии: Big Bang (все сразу), Bottom-up (снизу вверх), Top-down (сверху вниз), Sandwich (гибридный). Random не является признанной стратегией.",
      "points": 2
    },
    {
      "question": "Что такое Test Pyramid в контексте интеграционного тестирования?",
      "type": "single",
      "options": [
        {"text": "Структура организации тестовых файлов", "correct": false},
        {"text": "Принцип распределения количества тестов по уровням", "correct": true},
        {"text": "Метод создания тестовых данных", "correct": false},
        {"text": "Архитектурный паттерн для тестов", "correct": false}
      ],
      "explanation": "Test Pyramid показывает оптимальное распределение тестов: много unit тестов (база), умеренно интеграционных (середина), мало E2E тестов (вершина).",
      "points": 1
    },
    {
      "question": "Какие компоненты обычно тестируются в интеграционных тестах базы данных?",
      "type": "multiple",
      "options": [
        {"text": "CRUD операции с реальной БД", "correct": true},
        {"text": "Транзакции и откаты", "correct": true},
        {"text": "Ограничения целостности (constraints)", "correct": true},
        {"text": "Производительность SQL запросов", "correct": false},
        {"text": "Миграции схемы БД", "correct": true}
      ],
      "explanation": "Интеграционные тесты БД покрывают CRUD операции, транзакции, constraints и миграции. Производительность обычно тестируется отдельно в performance тестах.",
      "points": 2
    },
    {
      "question": "Что такое Contract Testing?",
      "type": "single",
      "options": [
        {"text": "Тестирование юридических контрактов", "correct": false},
        {"text": "Проверка соблюдения API контрактов между сервисами", "correct": true},
        {"text": "Тестирование пользовательских соглашений", "correct": false},
        {"text": "Проверка контрактов с внешними поставщиками", "correct": false}
      ],
      "explanation": "Contract Testing проверяет, что API сервисов соответствуют заранее определенным контрактам (схемам), обеспечивая совместимость между микросервисами.",
      "points": 1
    },
    {
      "question": "Какие проблемы решает использование testcontainers?",
      "type": "multiple",
      "options": [
        {"text": "Изоляция тестовой среды", "correct": true},
        {"text": "Воспроизводимость тестов на разных машинах", "correct": true},
        {"text": "Тестирование с реальными зависимостями (БД, Redis, etc.)", "correct": true},
        {"text": "Автоматическая очистка после тестов", "correct": true},
        {"text": "Ускорение выполнения тестов", "correct": false}
      ],
      "explanation": "Testcontainers обеспечивает изоляцию, воспроизводимость, работу с реальными зависимостями и автоочистку. Ускорение не является главной целью (контейнеры могут замедлять тесты).",
      "points": 2
    }
  ]
}
</script>
</div>

---

## 🔗 Связанные темы

- **[Mock объекты](08_mocking.md)** - изоляция vs интеграция
- **[Практические примеры](07_practical_examples.md)** - примеры интеграционных тестов
- **[TDD в веб-разработке](10_web_development_tdd.md)** - интеграционное тестирование веб-приложений
- **[Продвинутые техники](11_advanced_tdd.md)** - сложные интеграционные сценарии
- **[CI/CD и автоматизация](14_ci_cd_automation.md)** - автоматизация интеграционных тестов
- **[Лучшие практики](12_best_practices.md)** - организация интеграционных тестов

**Следующая глава:** [TDD в веб-разработке](10_web_development_tdd.md)

*🔗 Компоненты связаны — переходим к веб-приложениям!*
