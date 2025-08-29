# Mock объекты и изоляция тестов

## 🎯 Введение в мокирование

Мокирование — это техника замены реальных зависимостей на контролируемые "поддельные" объекты (моки) во время тестирования. Это критически важно для создания быстрых, надежных и изолированных unit тестов.

## 🤔 Зачем нужны моки?

### Проблемы без мокирования:

```python
# ❌ Тест без мокирования
def test_user_registration():
    """Проблемный тест регистрации пользователя."""
    # Зависит от реальной БД
    database = PostgreSQLDatabase("real_db_connection")
    
    # Зависит от внешнего API
    email_service = SMTPEmailService("smtp.gmail.com")
    
    # Зависит от файловой системы
    file_storage = FileStorage("/real/storage/path")
    
    user_service = UserService(database, email_service, file_storage)
    
    # Медленно, ненадежно, может сломаться
    user = user_service.register("test@example.com", "password")
    
    assert user.is_active == False  # Зависит от email подтверждения
```

### Решение с мокированием:

```python
# ✅ Тест с мокированием
def test_user_registration(mocker):
    """Изолированный тест регистрации."""
    # Мокируем зависимости
    mock_database = mocker.Mock()
    mock_email_service = mocker.Mock()
    mock_file_storage = mocker.Mock()
    
    # Настраиваем поведение моков
    mock_database.save.return_value = User(id=1, email="test@example.com")
    mock_email_service.send_confirmation.return_value = True
    
    user_service = UserService(mock_database, mock_email_service, mock_file_storage)
    
    # Быстрый, надежный, изолированный тест
    user = user_service.register("test@example.com", "password")
    
    assert user.email == "test@example.com"
    mock_database.save.assert_called_once()
    mock_email_service.send_confirmation.assert_called_once()
```

## 🎭 Типы тестовых дублеров

### 1. Dummy (Заглушка)
Объекты, которые передаются, но никогда не используются.

```python
def test_user_creation_with_dummy():
    """Dummy объект только для заполнения параметров."""
    dummy_logger = object()  # Не используется в тесте
    
    user_service = UserService(logger=dummy_logger)
    user = user_service.create_simple_user("John")
    
    assert user.name == "John"
```

### 2. Fake (Подделка)
Упрощенная рабочая реализация.

```python
class FakeDatabase:
    """Поддельная БД для тестов."""
    
    def __init__(self):
        self.users = {}
        self.next_id = 1
    
    def save(self, user):
        user.id = self.next_id
        self.users[self.next_id] = user
        self.next_id += 1
        return user
    
    def find_by_email(self, email):
        for user in self.users.values():
            if user.email == email:
                return user
        return None

def test_user_service_with_fake():
    """Тест с fake БД."""
    fake_db = FakeDatabase()
    user_service = UserService(database=fake_db)
    
    # Реальная логика, но с поддельной БД
    user = user_service.register("test@example.com", "password")
    found_user = user_service.find_by_email("test@example.com")
    
    assert found_user.email == user.email
```

### 3. Stub (Заглушка)
Предоставляет заранее подготовленные ответы на вызовы.

```python
class StubEmailService:
    """Заглушка email сервиса."""
    
    def __init__(self, should_succeed=True):
        self.should_succeed = should_succeed
        self.sent_emails = []
    
    def send_email(self, to, subject, body):
        if self.should_succeed:
            self.sent_emails.append((to, subject, body))
            return True
        else:
            raise EmailSendError("Failed to send email")

def test_notification_with_stub():
    """Тест с заглушкой email сервиса."""
    stub_email = StubEmailService(should_succeed=True)
    notification_service = NotificationService(email_service=stub_email)
    
    notification_service.send_welcome_email("user@example.com")
    
    assert len(stub_email.sent_emails) == 1
    assert stub_email.sent_emails[0][0] == "user@example.com"
```

### 4. Spy (Шпион)
Записывает информацию о том, как они были вызваны.

```python
class SpyLogger:
    """Шпион для логгера."""
    
    def __init__(self, real_logger):
        self.real_logger = real_logger
        self.logged_messages = []
    
    def log(self, level, message):
        self.logged_messages.append((level, message))
        return self.real_logger.log(level, message)

def test_error_handling_with_spy():
    """Тест с шпионом логгера."""
    real_logger = FileLogger("app.log")
    spy_logger = SpyLogger(real_logger)
    
    service = PaymentService(logger=spy_logger)
    
    with pytest.raises(PaymentError):
        service.process_payment(-100)  # Невалидная сумма
    
    # Проверяем что ошибка была залогирована
    assert len(spy_logger.logged_messages) == 1
    assert spy_logger.logged_messages[0][0] == "ERROR"
```

### 5. Mock (Мок)
Проверяет корректность взаимодействия с объектом.

```python
def test_payment_processing_with_mock(mocker):
    """Тест с мокированием платежного шлюза."""
    mock_payment_gateway = mocker.Mock()
    mock_payment_gateway.charge.return_value = PaymentResult(
        transaction_id="TX123",
        status="success"
    )
    
    payment_service = PaymentService(gateway=mock_payment_gateway)
    
    result = payment_service.process_payment(100, "card_token_123")
    
    # Проверяем взаимодействие
    mock_payment_gateway.charge.assert_called_once_with(
        amount=100,
        payment_method="card_token_123"
    )
    assert result.transaction_id == "TX123"
```

## 🛠 unittest.mock в деталях

### Создание базовых моков

```python
from unittest.mock import Mock, MagicMock

def test_basic_mock_usage():
    """Базовое использование Mock."""
    # Создание мока
    mock_service = Mock()
    
    # Настройка возвращаемого значения
    mock_service.get_user.return_value = User("John", "john@example.com")
    
    # Использование мока
    user = mock_service.get_user("123")
    
    # Проверки
    assert user.name == "John"
    mock_service.get_user.assert_called_once_with("123")

def test_magic_mock_special_methods():
    """MagicMock поддерживает магические методы."""
    mock_list = MagicMock()
    mock_list.__len__.return_value = 3
    mock_list.__getitem__.side_effect = lambda i: f"item_{i}"
    
    # Использование как обычный объект
    assert len(mock_list) == 3
    assert mock_list[0] == "item_0"
    assert mock_list[1] == "item_1"
```

