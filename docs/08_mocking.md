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

## 🎯 Следующие шаги

В следующей главе мы изучим интеграционное тестирование — как тестировать взаимодействие между компонентами системы.

---

**Следующая глава:** [Интеграционное тестирование](09_integration_testing.md)

*🎭 Моки освоены — переходим к тестированию взаимодействий!*
