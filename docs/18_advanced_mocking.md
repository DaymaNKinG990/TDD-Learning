# Продвинутое мокирование сложных зависимостей

## 🎯 Введение

После освоения базовых техник мокирования пришло время изучить продвинутые сценарии. В реальных проектах вы столкнетесь с необходимостью мокирования баз данных, асинхронного кода, файловых операций, внешних API и других сложных зависимостей. Эта глава покрывает все эти аспекты с практическими примерами.

## 🗄️ Мокирование баз данных

### Стратегии тестирования с БД

#### Setup: SQLAlchemy Models

Все примеры в этом разделе используют следующие определения моделей:

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Create declarative base
Base = declarative_base()

# User model
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
```

#### 1. In-Memory Database

```python
# Note: Base and User are defined in the Setup section above
# Использование SQLite в памяти для тестов
import pytest
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class UserRepository:
    def __init__(self, session):
        self.session = session
    
    def create_user(self, name, email):
        user = User(name=name, email=email)
        self.session.add(user)
        self.session.commit()
        return user
    
    def find_by_email(self, email):
        return self.session.query(User).filter_by(email=email).first()

# Настройка in-memory БД для тестов
@pytest.fixture
def in_memory_db():
    """Создает in-memory SQLite базу для тестов."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()

def test_user_repository_with_in_memory_db(in_memory_db):
    """Тест с реальной in-memory БД."""
    repo = UserRepository(in_memory_db)
    
    # Создаем пользователя
    user = repo.create_user("John Doe", "john@example.com")
    assert user.id is not None
    
    # Ищем пользователя
    found_user = repo.find_by_email("john@example.com")
    assert found_user.name == "John Doe"
```

#### 2. Test Doubles для ORM

```python
# Note: Base and User are defined in the Setup section above
# Мокирование SQLAlchemy сессии
def test_user_repository_with_mocked_session(mocker):
    """Тест с замоканной сессией."""
    mock_session = mocker.Mock()
    mock_user = mocker.Mock()
    mock_user.id = 1
    mock_user.name = "John Doe"
    mock_user.email = "john@example.com"
    
    # Настраиваем поведение мока
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_user
    
    repo = UserRepository(mock_session)
    user = repo.find_by_email("john@example.com")
    
    assert user.name == "John Doe"
    mock_session.query.assert_called_once_with(User)
    mock_session.query.return_value.filter_by.assert_called_once_with(email="john@example.com")
```

#### 3. Repository Pattern для тестируемости

```python
# Note: Base and User are defined in the Setup section above
from abc import ABC, abstractmethod
from typing import Optional

class UserRepositoryInterface(ABC):
    @abstractmethod
    def create_user(self, name: str, email: str) -> User:
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass

class SQLAlchemyUserRepository(UserRepositoryInterface):
    """Реальная реализация с SQLAlchemy."""
    
    def __init__(self, session):
        self.session = session
    
    def create_user(self, name: str, email: str) -> User:
        user = User(name=name, email=email)
        self.session.add(user)
        self.session.commit()
        return user
    
    def find_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter_by(email=email).first()

class FakeUserRepository(UserRepositoryInterface):
    """Fake реализация для тестов."""
    
    def __init__(self):
        self.users = {}
        self.next_id = 1
    
    def create_user(self, name: str, email: str) -> User:
        user = User(id=self.next_id, name=name, email=email)
        self.users[email] = user
        self.next_id += 1
        return user
    
    def find_by_email(self, email: str) -> Optional[User]:
        return self.users.get(email)

# Сервис, использующий репозиторий
class UserService:
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository
    
    def register_user(self, name: str, email: str) -> User:
        existing_user = self.user_repository.find_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        return self.user_repository.create_user(name, email)

# Тестирование с Fake репозиторием
def test_user_service_with_fake_repository():
    """Быстрый тест с fake репозиторием."""
    fake_repo = FakeUserRepository()
    service = UserService(fake_repo)
    
    # Успешная регистрация
    user = service.register_user("John Doe", "john@example.com")
    assert user.name == "John Doe"
    assert user.email == "john@example.com"
    
    # Попытка зарегистрировать дубликат
    with pytest.raises(ValueError, match="User with this email already exists"):
        service.register_user("Jane Doe", "john@example.com")
```

#### 4. Testcontainers для интеграционных тестов

```bash
# Установка testcontainers
uv add testcontainers[postgresql]
```

```python
import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Note: Base and User are defined in the Setup section above

@pytest.fixture(scope="session")
def postgres_container():
    """Запускает PostgreSQL в Docker контейнере для тестов."""
    with PostgresContainer("postgres:13") as postgres:
        yield postgres

@pytest.fixture
def postgres_session(postgres_container):
    """Создает сессию для PostgreSQL контейнера."""
    engine = create_engine(postgres_container.get_connection_url())
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.rollback()
    session.close()

def test_user_repository_with_real_postgres(postgres_session):
    """Интеграционный тест с реальной PostgreSQL."""
    repo = SQLAlchemyUserRepository(postgres_session)
    
    # Тестируем со всеми особенностями PostgreSQL
    user = repo.create_user("John Doe", "john@example.com")
    assert user.id is not None
    
    found_user = repo.find_by_email("john@example.com")
    assert found_user.name == "John Doe"
```

#### 5. Database Fixtures и транзакции

```python
# Note: Base and User are defined in the Setup section above
import pytest

@pytest.fixture
def db_transaction(real_db_session):
    """Фикстура для автоматического rollback после тестов."""
    transaction = real_db_session.begin()
    yield real_db_session
    transaction.rollback()

@pytest.fixture
def sample_users(db_transaction):
    """Фикстура с тестовыми данными."""
    users = [
        User(name="Alice", email="alice@example.com"),
        User(name="Bob", email="bob@example.com"),
        User(name="Charlie", email="charlie@example.com"),
    ]
    
    for user in users:
        db_transaction.add(user)
    db_transaction.flush()  # Получаем ID без commit
    
    return users

def test_user_search_with_fixtures(db_transaction, sample_users):
    """Тест с предустановленными данными."""
    repo = UserRepository(db_transaction)
    
    # Ищем существующего пользователя
    alice = repo.find_by_email("alice@example.com")
    assert alice.name == "Alice"
    
    # Ищем несуществующего
    missing = repo.find_by_email("missing@example.com")
    assert missing is None
```

## 🌐 Мокирование HTTP API и сетевых запросов

### 1. Мокирование requests

```python
import requests
import responses
from unittest.mock import Mock, patch

class WeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.weather.com"
    
    def get_temperature(self, city: str) -> float:
        response = requests.get(
            f"{self.base_url}/current",
            params={"city": city, "key": self.api_key}
        )
        response.raise_for_status()
        data = response.json()
        return data["temperature"]
    
    def get_forecast(self, city: str, days: int = 5) -> list:
        response = requests.get(
            f"{self.base_url}/forecast",
            params={"city": city, "days": days, "key": self.api_key}
        )
        response.raise_for_status()
        return response.json()["forecast"]

# Тестирование с responses
@responses.activate
def test_weather_service_get_temperature():
    """Тест с замоканным HTTP ответом."""
    responses.add(
        responses.GET,
        "https://api.weather.com/current",
        json={"temperature": 22.5, "humidity": 65},
        status=200
    )
    
    service = WeatherService("test-api-key")
    temperature = service.get_temperature("Moscow")
    
    assert temperature == 22.5
    assert len(responses.calls) == 1
    assert responses.calls[0].request.params["city"] == ["Moscow"]

# Тестирование с pytest-httpx для async клиентов
import httpx
import pytest
from pytest_httpx import HTTPXMock

class AsyncWeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.weather.com"
    
    async def get_temperature(self, city: str) -> float:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/current",
                params={"city": city, "key": self.api_key}
            )
            response.raise_for_status()
            data = response.json()
            return data["temperature"]

@pytest.mark.asyncio
async def test_async_weather_service(httpx_mock: HTTPXMock):
    """Тест асинхронного HTTP клиента."""
    httpx_mock.add_response(
        url="https://api.weather.com/current?city=Moscow&key=test-api-key",
        json={"temperature": 22.5}
    )
    
    service = AsyncWeatherService("test-api-key")
    temperature = await service.get_temperature("Moscow")
    
    assert temperature == 22.5
```

### 2. Мокирование с Circuit Breaker

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
    
    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

class ResilientWeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.circuit_breaker = CircuitBreaker()
    
    def get_temperature(self, city: str) -> float:
        return self.circuit_breaker.call(self._fetch_temperature, city)
    
    def _fetch_temperature(self, city: str) -> float:
        response = requests.get(
            "https://api.weather.com/current",
            params={"city": city, "key": self.api_key}
        )
        response.raise_for_status()
        return response.json()["temperature"]

def test_circuit_breaker_behavior():
    """Тест поведения circuit breaker."""
    service = ResilientWeatherService("test-key")
    
    # Мокируем requests для имитации сбоев
    with patch('requests.get') as mock_get:
        # Первые 5 запросов падают
        mock_get.side_effect = requests.ConnectionError("Network error")
        
        # Пытаемся получить температуру 5 раз
        for i in range(5):
            with pytest.raises(requests.ConnectionError):
                service.get_temperature("Moscow")
        
        # Circuit breaker должен открыться на 6-м запросе
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            service.get_temperature("Moscow")
        
        # Проверяем состояние
        assert service.circuit_breaker.state == CircuitState.OPEN
```

## 🔄 Мокирование асинхронного кода

### 1. Основы асинхронного мокирования

```python
import asyncio
import aiohttp
from unittest.mock import AsyncMock, Mock

class AsyncDataService:
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_user_data(self, user_id: int) -> dict:
        async with self.session.get(f"https://api.example.com/users/{user_id}") as response:
            response.raise_for_status()
            return await response.json()
    
    async def save_user_data(self, user_data: dict) -> bool:
        async with self.session.post("https://api.example.com/users", json=user_data) as response:
            return response.status == 201

# Тестирование с AsyncMock
@pytest.mark.asyncio
async def test_async_data_service(mocker):
    """Тест асинхронного сервиса с мокированием."""
    
    # Мокируем aiohttp сессию
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.json.return_value = {"id": 1, "name": "John"}
    mock_response.status = 200
    mock_response.raise_for_status.return_value = None
    
    # Настраиваем context manager
    mock_session.get.return_value.__aenter__.return_value = mock_response
    
    # Создаем сервис и подменяем сессию
    service = AsyncDataService()
    service.session = mock_session
    
    # Тестируем
    user_data = await service.fetch_user_data(1)
    
    assert user_data == {"id": 1, "name": "John"}
    mock_session.get.assert_called_once_with("https://api.example.com/users/1")
```

### 2. Мокирование async/await цепочек

```python
class AsyncEmailService:
    async def send_email(self, to: str, subject: str, body: str) -> bool:
        # Асинхронная отправка email
        await asyncio.sleep(0.1)  # Имитация задержки
        return True

class AsyncUserService:
    def __init__(self, data_service: AsyncDataService, email_service: AsyncEmailService):
        self.data_service = data_service
        self.email_service = email_service
    
    async def register_user(self, user_data: dict) -> dict:
        # Сохраняем пользователя
        success = await self.data_service.save_user_data(user_data)
        if not success:
            raise ValueError("Failed to save user")
        
        # Отправляем welcome email
        email_sent = await self.email_service.send_email(
            user_data["email"],
            "Welcome!",
            f"Welcome, {user_data['name']}!"
        )
        
        return {
            "user_saved": success,
            "email_sent": email_sent,
            "user_data": user_data
        }

@pytest.mark.asyncio
async def test_async_user_registration():
    """Тест асинхронной регистрации пользователя."""
    
    # Мокируем зависимости
    mock_data_service = AsyncMock()
    mock_data_service.save_user_data.return_value = True
    
    mock_email_service = AsyncMock()
    mock_email_service.send_email.return_value = True
    
    # Создаем сервис
    user_service = AsyncUserService(mock_data_service, mock_email_service)
    
    # Тестируем
    user_data = {"name": "John Doe", "email": "john@example.com"}
    result = await user_service.register_user(user_data)
    
    # Проверяем результат
    assert result["user_saved"] is True
    assert result["email_sent"] is True
    assert result["user_data"] == user_data
    
    # Проверяем вызовы
    mock_data_service.save_user_data.assert_called_once_with(user_data)
    mock_email_service.send_email.assert_called_once_with(
        "john@example.com",
        "Welcome!",
        "Welcome, John Doe!"
    )
```

### 3. Тестирование конкурентности и race conditions

```python
import asyncio
from typing import List

class AsyncCounter:
    def __init__(self):
        self._value = 0
        self._lock = asyncio.Lock()
    
    async def increment(self):
        async with self._lock:
            current = self._value
            await asyncio.sleep(0.001)  # Имитация задержки
            self._value = current + 1
    
    @property
    def value(self):
        return self._value

class AsyncTaskProcessor:
    def __init__(self, counter: AsyncCounter):
        self.counter = counter
    
    async def process_batch(self, items: List[str]) -> List[str]:
        tasks = []
        for item in items:
            task = asyncio.create_task(self._process_item(item))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
    
    async def _process_item(self, item: str) -> str:
        await self.counter.increment()
        await asyncio.sleep(0.01)  # Имитация обработки
        return f"processed_{item}"

@pytest.mark.asyncio
async def test_concurrent_processing():
    """Тест конкурентной обработки."""
    counter = AsyncCounter()
    processor = AsyncTaskProcessor(counter)
    
    items = [f"item_{i}" for i in range(10)]
    results = await processor.process_batch(items)
    
    # Проверяем результаты
    assert len(results) == 10
    assert all(result.startswith("processed_") for result in results)
    
    # Проверяем, что все инкременты сработали
    assert counter.value == 10

@pytest.mark.asyncio
async def test_race_condition_protection():
    """Тест защиты от race conditions."""
    counter = AsyncCounter()
    
    # Запускаем множественные конкурентные инкременты
    tasks = [counter.increment() for _ in range(100)]
    await asyncio.gather(*tasks)
    
    # Должно быть ровно 100, а не меньше из-за race condition
    assert counter.value == 100
```

## 📁 Мокирование файловых операций

### 1. Базовое мокирование файлов

```python
import os
import json
from pathlib import Path
from unittest.mock import mock_open, patch

class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
    
    def load_config(self) -> dict:
        if not self.config_path.exists():
            return {}
        
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def save_config(self, config: dict) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)

def test_config_manager_load_existing():
    """Тест загрузки существующего конфига."""
    config_data = {"database_url": "localhost", "debug": True}
    
    with patch("pathlib.Path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=json.dumps(config_data))):
            manager = ConfigManager("/app/config.json")
            loaded_config = manager.load_config()
            
            assert loaded_config == config_data

def test_config_manager_load_missing():
    """Тест загрузки несуществующего конфига."""
    with patch("pathlib.Path.exists", return_value=False):
        manager = ConfigManager("/app/config.json")
        loaded_config = manager.load_config()
        
        assert loaded_config == {}

def test_config_manager_save():
    """Тест сохранения конфига."""
    config_data = {"database_url": "localhost", "debug": True}
    
    with patch("pathlib.Path.mkdir") as mock_mkdir:
        with patch("builtins.open", mock_open()) as mock_file:
            manager = ConfigManager("/app/config.json")
            manager.save_config(config_data)
            
            # Проверяем создание директории
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
            
            # Проверяем запись файла
            mock_file.assert_called_once_with(Path("/app/config.json"), 'w')
            handle = mock_file()
            handle.write.assert_called()
```

### 2. Мокирование с pyfakefs

```bash
# Установка pyfakefs
uv add pyfakefs
```

```python
import pytest
from pathlib import Path
from typing import List
from pyfakefs.fake_filesystem_unittest import Patcher

class LogFileManager:
    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
    
    def write_log(self, message: str) -> None:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = self.log_dir / "app.log"
        with open(log_file, 'a') as f:
            f.write(f"{message}\n")
    
    def read_logs(self) -> List[str]:
        log_file = self.log_dir / "app.log"
        if not log_file.exists():
            return []
        
        with open(log_file, 'r') as f:
            return [line.strip() for line in f.readlines()]
    
    def clear_logs(self) -> None:
        log_file = self.log_dir / "app.log"
        if log_file.exists():
            log_file.unlink()

def test_log_file_manager_with_fake_fs():
    """Тест с fake файловой системой."""
    with Patcher() as patcher:
        # Создаем fake файловую систему
        patcher.fs.create_dir("/app/logs")
        
        manager = LogFileManager("/app/logs")
        
        # Записываем логи
        manager.write_log("First message")
        manager.write_log("Second message")
        
        # Читаем логи
        logs = manager.read_logs()
        assert logs == ["First message", "Second message"]
        
        # Очищаем логи
        manager.clear_logs()
        logs = manager.read_logs()
        assert logs == []

@pytest.fixture
def fake_fs():
    """Фикстура для fake файловой системы."""
    with Patcher() as patcher:
        yield patcher.fs

def test_file_operations_with_fixture(fake_fs):
    """Тест с использованием фикстуры."""
    # Создаем файловую структуру
    fake_fs.create_file("/etc/config.json", contents='{"key": "value"}')
    fake_fs.create_dir("/var/log")
    
    # Тестируем операции
    assert os.path.exists("/etc/config.json")
    assert os.path.isdir("/var/log")
    
    with open("/etc/config.json", 'r') as f:
        data = json.load(f)
        assert data["key"] == "value"
```

### 3. Temporary Files и Directories

```python
import tempfile
import shutil

class FileProcessor:
    def process_file(self, input_path: str, output_path: str) -> None:
        with open(input_path, 'r') as input_file:
            content = input_file.read()
        
        # Обработка содержимого
        processed_content = content.upper()
        
        with open(output_path, 'w') as output_file:
            output_file.write(processed_content)

def test_file_processor_with_temp_files():
    """Тест с временными файлами."""
    processor = FileProcessor()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем временные файлы
        input_path = Path(temp_dir) / "input.txt"
        output_path = Path(temp_dir) / "output.txt"
        
        # Записываем входные данные
        with open(input_path, 'w') as f:
            f.write("hello world")
        
        # Обрабатываем
        processor.process_file(str(input_path), str(output_path))
        
        # Проверяем результат
        with open(output_path, 'r') as f:
            result = f.read()
            assert result == "HELLO WORLD"

@pytest.fixture
def temp_workspace():
    """Фикстура для временного рабочего пространства."""
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir)
        
        # Создаем структуру папок
        (workspace / "input").mkdir()
        (workspace / "output").mkdir()
        (workspace / "config").mkdir()
        
        yield workspace

def test_complex_file_operations(temp_workspace):
    """Тест сложных файловых операций."""
    input_dir = temp_workspace / "input"
    output_dir = temp_workspace / "output"
    
    # Создаем несколько входных файлов
    (input_dir / "file1.txt").write_text("content 1")
    (input_dir / "file2.txt").write_text("content 2")
    
    processor = FileProcessor()
    
    # Обрабатываем все файлы
    for input_file in input_dir.glob("*.txt"):
        output_file = output_dir / input_file.name
        processor.process_file(str(input_file), str(output_file))
    
    # Проверяем результаты
    assert (output_dir / "file1.txt").read_text() == "CONTENT 1"
    assert (output_dir / "file2.txt").read_text() == "CONTENT 2"
```

## 🕰️ Мокирование времени и даты

### 1. Базовое мокирование времени

```python
import datetime
from unittest.mock import patch
import pytest
from freezegun import freeze_time

class TimeBasedService:
    def get_current_timestamp(self) -> str:
        return datetime.datetime.now().isoformat()
    
    def is_business_hours(self) -> bool:
        now = datetime.datetime.now()
        return 9 <= now.hour < 18 and now.weekday() < 5
    
    def calculate_age(self, birth_date: datetime.date) -> int:
        today = datetime.date.today()
        return today.year - birth_date.year

# Тестирование с patch
def test_timestamp_with_patch():
    """Тест с мокированием datetime."""
    fixed_time = datetime.datetime(2024, 8, 26, 12, 30, 45)
    
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = fixed_time
        mock_datetime.side_effect = lambda *args, **kw: datetime.datetime(*args, **kw)
        
        service = TimeBasedService()
        timestamp = service.get_current_timestamp()
        
        assert timestamp == "2024-08-26T12:30:45"

# Тестирование с freezegun
@freeze_time("2024-08-26 12:30:45")
def test_business_hours_monday_noon():
    """Тест бизнес-часов в понедельник в полдень."""
    service = TimeBasedService()
    assert service.is_business_hours() is True

@freeze_time("2024-08-26 20:00:00")  # 8 PM
def test_business_hours_evening():
    """Тест после рабочих часов."""
    service = TimeBasedService()
    assert service.is_business_hours() is False

@freeze_time("2024-08-25 12:00:00")  # Sunday
def test_business_hours_weekend():
    """Тест в выходной день."""
    service = TimeBasedService()
    assert service.is_business_hours() is False

@freeze_time("2024-08-26")
def test_age_calculation():
    """Тест расчета возраста."""
    service = TimeBasedService()
    birth_date = datetime.date(1990, 5, 15)
    
    age = service.calculate_age(birth_date)
    assert age == 34
```

### 2. Мокирование таймаутов и задержек

```python
import asyncio
import time
import aiohttp
import pytest
from unittest.mock import patch, AsyncMock

class RateLimitedService:
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    def make_request(self, data: str) -> str:
        current_time = time.time()
        
        # Удаляем старые вызовы (старше минуты)
        self.calls = [call_time for call_time in self.calls 
                     if current_time - call_time < 60]
        
        # Проверяем лимит
        if len(self.calls) >= self.calls_per_minute:
            raise Exception("Rate limit exceeded")
        
        self.calls.append(current_time)
        return f"processed: {data}"

class AsyncRetryService:
    async def fetch_with_retry(self, url: str, max_retries: int = 3) -> str:
        for attempt in range(max_retries):
            try:
                # HTTP запрос через aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        response.raise_for_status()
                        return f"Success: {url}"
                
            except aiohttp.ClientError:
                if attempt == max_retries - 1:
                    raise
                
                # Exponential backoff
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)

def test_rate_limiting_with_time_mock():
    """Тест rate limiting с мокированием времени."""
    service = RateLimitedService(calls_per_minute=2)
    
    with patch('time.time') as mock_time:
        # Первый вызов в момент времени 0
        mock_time.return_value = 0
        result1 = service.make_request("data1")
        assert result1 == "processed: data1"
        
        # Второй вызов через 30 секунд
        mock_time.return_value = 30
        result2 = service.make_request("data2")
        assert result2 == "processed: data2"
        
        # Третий вызов сразу же - должен упасть
        with pytest.raises(Exception, match="Rate limit exceeded"):
            service.make_request("data3")
        
        # Но через минуту должен работать
        mock_time.return_value = 61
        result3 = service.make_request("data3")
        assert result3 == "processed: data3"

@pytest.mark.asyncio
async def test_async_retry_with_time_control():
    """Тест async retry с контролем времени."""
    service = AsyncRetryService()
    
    # Мокируем asyncio.sleep чтобы тесты были быстрыми
    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        # Мокируем HTTP запросы - первые 2 попытки падают, третья успешна
        call_count = 0
        
        async def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:  # Первые 2 попытки падают
                raise aiohttp.ClientError("Network error")
            # Успешный ответ
            mock_response = AsyncMock()
            mock_response.raise_for_status = AsyncMock()
            return mock_response
        
        # Мокируем контекстный менеджер для ClientSession
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(side_effect=mock_get)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        # Патчим ClientSession чтобы он возвращал мок с контролируемым поведением get
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await service.fetch_with_retry("http://example.com")
            
            # Проверяем, что были задержки
            assert mock_sleep.call_count >= 2  # Минимум 2 retry
            assert result == "Success: http://example.com"
```

## 🧪 Сложные сценарии мокирования

### 1. Мокирование чейнинга методов

```python
class FluentQueryBuilder:
    def __init__(self, table: str):
        self.table = table
        self.conditions = []
        self.order_by_clause = None
        self.limit_clause = None
    
    def where(self, condition: str):
        self.conditions.append(condition)
        return self
    
    def order_by(self, column: str):
        self.order_by_clause = column
        return self
    
    def limit(self, count: int):
        self.limit_clause = count
        return self
    
    def execute(self) -> list:
        # Имитация выполнения запроса
        query = f"SELECT * FROM {self.table}"
        if self.conditions:
            query += f" WHERE {' AND '.join(self.conditions)}"
        if self.order_by_clause:
            query += f" ORDER BY {self.order_by_clause}"
        if self.limit_clause:
            query += f" LIMIT {self.limit_clause}"
        
        # Здесь был бы реальный запрос к БД
        return [{"id": 1, "name": "test"}]

def test_fluent_query_builder():
    """Тест fluent интерфейса с мокированием."""
    
    # Создаем мок с поддержкой чейнинга
    mock_builder = Mock()
    mock_builder.where.return_value = mock_builder
    mock_builder.order_by.return_value = mock_builder
    mock_builder.limit.return_value = mock_builder
    mock_builder.execute.return_value = [{"id": 1, "name": "test"}]
    
    # Тестируем чейнинг
    result = (mock_builder
              .where("age > 18")
              .where("active = true")
              .order_by("name")
              .limit(10)
              .execute())
    
    assert result == [{"id": 1, "name": "test"}]
    
    # Проверяем вызовы
    mock_builder.where.assert_any_call("age > 18")
    mock_builder.where.assert_any_call("active = true")
    mock_builder.order_by.assert_called_once_with("name")
    mock_builder.limit.assert_called_once_with(10)
    mock_builder.execute.assert_called_once()
```

### 2. Мокирование context managers

```python
class DatabaseTransaction:
    def __init__(self, connection):
        self.connection = connection
        self.transaction = None
    
    def __enter__(self):
        self.transaction = self.connection.begin()
        return self.transaction
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.transaction.commit()
        else:
            self.transaction.rollback()

class UserService:
    def __init__(self, connection):
        self.connection = connection
    
    def create_user_with_profile(self, user_data: dict, profile_data: dict) -> int:
        with DatabaseTransaction(self.connection) as tx:
            # Создаем пользователя
            user_id = tx.execute("INSERT INTO users ...", user_data)
            
            # Создаем профиль
            profile_data["user_id"] = user_id
            tx.execute("INSERT INTO profiles ...", profile_data)
            
            return user_id

def test_user_service_with_transaction():
    """Тест сервиса с мокированием транзакции."""
    
    # Мокируем компоненты
    mock_connection = Mock()
    mock_transaction = Mock()
    mock_transaction.execute.side_effect = [123, None]  # user_id, затем None
    
    # Настраиваем context manager
    mock_connection.begin.return_value = mock_transaction
    
    # Тестируем
    service = UserService(mock_connection)
    user_data = {"name": "John", "email": "john@example.com"}
    profile_data = {"bio": "Developer"}
    
    user_id = service.create_user_with_profile(user_data, profile_data)
    
    assert user_id == 123
    
    # Проверяем вызовы
    mock_connection.begin.assert_called_once()
    assert mock_transaction.execute.call_count == 2
    mock_transaction.commit.assert_called_once()
    mock_transaction.rollback.assert_not_called()
```

### 3. Property-based тестирование с моками

```bash
# Установка Hypothesis
uv add hypothesis
```

```python
from hypothesis import given, strategies as st

class MathService:
    def __init__(self, logger):
        self.logger = logger
    
    def divide(self, a: float, b: float) -> float:
        if b == 0:
            self.logger.error(f"Division by zero attempted: {a} / {b}")
            raise ValueError("Cannot divide by zero")
        
        result = a / b
        self.logger.info(f"Division: {a} / {b} = {result}")
        return result

@given(
    a=st.floats(allow_nan=False, allow_infinity=False),
    b=st.floats(allow_nan=False, allow_infinity=False).filter(lambda x: x != 0)
)
def test_math_service_divide_property(a, b):
    """Property-based тест деления с мокированием."""
    mock_logger = Mock()
    service = MathService(mock_logger)
    
    result = service.divide(a, b)
    
    # Свойства, которые должны выполняться
    assert isinstance(result, float)
    assert result == a / b
    
    # Проверяем логирование
    mock_logger.info.assert_called_once()
    mock_logger.error.assert_not_called()

@given(a=st.floats(allow_nan=False, allow_infinity=False))
def test_math_service_divide_by_zero_property(a):
    """Property-based тест деления на ноль."""
    mock_logger = Mock()
    service = MathService(mock_logger)
    
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        service.divide(a, 0)
    
    # Проверяем логирование ошибки
    mock_logger.error.assert_called_once()
    mock_logger.info.assert_not_called()
```

## 🎯 Лучшие практики продвинутого мокирования

### ✅ Do's

1. **Используйте подходящий уровень мокирования**
   - Unit тесты: мокируйте все внешние зависимости
   - Integration тесты: мокируйте только недоступные сервисы
   - E2E тесты: минимальное мокирование

2. **Выбирайте правильную стратегию для БД**
   - In-memory БД для быстрых тестов
   - Testcontainers для интеграционных тестов
   - Мокирование для unit тестов

3. **Мокируйте асинхронный код правильно**
   - Используйте AsyncMock для async функций
   - Тестируйте конкурентность отдельно
   - Контролируйте время выполнения

### ❌ Don'ts

1. **Не создавайте слишком сложные моки**
2. **Не мокируйте то, что тестируете**
3. **Не забывайте проверять вызовы моков**
4. **Не игнорируйте async/await особенности**
5. **Не полагайтесь только на моки для интеграционных тестов**

## 🔮 Следующие шаги

В следующей главе мы изучим **TDD и архитектурные паттерны** — как правильно проектировать приложения с учетом тестируемости.

## 🧪 Проверьте свои знания

<div class="quiz-container" id="advanced-mocking-quiz">
<script type="application/json">
{
  "title": "Продвинутое мокирование",
  "description": "Проверьте понимание продвинутых техник мокирования сложных зависимостей",
  "icon": "🎭",
  "questions": [
    {
      "question": "Какая стратегия лучше всего подходит для быстрого тестирования репозитория с БД?",
      "type": "single",
      "options": [
        {"text": "In-Memory SQLite база данных", "correct": true},
        {"text": "Создание отдельной тестовой БД на PostgreSQL", "correct": false},
        {"text": "Мокирование всех методов репозитория", "correct": false},
        {"text": "Использование файловой БД на диске", "correct": false}
      ],
      "explanation": "In-Memory SQLite идеально подходит для быстрых unit тестов, так как создается в памяти и не требует дополнительной настройки.",
      "points": 1
    },
    {
      "question": "Что такое Fake объект в отличие от Mock объекта?",
      "type": "single",
      "options": [
        {"text": "Fake имеет реальную логику, а Mock просто записывает вызовы", "correct": true},
        {"text": "Fake проще в использовании, чем Mock", "correct": false},
        {"text": "Fake работает только с базами данных", "correct": false},
        {"text": "Fake не может выбрасывать исключения", "correct": false}
      ],
      "explanation": "Fake объекты содержат реальную (упрощенную) логику, в то время как Mock объекты просто записывают вызовы и возвращают предопределенные значения.",
      "points": 1
    },
    {
      "question": "Какие библиотеки используются для мокирования HTTP запросов? (выберите все правильные)",
      "type": "multiple",
      "options": [
        {"text": "responses - для мокирования requests", "correct": true},
        {"text": "httpx-mock - для мокирования httpx", "correct": true},
        {"text": "pytest-mock - для общего мокирования", "correct": false},
        {"text": "requests-mock - для мокирования requests", "correct": true},
        {"text": "unittest.mock - для создания mock объектов", "correct": false}
      ],
      "explanation": "responses и requests-mock используются для мокирования requests, httpx-mock - для httpx, pytest-mock предоставляет удобные фикстуры.",
      "points": 2
    },
    {
      "question": "Как правильно мокировать асинхронные функции?",
      "type": "single",
      "options": [
        {"text": "Использовать AsyncMock вместо Mock", "correct": true},
        {"text": "Обычный Mock работает с async функциями автоматически", "correct": false},
        {"text": "Нужно использовать patch.coroutine", "correct": false},
        {"text": "Async функции нельзя мокировать", "correct": false}
      ],
      "explanation": "AsyncMock специально предназначен для мокирования асинхронных функций и поддерживает await.",
      "points": 1
    },
    {
      "question": "Что такое Circuit Breaker паттерн в контексте мокирования?",
      "type": "single",
      "options": [
        {"text": "Механизм защиты от каскадных сбоев в распределенных системах", "correct": true},
        {"text": "Способ обхода ограничений мокирования", "correct": false},
        {"text": "Метод оптимизации тестов", "correct": false},
        {"text": "Паттерн для работы с базами данных", "correct": false}
      ],
      "explanation": "Circuit Breaker предотвращает повторные вызовы неработающего сервиса, переходя в состояние OPEN после нескольких сбоев.",
      "points": 1
    },
    {
      "question": "Как правильно мокировать время и даты в тестах?",
      "type": "single",
      "options": [
        {"text": "Использовать monkeypatch.setattr для datetime.now", "correct": true},
        {"text": "Перезапускать сервер для изменения времени", "correct": false},
        {"text": "Использовать специальную библиотеку time-machine", "correct": false},
        {"text": "Время в тестах нельзя контролировать", "correct": false}
      ],
      "explanation": "monkeypatch.setattr позволяет заменить datetime.now на функцию, возвращающую фиксированное время для тестов.",
      "points": 1
    }
  ]
}
</script>
</div>

---

## 🔗 Связанные темы

- **[Mock объекты](08_mocking.md)** - основы мокирования
- **[Pytest фреймворк](06_pytest.md)** - продвинутые fixtures
- **[Интеграционное тестирование](09_integration_testing.md)** - моки в интеграционных тестах
- **[TDD в веб-разработке](10_web_development_tdd.md)** - мокирование в веб-приложениях
- **[Стратегии работы с Legacy Code](17_legacy_code_strategies.md)** - мокирование legacy кода
- **[TDD и архитектура](19_tdd_architecture.md)** - мокирование и архитектура

**Следующая глава:** [TDD и архитектура приложения](19_tdd_architecture.md)

*🎭 Помните: мокирование — это искусство создания управляемой реальности для ваших тестов!*