### Настройка поведения моков

```python
def test_mock_return_values():
    """Различные способы настройки возвращаемых значений."""
    mock_api = Mock()
    
    # Простое возвращаемое значение
    mock_api.get_data.return_value = {"status": "success"}
    
    # Последовательность значений
    mock_api.get_status.side_effect = ["pending", "processing", "completed"]
    
    # Функция как side_effect
    def calculate_tax(amount):
        return amount * 0.1
    mock_api.calculate_tax.side_effect = calculate_tax
    
    # Исключение
    mock_api.delete_user.side_effect = PermissionError("Access denied")
    
    # Тестирование
    assert mock_api.get_data() == {"status": "success"}
    assert mock_api.get_status() == "pending"
    assert mock_api.get_status() == "processing"
    assert mock_api.calculate_tax(100) == 10
    
    with pytest.raises(PermissionError):
        mock_api.delete_user("123")
```

### Проверка вызовов

```python
def test_mock_call_verification():
    """Проверка вызовов моков."""
    mock_service = Mock()
    
    # Вызываем методы
    mock_service.create_user("john@example.com", name="John")
    mock_service.send_email("john@example.com", "Welcome!")
    mock_service.create_user("jane@example.com", name="Jane")
    
    # Проверки вызовов
    mock_service.create_user.assert_called_with("jane@example.com", name="Jane")
    mock_service.send_email.assert_called_once_with("john@example.com", "Welcome!")
    
    # Проверка количества вызовов
    assert mock_service.create_user.call_count == 2
    
    # Проверка всех вызовов
    expected_calls = [
        call("john@example.com", name="John"),
        call("jane@example.com", name="Jane")
    ]
    mock_service.create_user.assert_has_calls(expected_calls)
    
    # Проверка что метод НЕ вызывался
    mock_service.delete_user.assert_not_called()
```

## 🎭 Патчинг с @patch

### Декоратор @patch

```python
from unittest.mock import patch
import requests

# Тестируемый код
class WeatherService:
    def get_temperature(self, city):
        response = requests.get(f"http://api.weather.com/{city}")
        return response.json()["temperature"]

class TestWeatherService:
    
    @patch('requests.get')
    def test_get_temperature_success(self, mock_get):
        """Тест успешного получения температуры."""
        # Настройка мока
        mock_response = Mock()
        mock_response.json.return_value = {"temperature": 25}
        mock_get.return_value = mock_response
        
        # Тест
        service = WeatherService()
        temperature = service.get_temperature("Moscow")
        
        # Проверки
        assert temperature == 25
        mock_get.assert_called_once_with("http://api.weather.com/Moscow")
    
    @patch('requests.get')
    def test_get_temperature_api_error(self, mock_get):
        """Тест обработки ошибки API."""
        mock_get.side_effect = requests.RequestException("API unavailable")
        
        service = WeatherService()
        
        with pytest.raises(requests.RequestException):
            service.get_temperature("Moscow")
```

### Множественное патчинг

```python
class EmailNotificationService:
    def __init__(self, email_client, user_repository, template_engine):
        self.email_client = email_client
        self.user_repository = user_repository
        self.template_engine = template_engine
    
    def send_welcome_email(self, user_id):
        user = self.user_repository.find_by_id(user_id)
        template = self.template_engine.render("welcome", user=user)
        return self.email_client.send(user.email, "Welcome!", template)

class TestEmailNotificationService:
    
    @patch('myapp.services.TemplateEngine')
    @patch('myapp.services.UserRepository') 
    @patch('myapp.services.EmailClient')
    def test_send_welcome_email(self, mock_email_client, mock_user_repo, mock_template_engine):
        """Тест отправки приветственного email."""
        # Настройка моков
        mock_user = Mock()
        mock_user.email = "user@example.com"
        mock_user_repo.find_by_id.return_value = mock_user
        
        mock_template_engine.render.return_value = "<h1>Welcome!</h1>"
        mock_email_client.send.return_value = True
        
        # Создание сервиса с моками
        service = EmailNotificationService(
            mock_email_client,
            mock_user_repo, 
            mock_template_engine
        )
        
        # Тест
        result = service.send_welcome_email(123)
        
        # Проверки
        assert result == True
        mock_user_repo.find_by_id.assert_called_once_with(123)
        mock_template_engine.render.assert_called_once_with("welcome", user=mock_user)
        mock_email_client.send.assert_called_once_with(
            "user@example.com", 
            "Welcome!", 
            "<h1>Welcome!</h1>"
        )
```

### Контекстный менеджер patch

```python
def test_with_context_manager():
    """Использование patch как контекстного менеджера."""
    service = FileProcessingService()
    
    with patch('builtins.open', mock_open(read_data="test data")) as mock_file:
        content = service.read_file("test.txt")
        
        assert content == "test data"
        mock_file.assert_called_once_with("test.txt", "r")

def test_temporary_patch():
    """Временное патчинг в части теста."""
    service = ConfigService()
    
    # Нормальное поведение
    assert service.get_env("PATH") is not None
    
    # Временный патч
    with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
        assert service.get_env("TEST_VAR") == "test_value"
    
    # Патч больше не действует
    assert service.get_env("TEST_VAR") is None
```

## 🎯 pytest-mock: Упрощенное мокирование

### Fixture mocker

```python
import pytest

def test_with_pytest_mock(mocker):
    """Использование pytest-mock."""
    # Патчинг через mocker fixture
    mock_requests = mocker.patch('requests.get')
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"data": "test"}
    mock_requests.return_value = mock_response
    
    # Создание обычных моков
    mock_service = mocker.Mock()
    mock_service.process.return_value = "processed"
    
    # Тест
    api_client = APIClient()
    result = api_client.fetch_data("https://api.example.com")
    
    assert result == {"data": "test"}
    mock_requests.assert_called_once()
```

### Spy функциональность

```python
def test_spy_on_real_object(mocker):
    """Шпионаж за реальным объектом."""
    real_calculator = Calculator()
    
    # Создаем шпиона
    spy_add = mocker.spy(real_calculator, 'add')
    
    # Используем реальный объект
    result = real_calculator.add(2, 3)
    
    # Проверяем что метод вызывался
    assert result == 5  # Реальный результат
    spy_add.assert_called_once_with(2, 3)
```

## 🏗 Паттерны мокирования в TDD

### 1. Mock Injection Pattern

```python
class OrderService:
    """Сервис заказов с инъекцией зависимостей."""
    
    def __init__(self, payment_gateway, inventory_service, email_service):
        self.payment_gateway = payment_gateway
        self.inventory_service = inventory_service
        self.email_service = email_service
    
    def place_order(self, order):
        # Проверяем наличие товара
        if not self.inventory_service.is_available(order.product_id, order.quantity):
            raise OutOfStockError()
        
        # Обрабатываем платеж
        payment_result = self.payment_gateway.charge(order.total_amount)
        if not payment_result.success:
            raise PaymentError()
        
        # Резервируем товар
        self.inventory_service.reserve(order.product_id, order.quantity)
        
        # Отправляем подтверждение
        self.email_service.send_order_confirmation(order.customer_email, order)
        
        return Order(id=payment_result.transaction_id, status="confirmed")

def test_place_order_success(mocker):
    """Тест успешного размещения заказа."""
    # Создаем моки
    mock_payment = mocker.Mock()
    mock_inventory = mocker.Mock()
    mock_email = mocker.Mock()
    
    # Настраиваем успешное поведение
    mock_inventory.is_available.return_value = True
    mock_payment.charge.return_value = PaymentResult(
        success=True, 
        transaction_id="TX123"
    )
    mock_email.send_order_confirmation.return_value = True
    
    # Создаем сервис с моками
    service = OrderService(mock_payment, mock_inventory, mock_email)
    
    # Тест
    order = Order(product_id="PROD123", quantity=2, total_amount=100)
    result = service.place_order(order)
    
    # Проверки
    assert result.id == "TX123"
    assert result.status == "confirmed"
    
    # Проверяем взаимодействия
    mock_inventory.is_available.assert_called_once_with("PROD123", 2)
    mock_payment.charge.assert_called_once_with(100)
    mock_inventory.reserve.assert_called_once_with("PROD123", 2)
    mock_email.send_order_confirmation.assert_called_once()
```

### 2. Builder Pattern для моков

```python
class MockUserBuilder:
    """Строитель для мока пользователя."""
    
    def __init__(self):
        self.mock_user = Mock()
        self.mock_user.id = 1
        self.mock_user.email = "user@example.com"
        self.mock_user.name = "Test User"
        self.mock_user.is_active = True
        self.mock_user.roles = []
    
    def with_id(self, user_id):
        self.mock_user.id = user_id
        return self
    
    def with_email(self, email):
        self.mock_user.email = email
        return self
    
    def with_name(self, name):
        self.mock_user.name = name
        return self
    
    def inactive(self):
        self.mock_user.is_active = False
        return self
    
    def with_roles(self, *roles):
        self.mock_user.roles = list(roles)
        return self
    
    def build(self):
        return self.mock_user

def test_admin_access_with_builder():
    """Тест доступа администратора с использованием builder."""
    admin_user = (MockUserBuilder()
                  .with_id(100)
                  .with_email("admin@example.com")
                  .with_roles("admin", "user")
                  .build())
    
    service = UserPermissionService()
    
    assert service.can_access_admin_panel(admin_user) == True

def test_regular_user_access_with_builder():
    """Тест доступа обычного пользователя."""
    regular_user = (MockUserBuilder()
                    .with_id(200)
                    .with_roles("user")
                    .build())
    
    service = UserPermissionService()
    
    assert service.can_access_admin_panel(regular_user) == False
```

## ⚠️ Проблемы и антипаттерны

### 1. Over-Mocking (Чрезмерное мокирование)

```python
# ❌ Плохо: мокируем все подряд
def test_user_full_name_bad(mocker):
    """Перемокированный тест."""
    mock_first_name = mocker.Mock(return_value="John")
    mock_last_name = mocker.Mock(return_value="Doe")
    mock_space = mocker.Mock(return_value=" ")
    
    # Мокируем даже примитивные операции
    mocker.patch('str.__add__', side_effect=lambda a, b: f"{a}{b}")
    
    user = User(first_name=mock_first_name(), last_name=mock_last_name())
    full_name = user.get_full_name()
    
    # Тест ничего не проверяет из реальной логики

# ✅ Хорошо: мокируем только внешние зависимости
def test_user_full_name_good():
    """Правильный тест без лишних моков."""
    user = User(first_name="John", last_name="Doe")
    full_name = user.get_full_name()
    
    assert full_name == "John Doe"
```

### 2. Mock Leakage (Утечка моков)

```python
# ❌ Плохо: моки влияют на другие тесты
class TestUserService:
    
    @patch('myapp.database.connection')
    def test_create_user(self, mock_db):
        mock_db.save.return_value = True
        # Патч остается активным для других тестов
    
    def test_find_user(self):
        # Этот тест может использовать мок из предыдущего теста
        pass

# ✅ Хорошо: изоляция моков
class TestUserService:
    
    def test_create_user(self, mocker):
        mock_db = mocker.patch('myapp.database.connection')
        mock_db.save.return_value = True
        # Мок автоматически очищается после теста
    
    def test_find_user(self):
        # Чистый тест без влияния предыдущих моков
        pass
```

### 3. Mock Reality Mismatch (Несоответствие мока реальности)

```python
# ❌ Плохо: мок не соответствует реальному API
def test_payment_processing_bad(mocker):
    """Мок не соответствует реальному API."""
    mock_gateway = mocker.Mock()
    # Реальный API требует больше параметров
    mock_gateway.charge.return_value = True  
    
    service = PaymentService(mock_gateway)
    result = service.process_payment(100)
    
    # Тест пройдет, но в продакшене сломается
    mock_gateway.charge.assert_called_with(100)

# ✅ Хорошо: мок соответствует реальному интерфейсу
def test_payment_processing_good(mocker):
    """Мок соответствует реальному API."""
    mock_gateway = mocker.Mock()
    mock_gateway.charge.return_value = PaymentResult(
        transaction_id="TX123",
        status="success",
        amount=100
    )
    
    service = PaymentService(mock_gateway)
    result = service.process_payment(100, "card_token")
    
    # Проверяем полный интерфейс
    mock_gateway.charge.assert_called_with(
        amount=100,
        payment_method="card_token",
        currency="USD"  # Параметры как в реальном API
    )
```

## 🎯 Лучшие практики мокирования

### 1. Мокируйте на границах

```python
# ✅ Мокируйте внешние зависимости
@patch('requests.get')  # Внешний HTTP API
@patch('smtplib.SMTP')  # Внешний email сервис
@patch('boto3.client')  # Внешний AWS сервис
def test_data_processing(mock_aws, mock_smtp, mock_requests):
    pass

# ❌ Не мокируйте внутреннюю логику
@patch('myapp.utils.calculate_total')  # Наша функция
def test_order_total(mock_calculate):
    pass
```

### 2. Используйте явные интерфейсы

```python
from abc import ABC, abstractmethod

class PaymentGateway(ABC):
    """Интерфейс платежного шлюза."""
    
    @abstractmethod
    def charge(self, amount: Decimal, payment_method: str) -> PaymentResult:
        pass

class MockPaymentGateway(PaymentGateway):
    """Мок для тестирования."""
    
    def __init__(self):
        self.charges = []
    
    def charge(self, amount: Decimal, payment_method: str) -> PaymentResult:
        self.charges.append((amount, payment_method))
        return PaymentResult(transaction_id="MOCK_TX", status="success")

def test_with_explicit_interface():
    """Тест с явным интерфейсом."""
    mock_gateway = MockPaymentGateway()
    service = PaymentService(mock_gateway)
    
    result = service.process_payment(Decimal("100"), "card_123")
    
    assert result.status == "success"
    assert len(mock_gateway.charges) == 1
```

### 3. Проверяйте важные взаимодействия

```python
def test_audit_logging(mocker):
    """Проверяем что критические действия логируются."""
    mock_audit_logger = mocker.Mock()
    
    service = BankingService(audit_logger=mock_audit_logger)
    service.transfer_money(
        from_account="ACC123",
        to_account="ACC456", 
        amount=Decimal("1000")
    )
    
    # Проверяем что операция залогирована
    mock_audit_logger.log_transaction.assert_called_once_with(
        action="transfer",
        from_account="ACC123",
        to_account="ACC456",
        amount=Decimal("1000"),
        timestamp=mocker.ANY
    )
```

## 🌐 Мокирование внешних сервисов

### 1. REST API мокирование

```python
import responses
import requests

class APIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
    
    def get_user(self, user_id):
        response = requests.get(
            f"{self.base_url}/users/{user_id}",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        response.raise_for_status()
        return response.json()
    
    def create_user(self, user_data):
        response = requests.post(
            f"{self.base_url}/users",
            json=user_data,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        response.raise_for_status()
        return response.json()

@responses.activate
def test_api_client_get_user():
    """Тест получения пользователя через API."""
    responses.add(
        responses.GET,
        "https://api.example.com/users/123",
        json={"id": 123, "name": "John Doe", "email": "john@example.com"},
        status=200
    )
    
    client = APIClient("https://api.example.com", "test-token")
    user = client.get_user(123)
    
    assert user["name"] == "John Doe"
    assert len(responses.calls) == 1
    assert "Bearer test-token" in responses.calls[0].request.headers["Authorization"]

@responses.activate
def test_api_client_error_handling():
    """Тест обработки ошибок API."""
    responses.add(
        responses.GET,
        "https://api.example.com/users/999",
        json={"error": "User not found"},
        status=404
    )
    
    client = APIClient("https://api.example.com", "test-token")
    
    with pytest.raises(requests.HTTPError):
        client.get_user(999)
```

### 2. GraphQL мокирование

```python
import httpx
from unittest.mock import AsyncMock

class GraphQLClient:
    def __init__(self, endpoint):
        self.endpoint = endpoint
    
    async def query(self, query, variables=None):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.endpoint,
                json={"query": query, "variables": variables}
            )
            return response.json()

@pytest.mark.asyncio
async def test_graphql_query(mocker):
    """Тест GraphQL запроса."""
    mock_post = mocker.patch('httpx.AsyncClient.post', new_callable=AsyncMock)
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "data": {
            "user": {
                "id": "123",
                "name": "John Doe",
                "posts": [
                    {"title": "First Post", "content": "Hello World"}
                ]
            }
        }
    }
    mock_post.return_value = mock_response
    
    client = GraphQLClient("https://api.example.com/graphql")
    
    query = """
        query GetUser($id: ID!) {
            user(id: $id) {
                id
                name
                posts {
                    title
                    content
                }
            }
        }
    """
    
    result = await client.query(query, {"id": "123"})
    
    assert result["data"]["user"]["name"] == "John Doe"
    assert len(result["data"]["user"]["posts"]) == 1
    
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[1]["json"]["query"] == query
```

### 3. WebSocket мокирование

```python
import asyncio
import websockets
from unittest.mock import AsyncMock, patch

class WebSocketClient:
    def __init__(self, url):
        self.url = url
        self.websocket = None
    
    async def connect(self):
        self.websocket = await websockets.connect(self.url)
    
    async def send_message(self, message):
        await self.websocket.send(message)
    
    async def receive_message(self):
        return await self.websocket.recv()

@pytest.mark.asyncio
async def test_websocket_communication():
    """Тест WebSocket коммуникации."""
    mock_websocket = AsyncMock()
    mock_websocket.recv.return_value = "pong"
    
    with patch('websockets.connect', return_value=mock_websocket):
        client = WebSocketClient("ws://localhost:8000")
        await client.connect()
        
        await client.send_message("ping")
        response = await client.receive_message()
        
        assert response == "pong"
        mock_websocket.send.assert_called_once_with("ping")
        mock_websocket.recv.assert_called_once()
```

## 🗄️ Продвинутое мокирование баз данных

### 1. Мокирование ORM запросов

```python
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

class UserRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def find_active_users(self):
        return self.session.query(User).filter(User.is_active == True).all()
    
    def find_by_email(self, email):
        return self.session.query(User).filter(User.email == email).first()
    
    def create_user(self, user_data):
        user = User(**user_data)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

def test_user_repository_find_active(mocker):
    """Тест поиска активных пользователей."""
    mock_session = mocker.Mock()
    
    # Настраиваем цепочку вызовов ORM
    mock_query = mocker.Mock()
    mock_filter = mocker.Mock()
    
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.all.return_value = [
        User(id=1, email="user1@example.com", is_active=True),
        User(id=2, email="user2@example.com", is_active=True)
    ]
    
    repository = UserRepository(mock_session)
    users = repository.find_active_users()
    
    assert len(users) == 2
    assert all(user.is_active for user in users)
    
    mock_session.query.assert_called_once_with(User)
    mock_query.filter.assert_called_once()
```

### 2. Мокирование транзакций

```python
class OrderService:
    def __init__(self, session: Session, payment_service):
        self.session = session
        self.payment_service = payment_service
    
    def process_order(self, order_data):
        try:
            # Начинаем транзакцию
            order = Order(**order_data)
            self.session.add(order)
            self.session.flush()  # Получаем ID без commit
            
            # Обрабатываем платеж
            payment_result = self.payment_service.charge(
                order.id, 
                order.total_amount
            )
            
            if payment_result.success:
                order.status = "paid"
                self.session.commit()
                return order
            else:
                self.session.rollback()
                raise PaymentError("Payment failed")
                
        except Exception:
            self.session.rollback()
            raise

def test_order_service_successful_payment(mocker):
    """Тест успешной обработки заказа."""
    mock_session = mocker.Mock()
    mock_payment_service = mocker.Mock()
    
    mock_payment_service.charge.return_value = PaymentResult(success=True)
    
    service = OrderService(mock_session, mock_payment_service)
    order_data = {"product_id": 1, "quantity": 2, "total_amount": 100}
    
    result = service.process_order(order_data)
    
    # Проверяем последовательность операций
    mock_session.add.assert_called_once()
    mock_session.flush.assert_called_once()
    mock_payment_service.charge.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()

def test_order_service_payment_failure(mocker):
    """Тест неуспешной обработки платежа."""
    mock_session = mocker.Mock()
    mock_payment_service = mocker.Mock()
    
    mock_payment_service.charge.return_value = PaymentResult(success=False)
    
    service = OrderService(mock_session, mock_payment_service)
    order_data = {"product_id": 1, "quantity": 2, "total_amount": 100}
    
    with pytest.raises(PaymentError):
        service.process_order(order_data)
    
    # Проверяем откат транзакции
    mock_session.rollback.assert_called_once()
    mock_session.commit.assert_not_called()
```

### 3. Мокирование Redis

```python
import redis
from unittest.mock import Mock

class CacheService:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def get_user_cache(self, user_id):
        cached = self.redis.get(f"user:{user_id}")
        if cached:
            return json.loads(cached)
        return None
    
    def set_user_cache(self, user_id, user_data, ttl=3600):
        self.redis.setex(
            f"user:{user_id}", 
            ttl, 
            json.dumps(user_data)
        )

def test_cache_service_hit(mocker):
    """Тест попадания в кэш."""
    mock_redis = mocker.Mock()
    mock_redis.get.return_value = '{"id": 123, "name": "John"}'
    
    cache_service = CacheService(mock_redis)
    user_data = cache_service.get_user_cache(123)
    
    assert user_data["name"] == "John"
    mock_redis.get.assert_called_once_with("user:123")

def test_cache_service_miss(mocker):
    """Тест промаха кэша."""
    mock_redis = mocker.Mock()
    mock_redis.get.return_value = None
    
    cache_service = CacheService(mock_redis)
    user_data = cache_service.get_user_cache(123)
    
    assert user_data is None
    mock_redis.get.assert_called_once_with("user:123")

def test_cache_service_set(mocker):
    """Тест установки кэша."""
    mock_redis = mocker.Mock()
    
    cache_service = CacheService(mock_redis)
    user_data = {"id": 123, "name": "John"}
    cache_service.set_user_cache(123, user_data, ttl=1800)
    
    mock_redis.setex.assert_called_once_with(
        "user:123", 
        1800, 
        '{"id": 123, "name": "John"}'
    )
```

## ⚡ Мокирование асинхронного кода

### 1. AsyncMock для async/await

```python
import asyncio
import aiohttp
from unittest.mock import AsyncMock

class AsyncAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    async def fetch_data(self, endpoint):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/{endpoint}") as response:
                return await response.json()
    
    async def post_data(self, endpoint, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/{endpoint}", json=data) as response:
                return await response.json()

@pytest.mark.asyncio
async def test_async_api_client_fetch(mocker):
    """Тест асинхронного получения данных."""
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.json.return_value = {"status": "success", "data": [1, 2, 3]}
    
    # Настраиваем async context manager
    mock_session.get.return_value.__aenter__.return_value = mock_response
    
    # Мокируем создание сессии
    mocker.patch('aiohttp.ClientSession', return_value=mock_session)
    
    client = AsyncAPIClient("https://api.example.com")
    result = await client.fetch_data("users")
    
    assert result["status"] == "success"
    assert result["data"] == [1, 2, 3]
    
    mock_session.get.assert_called_once_with("https://api.example.com/users")
    mock_response.json.assert_called_once()

@pytest.mark.asyncio
async def test_async_api_client_post(mocker):
    """Тест асинхронной отправки данных."""
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.json.return_value = {"id": 123, "created": True}
    
    mock_session.post.return_value.__aenter__.return_value = mock_response
    mocker.patch('aiohttp.ClientSession', return_value=mock_session)
    
    client = AsyncAPIClient("https://api.example.com")
    result = await client.post_data("users", {"name": "John"})
    
    assert result["created"] is True
    assert result["id"] == 123
    
    mock_session.post.assert_called_once_with(
        "https://api.example.com/users", 
        json={"name": "John"}
    )
```

### 2. Мокирование asyncio.sleep и таймеров

```python
import asyncio
from unittest.mock import patch, AsyncMock

class RateLimitedService:
    def __init__(self, requests_per_second=10):
        self.requests_per_second = requests_per_second
        self.last_request_time = 0
    
    async def make_request(self, data):
        # Ограничение скорости запросов
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.requests_per_second
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = asyncio.get_event_loop().time()
        return f"Processed: {data}"

@pytest.mark.asyncio
async def test_rate_limited_service():
    """Тест сервиса с ограничением скорости."""
    service = RateLimitedService(requests_per_second=2)  # 2 запроса в секунду
    
    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        # Первый запрос - без задержки
        result1 = await service.make_request("data1")
        assert result1 == "Processed: data1"
        mock_sleep.assert_not_called()
        
        # Второй запрос сразу - должна быть задержка
        result2 = await service.make_request("data2")
        assert result2 == "Processed: data2"
        mock_sleep.assert_called_once()
        
        # Проверяем время задержки (примерно 0.5 секунды для 2 rps)
        call_args = mock_sleep.call_args[0]
        assert 0.4 <= call_args[0] <= 0.6
```

### 3. Мокирование конкурентности

```python
import asyncio
from unittest.mock import AsyncMock, patch

class ConcurrentProcessor:
    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)
    
    async def process_item(self, item):
        async with self.semaphore:
            # Имитация обработки
            await asyncio.sleep(0.1)
            return f"processed_{item}"
    
    async def process_batch(self, items):
        tasks = []
        for item in items:
            task = asyncio.create_task(self.process_item(item))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

@pytest.mark.asyncio
async def test_concurrent_processor():
    """Тест конкурентной обработки."""
    processor = ConcurrentProcessor(max_workers=2)
    
    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        items = ["item1", "item2", "item3", "item4"]
        results = await processor.process_batch(items)
        
        assert len(results) == 4
        assert all(result.startswith("processed_") for result in results)
        
        # Проверяем что sleep вызывался для каждого элемента
        assert mock_sleep.call_count == 4
```

## 📁 Мокирование файловых операций

### 1. Мокирование pathlib

```python
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

class ConfigManager:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
    
    def load_config(self, config_name: str):
        config_file = self.config_dir / f"{config_name}.json"
        
        if not config_file.exists():
            return {}
        
        with config_file.open('r') as f:
            return json.load(f)
    
    def save_config(self, config_name: str, config_data: dict):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config_file = self.config_dir / f"{config_name}.json"
        
        with config_file.open('w') as f:
            json.dump(config_data, f, indent=2)

def test_config_manager_load_existing(mocker):
    """Тест загрузки существующего конфига."""
    config_data = {"database_url": "localhost", "debug": True}
    
    # Мокируем pathlib операции
    mock_path = mocker.Mock()
    mock_path.exists.return_value = True
    mock_path.open.return_value.__enter__.return_value = mock_open(
        read_data=json.dumps(config_data)
    ).return_value
    
    mocker.patch('pathlib.Path.__truediv__', return_value=mock_path)
    
    manager = ConfigManager(Path("/app/config"))
    config = manager.load_config("database")
    
    assert config == config_data
    mock_path.exists.assert_called_once()

def test_config_manager_save(mocker):
    """Тест сохранения конфига."""
    config_data = {"database_url": "localhost", "debug": True}
    
    mock_config_dir = mocker.Mock()
    mock_config_file = mocker.Mock()
    
    mock_config_dir.__truediv__.return_value = mock_config_file
    
    # Мокируем file operations
    mock_file = mock_open()
    mock_config_file.open.return_value = mock_file.return_value
    
    manager = ConfigManager(mock_config_dir)
    manager.save_config("database", config_data)
    
    mock_config_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)
    mock_config_file.open.assert_called_once_with('w')
```

### 2. Мокирование os.environ

```python
import os
from unittest.mock import patch

class EnvironmentConfig:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///default.db")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.secret_key = os.getenv("SECRET_KEY")
    
    def validate(self):
        if not self.secret_key:
            raise ValueError("SECRET_KEY environment variable is required")
        
        if len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")

def test_environment_config_defaults():
    """Тест значений по умолчанию."""
    with patch.dict(os.environ, {}, clear=True):
        config = EnvironmentConfig()
        
        assert config.database_url == "sqlite:///default.db"
        assert config.debug is False
        assert config.secret_key is None

def test_environment_config_custom_values():
    """Тест пользовательских значений."""
    env_vars = {
        "DATABASE_URL": "postgresql://localhost/mydb",
        "DEBUG": "true",
        "SECRET_KEY": "a" * 32
    }
    
    with patch.dict(os.environ, env_vars, clear=True):
        config = EnvironmentConfig()
        
        assert config.database_url == "postgresql://localhost/mydb"
        assert config.debug is True
        assert config.secret_key == "a" * 32

def test_environment_config_validation_missing_key():
    """Тест валидации отсутствующего ключа."""
    with patch.dict(os.environ, {}, clear=True):
        config = EnvironmentConfig()
        
        with pytest.raises(ValueError, match="SECRET_KEY environment variable is required"):
            config.validate()

def test_environment_config_validation_short_key():
    """Тест валидации короткого ключа."""
    with patch.dict(os.environ, {"SECRET_KEY": "short"}, clear=True):
        config = EnvironmentConfig()
        
        with pytest.raises(ValueError, match="SECRET_KEY must be at least 32 characters"):
            config.validate()
```

## 🔄 Мокирование циркулярных зависимостей

### 1. Разрешение циркулярных зависимостей

```python
# Проблема: циркулярная зависимость
class UserService:
    def __init__(self, order_service):
        self.order_service = order_service
    
    def get_user_with_orders(self, user_id):
        user = self.get_user(user_id)
        orders = self.order_service.get_user_orders(user_id)
        return {"user": user, "orders": orders}

class OrderService:
    def __init__(self, user_service):
        self.user_service = user_service
    
    def get_order_with_user(self, order_id):
        order = self.get_order(order_id)
        user = self.user_service.get_user(order.user_id)
        return {"order": order, "user": user}

# Решение через мокирование
def test_user_service_with_orders(mocker):
    """Тест сервиса пользователей с заказами."""
    # Мокируем OrderService
    mock_order_service = mocker.Mock()
    mock_order_service.get_user_orders.return_value = [
        Order(id=1, user_id=123, total=100),
        Order(id=2, user_id=123, total=200)
    ]
    
    # Создаем UserService с мокированным OrderService
    user_service = UserService(mock_order_service)
    
    # Мокируем get_user метод
    mocker.patch.object(user_service, 'get_user', return_value=User(id=123, name="John"))
    
    result = user_service.get_user_with_orders(123)
    
    assert result["user"].name == "John"
    assert len(result["orders"]) == 2
    assert result["orders"][0].total == 100
    
    mock_order_service.get_user_orders.assert_called_once_with(123)
```

### 2. Dependency Injection для тестирования

```python
from typing import Protocol

class UserRepositoryProtocol(Protocol):
    def find_by_id(self, user_id: int) -> User: ...

class OrderRepositoryProtocol(Protocol):
    def find_by_user_id(self, user_id: int) -> list[Order]: ...

class UserService:
    def __init__(self, user_repo: UserRepositoryProtocol, order_repo: OrderRepositoryProtocol):
        self.user_repo = user_repo
        self.order_repo = order_repo
    
    def get_user_summary(self, user_id: int):
        user = self.user_repo.find_by_id(user_id)
        orders = self.order_repo.find_by_user_id(user_id)
        
        return {
            "user": user,
            "total_orders": len(orders),
            "total_spent": sum(order.total for order in orders)
        }

def test_user_service_summary(mocker):
    """Тест сводки пользователя."""
    mock_user_repo = mocker.Mock()
    mock_order_repo = mocker.Mock()
    
    mock_user_repo.find_by_id.return_value = User(id=123, name="John")
    mock_order_repo.find_by_user_id.return_value = [
        Order(id=1, total=100),
        Order(id=2, total=200),
        Order(id=3, total=150)
    ]
    
    service = UserService(mock_user_repo, mock_order_repo)
    summary = service.get_user_summary(123)
    
    assert summary["user"].name == "John"
    assert summary["total_orders"] == 3
    assert summary["total_spent"] == 450
    
    mock_user_repo.find_by_id.assert_called_once_with(123)
    mock_order_repo.find_by_user_id.assert_called_once_with(123)
```

## 🎯 Продвинутые техники верификации

### 1. Argument Captors

```python
from unittest.mock import Mock, call

class EmailService:
    def __init__(self, smtp_client):
        self.smtp_client = smtp_client
    
    def send_bulk_emails(self, recipients, template, **template_vars):
        sent_count = 0
        for recipient in recipients:
            try:
                message = template.format(name=recipient.get('name', 'User'), **template_vars)
                self.smtp_client.send(
                    to=recipient['email'],
                    subject=f"Message for {recipient.get('name', 'User')}",
                    body=message
                )
                sent_count += 1
            except Exception:
                continue
        
        return sent_count

def test_email_service_bulk_send(mocker):
    """Тест массовой рассылки с захватом аргументов."""
    mock_smtp = mocker.Mock()
    mock_smtp.send.return_value = True
    
    service = EmailService(mock_smtp)
    
    recipients = [
        {"email": "john@example.com", "name": "John"},
        {"email": "jane@example.com", "name": "Jane"},
        {"email": "bob@example.com", "name": "Bob"}
    ]
    
    template = "Hello {name}! Welcome to our {product}!"
    sent_count = service.send_bulk_emails(recipients, template, product="Service")
    
    assert sent_count == 3
    assert mock_smtp.send.call_count == 3
    
    # Проверяем все вызовы
    expected_calls = [
        call(
            to="john@example.com",
            subject="Message for John",
            body="Hello John! Welcome to our Service!"
        ),
        call(
            to="jane@example.com",
            subject="Message for Jane",
            body="Hello Jane! Welcome to our Service!"
        ),
        call(
            to="bob@example.com",
            subject="Message for Bob",
            body="Hello Bob! Welcome to our Service!"
        )
    ]
    
    mock_smtp.send.assert_has_calls(expected_calls, any_order=False)
    
    # Альтернативный способ - анализ call_args_list
    call_args_list = mock_smtp.send.call_args_list
    sent_emails = [call[1]['to'] for call in call_args_list]
    assert "john@example.com" in sent_emails
    assert "jane@example.com" in sent_emails
    assert "bob@example.com" in sent_emails
```

### 2. Поведенческая верификация

```python
class AuditLogger:
    def __init__(self, log_storage):
        self.log_storage = log_storage
    
    def log_action(self, user_id, action, resource_id, details=None):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource_id": resource_id,
            "details": details or {}
        }
        self.log_storage.store(log_entry)

class BankingService:
    def __init__(self, account_repo, audit_logger):
        self.account_repo = account_repo
        self.audit_logger = audit_logger
    
    def transfer_money(self, from_account_id, to_account_id, amount, user_id):
        # Получаем аккаунты
        from_account = self.account_repo.get(from_account_id)
        to_account = self.account_repo.get(to_account_id)
        
        # Проверяем баланс
        if from_account.balance < amount:
            self.audit_logger.log_action(
                user_id, "transfer_failed", from_account_id,
                {"reason": "insufficient_funds", "amount": amount}
            )
            raise InsufficientFundsError()
        
        # Выполняем перевод
        from_account.balance -= amount
        to_account.balance += amount
        
        self.account_repo.save(from_account)
        self.account_repo.save(to_account)
        
        # Логируем успешный перевод
        self.audit_logger.log_action(
            user_id, "transfer_completed", from_account_id,
            {
                "to_account": to_account_id,
                "amount": amount,
                "from_balance": from_account.balance,
                "to_balance": to_account.balance
            }
        )

def test_banking_service_successful_transfer(mocker):
    """Тест успешного перевода с проверкой аудита."""
    mock_repo = mocker.Mock()
    mock_audit = mocker.Mock()
    
    # Настраиваем аккаунты
    from_account = Account(id=1, balance=1000)
    to_account = Account(id=2, balance=500)
    
    mock_repo.get.side_effect = lambda account_id: {
        1: from_account,
        2: to_account
    }[account_id]
    
    service = BankingService(mock_repo, mock_audit)
    
    # Выполняем перевод
    service.transfer_money(
        from_account_id=1,
        to_account_id=2,
        amount=200,
        user_id=99
    )
    
    # Проверяем изменения балансов
    assert from_account.balance == 800
    assert to_account.balance == 700
    
    # Проверяем сохранение
    assert mock_repo.save.call_count == 2
    
    # Проверяем аудит лог
    mock_audit.log_action.assert_called_once()
    audit_call = mock_audit.log_action.call_args
    
    assert audit_call[0][0] == 99  # user_id
    assert audit_call[0][1] == "transfer_completed"  # action
    assert audit_call[0][2] == 1  # resource_id
    
    details = audit_call[0][3]
    assert details["amount"] == 200
    assert details["to_account"] == 2
    assert details["from_balance"] == 800
    assert details["to_balance"] == 700

def test_banking_service_insufficient_funds(mocker):
    """Тест перевода с недостаточными средствами."""
    mock_repo = mocker.Mock()
    mock_audit = mocker.Mock()
    
    from_account = Account(id=1, balance=100)  # Недостаточно средств
    mock_repo.get.return_value = from_account
    
    service = BankingService(mock_repo, mock_audit)
    
    with pytest.raises(InsufficientFundsError):
        service.transfer_money(
            from_account_id=1,
            to_account_id=2,
            amount=200,
            user_id=99
        )
    
    # Проверяем что ничего не сохранили
    mock_repo.save.assert_not_called()
    
    # Проверяем аудит лог ошибки
    mock_audit.log_action.assert_called_once_with(
        99, "transfer_failed", 1,
        {"reason": "insufficient_funds", "amount": 200}
    )
```

## 🎯 Следующие шаги

В следующей главе мы изучим интеграционное тестирование — как тестировать взаимодействие между компонентами системы.

Также рекомендуем изучить:
- [Продвинутое мокирование](18_advanced_mocking.md) — для более сложных сценариев
- [Тестирование обработки ошибок](15_error_handling_tdd.md) — для работы с исключениями в моках

## 🧪 Проверьте свои знания

<div class="quiz-container" id="mocking-quiz">
<script type="application/json">
{
  "title": "Mock объекты и изоляция тестов",
  "description": "Проверьте знание техник мокирования и изоляции в тестах",
  "icon": "🎭",
  "questions": [
    {
      "question": "В чем основная цель использования mock объектов в тестах?",
      "type": "single",
      "options": [
        {"text": "Ускорить выполнение тестов", "correct": false},
        {"text": "Изолировать тестируемый код от внешних зависимостей", "correct": true},
        {"text": "Упростить написание тестов", "correct": false},
        {"text": "Заменить настоящие объекты более простыми", "correct": false}
      ],
      "explanation": "Основная цель mock объектов - изолировать тестируемый код от внешних зависимостей (БД, API, файловая система), чтобы тесты были независимыми и предсказуемыми.",
      "points": 1
    },
    {
      "question": "Какие типы test doubles существуют? (выберите все правильные)",
      "type": "multiple",
      "options": [
        {"text": "Dummy - объекты-заглушки без поведения", "correct": true},
        {"text": "Stub - объекты с предопределенными ответами", "correct": true},
        {"text": "Spy - объекты, которые записывают информацию о вызовах", "correct": true},
        {"text": "Mock - объекты с ожиданиями о том, как они будут вызваны", "correct": true},
        {"text": "Fake - объекты с упрощенной реализацией", "correct": true}
      ],
      "explanation": "Существует 5 типов test doubles: Dummy (заглушки), Stub (предопределенные ответы), Spy (запись вызовов), Mock (ожидания), Fake (упрощенная реализация).",
      "points": 2
    },
    {
      "question": "Как правильно замокать метод в pytest-mock?",
      "type": "single",
      "options": [
        {"text": "mocker.mock('module.Class.method')", "correct": false},
        {"text": "mocker.patch('module.Class.method')", "correct": true},
        {"text": "mocker.replace('module.Class.method')", "correct": false},
        {"text": "mocker.stub('module.Class.method')", "correct": false}
      ],
      "explanation": "В pytest-mock правильный синтаксис: mocker.patch('module.Class.method'). Это создает mock объект, который заменяет оригинальный метод.",
      "points": 1
    },
    {
      "question": "Что делает assert_called_once_with() в mock объекте?",
      "type": "single",
      "options": [
        {"text": "Проверяет, что метод был вызван хотя бы один раз", "correct": false},
        {"text": "Проверяет, что метод был вызван ровно один раз с указанными аргументами", "correct": true},
        {"text": "Проверяет, что метод не был вызван", "correct": false},
        {"text": "Проверяет количество вызовов метода", "correct": false}
      ],
      "explanation": "assert_called_once_with() проверяет, что метод был вызван ровно один раз с точно указанными аргументами. Это комбинация проверки количества вызовов и аргументов.",
      "points": 1
    },
    {
      "question": "Какой правильный способ тестирования исключений с mock объектами?",
      "type": "single",
      "options": [
        {"text": "mock_method.side_effect = ValueError('Error')", "correct": true},
        {"text": "mock_method.return_value = ValueError('Error')", "correct": false},
        {"text": "mock_method.raises = ValueError('Error')", "correct": false},
        {"text": "mock_method.exception = ValueError('Error')", "correct": false}
      ],
      "explanation": "Для эмуляции исключений в mock объектах используется side_effect. Это заставляет mock объект выбросить исключение при вызове.",
      "points": 1
    },
    {
      "question": "В чем разница между @patch и mocker.patch?",
      "type": "single",
      "options": [
        {"text": "@patch работает только с классами, mocker.patch только с функциями", "correct": false},
        {"text": "@patch - это декоратор, mocker.patch используется внутри теста", "correct": true},
        {"text": "Никакой разницы нет", "correct": false},
        {"text": "@patch быстрее работает", "correct": false}
      ],
      "explanation": "@patch - это декоратор, который применяется к функции теста, а mocker.patch - это метод фикстуры pytest-mock, который вызывается внутри теста.",
      "points": 1
    }
  ]
}
</script>
</div>

## 🚀 Интерактивная практика

### 📧 Email сервис с Mock объектами

Готовы применить мокирование на практике? Создайте email сервис с полной изоляцией зависимостей:

**[🎯 Интерактивное упражнение: Email сервис с Mock объектами](exercises/08_mocking_email_service.md)**

В этом упражнении вы:
- Создадите архитектуру с Dependency Injection
- Освоите все виды Test Doubles (Dummy, Stub, Spy, Mock, Fake)
- Изучите продвинутые техники мокирования (`side_effect`, функции, последовательности)
- Протестируете различные сценарии ошибок и исключений
- Поработаете с `@patch` декораторами и `pytest-mock`

Это упражнение покажет, как создавать быстрые, надежные и изолированные тесты для сложных систем!

---

**Следующая глава:** [Интеграционное тестирование](09_integration_testing.md)

*🎭 Моки освоены — переходим к тестированию взаимодействий!*
