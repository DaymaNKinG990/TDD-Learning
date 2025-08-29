# TDD и архитектура приложения

## 🎯 Введение

Test-Driven Development влияет не только на качество кода, но и на архитектуру всего приложения. TDD естественным образом ведет к созданию слабо связанной, высоко тестируемой архитектуры, которая следует лучшим практикам проектирования. В этой главе мы изучим, как TDD формирует архитектурные решения и какие паттерны лучше всего подходят для тестируемых систем.

## 🏗️ Влияние TDD на архитектуру

### Основные принципы

TDD способствует созданию архитектуры, которая:

1. **Слабо связана** — компоненты не зависят друг от друга напрямую
2. **Высоко связна** — компоненты сфокусированы на одной ответственности
3. **Легко тестируема** — каждый компонент можно тестировать изолированно
4. **Гибка к изменениям** — новые требования легко интегрируются

### Пример: эволюция архитектуры через TDD

```python
# Начальная версия - монолитный подход
class OrderService:
    def process_order(self, order_data):
        # Валидация
        if not order_data.get('customer_id'):
            return False
        
        # Проверка inventory
        db = MySQLDatabase()
        inventory = db.get_inventory(order_data['product_id'])
        if inventory < order_data['quantity']:
            return False
        
        # Обработка платежа
        payment_gateway = PayPalGateway()
        payment_result = payment_gateway.charge(order_data['amount'])
        if not payment_result.success:
            return False
        
        # Отправка email
        smtp = SMTPService()
        smtp.send_email(order_data['customer_email'], "Order confirmation")
        
        return True

# После применения TDD - разделенная архитектура
class OrderService:
    def __init__(self, 
                 validator: OrderValidator,
                 inventory_checker: InventoryChecker,
                 payment_processor: PaymentProcessor,
                 notification_service: NotificationService):
        self.validator = validator
        self.inventory_checker = inventory_checker
        self.payment_processor = payment_processor
        self.notification_service = notification_service
    
    def process_order(self, order_data: OrderData) -> OrderResult:
        # Каждый шаг тестируется отдельно
        validation_result = self.validator.validate(order_data)
        if not validation_result.is_valid:
            return OrderResult.failure(validation_result.errors)
        
        if not self.inventory_checker.is_available(order_data.product_id, order_data.quantity):
            return OrderResult.failure(["Product not available"])
        
        payment_result = self.payment_processor.process(order_data.payment_info)
        if not payment_result.is_successful:
            return OrderResult.failure(["Payment failed"])
        
        self.notification_service.send_confirmation(order_data.customer_email)
        
        return OrderResult.success(payment_result.transaction_id)
```

## 🎭 SOLID принципы в TDD

### Single Responsibility Principle (SRP)

TDD естественно ведет к SRP, так как легче тестировать классы с одной ответственностью.

```python
# Нарушение SRP - сложно тестировать
class UserManager:
    def create_user(self, user_data):
        # Валидация
        if not self._validate_email(user_data['email']):
            raise ValueError("Invalid email")
        
        # Сохранение в БД
        self._save_to_database(user_data)
        
        # Отправка email
        self._send_welcome_email(user_data['email'])
        
        # Логирование
        self._log_user_creation(user_data)

# Следование SRP - каждый класс легко тестировать
class EmailValidator:
    def validate(self, email: str) -> bool:
        return "@" in email and "." in email.split("@")[1]

class UserRepository:
    def save(self, user: User) -> User:
        # Сохранение в БД
        pass

class WelcomeEmailService:
    def send_welcome_email(self, email: str) -> None:
        # Отправка приветственного email
        pass

class UserCreationLogger:
    def log_creation(self, user: User) -> None:
        # Логирование создания пользователя
        pass

class UserService:
    def __init__(self, 
                 validator: EmailValidator,
                 repository: UserRepository,
                 email_service: WelcomeEmailService,
                 logger: UserCreationLogger):
        self.validator = validator
        self.repository = repository
        self.email_service = email_service
        self.logger = logger
    
    def create_user(self, user_data: dict) -> User:
        if not self.validator.validate(user_data['email']):
            raise ValueError("Invalid email")
        
        user = User.from_dict(user_data)
        saved_user = self.repository.save(user)
        
        self.email_service.send_welcome_email(saved_user.email)
        self.logger.log_creation(saved_user)
        
        return saved_user

# Тестирование становится простым
def test_user_service_create_user():
    # Мокируем все зависимости
    mock_validator = Mock()
    mock_validator.validate.return_value = True
    
    mock_repository = Mock()
    mock_repository.save.return_value = User(id=1, email="test@example.com")
    
    mock_email_service = Mock()
    mock_logger = Mock()
    
    service = UserService(mock_validator, mock_repository, mock_email_service, mock_logger)
    
    user_data = {"email": "test@example.com", "name": "Test User"}
    result = service.create_user(user_data)
    
    assert result.email == "test@example.com"
    mock_validator.validate.assert_called_once_with("test@example.com")
    mock_repository.save.assert_called_once()
    mock_email_service.send_welcome_email.assert_called_once()
    mock_logger.log_creation.assert_called_once()
```

### Open/Closed Principle (OCP)

TDD способствует расширяемости через абстракции.

```python
from abc import ABC, abstractmethod

# Абстракция для уведомлений
class NotificationSender(ABC):
    @abstractmethod
    def send(self, recipient: str, message: str) -> bool:
        pass

# Конкретные реализации
class EmailNotificationSender(NotificationSender):
    def send(self, recipient: str, message: str) -> bool:
        # Отправка email
        return True

class SMSNotificationSender(NotificationSender):
    def send(self, recipient: str, message: str) -> bool:
        # Отправка SMS
        return True

class PushNotificationSender(NotificationSender):
    def send(self, recipient: str, message: str) -> bool:
        # Отправка push уведомления
        return True

# Сервис, закрытый для модификации, но открытый для расширения
class NotificationService:
    def __init__(self, senders: list[NotificationSender]):
        self.senders = senders
    
    def send_notification(self, recipient: str, message: str) -> list[bool]:
        results = []
        for sender in self.senders:
            try:
                result = sender.send(recipient, message)
                results.append(result)
            except Exception:
                results.append(False)
        return results

# Тестирование нового типа уведомлений без изменения кода
class SlackNotificationSender(NotificationSender):
    def send(self, recipient: str, message: str) -> bool:
        # Отправка в Slack
        return True

def test_notification_service_with_multiple_senders():
    email_sender = Mock()
    email_sender.send.return_value = True
    
    sms_sender = Mock()
    sms_sender.send.return_value = True
    
    slack_sender = Mock()
    slack_sender.send.return_value = True
    
    service = NotificationService([email_sender, sms_sender, slack_sender])
    results = service.send_notification("user@example.com", "Hello")
    
    assert results == [True, True, True]
    assert email_sender.send.call_count == 1
    assert sms_sender.send.call_count == 1
    assert slack_sender.send.call_count == 1
```

### Dependency Inversion Principle (DIP)

TDD требует инверсии зависимостей для тестируемости.

```python
# Высокоуровневые модули не должны зависеть от низкоуровневых
# Нарушение DIP
class OrderProcessor:
    def __init__(self):
        self.mysql_db = MySQLDatabase()  # Зависимость от конкретной реализации
        self.paypal = PayPalGateway()    # Зависимость от конкретной реализации
    
    def process(self, order):
        # Сложно тестировать из-за жестких зависимостей
        pass

# Следование DIP
class OrderRepository(ABC):
    @abstractmethod
    def save_order(self, order: Order) -> int:
        pass

class PaymentGateway(ABC):
    @abstractmethod
    def process_payment(self, amount: float, payment_info: dict) -> PaymentResult:
        pass

class OrderProcessor:
    def __init__(self, 
                 order_repository: OrderRepository,
                 payment_gateway: PaymentGateway):
        self.order_repository = order_repository
        self.payment_gateway = payment_gateway
    
    def process(self, order: Order) -> ProcessingResult:
        payment_result = self.payment_gateway.process_payment(
            order.total_amount, 
            order.payment_info
        )
        
        if payment_result.is_successful:
            order_id = self.order_repository.save_order(order)
            return ProcessingResult.success(order_id)
        
        return ProcessingResult.failure(payment_result.error_message)

# Конкретные реализации
class MySQLOrderRepository(OrderRepository):
    def save_order(self, order: Order) -> int:
        # Сохранение в MySQL
        pass

class PayPalGateway(PaymentGateway):
    def process_payment(self, amount: float, payment_info: dict) -> PaymentResult:
        # Обработка через PayPal
        pass

# Легкое тестирование благодаря DIP
def test_order_processor():
    mock_repository = Mock()
    mock_repository.save_order.return_value = 123
    
    mock_gateway = Mock()
    mock_gateway.process_payment.return_value = PaymentResult.success("txn_456")
    
    processor = OrderProcessor(mock_repository, mock_gateway)
    order = Order(total_amount=100.0, payment_info={"card": "1234"})
    
    result = processor.process(order)
    
    assert result.is_successful
    assert result.order_id == 123
```

## 🏛️ Архитектурные паттерны для TDD

### 1. Hexagonal Architecture (Ports & Adapters)

```python
# Domain Layer - центр архитектуры
class User:
    def __init__(self, email: str, name: str):
        self.email = email
        self.name = name
        self.is_active = True
    
    def deactivate(self):
        self.is_active = False
    
    def change_email(self, new_email: str):
        if "@" not in new_email:
            raise ValueError("Invalid email format")
        self.email = new_email

# Ports - интерфейсы
class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> User:
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass

class EmailService(ABC):
    @abstractmethod
    def send_confirmation(self, email: str, token: str) -> bool:
        pass

# Application Layer - use cases
class UserRegistrationUseCase:
    def __init__(self, 
                 user_repository: UserRepository,
                 email_service: EmailService):
        self.user_repository = user_repository
        self.email_service = email_service
    
    def register_user(self, email: str, name: str) -> User:
        # Проверяем существующего пользователя
        existing_user = self.user_repository.find_by_email(email)
        if existing_user:
            raise ValueError("User already exists")
        
        # Создаем нового пользователя
        user = User(email, name)
        saved_user = self.user_repository.save(user)
        
        # Отправляем подтверждение
        confirmation_token = "abc123"  # В реальности генерируется
        self.email_service.send_confirmation(email, confirmation_token)
        
        return saved_user

# Adapters - внешние реализации
class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session):
        self.session = session
    
    def save(self, user: User) -> User:
        # Сохранение через SQLAlchemy
        pass
    
    def find_by_email(self, email: str) -> Optional[User]:
        # Поиск через SQLAlchemy
        pass

class SMTPEmailService(EmailService):
    def send_confirmation(self, email: str, token: str) -> bool:
        # Отправка через SMTP
        pass

# Web Adapter (FastAPI)
from fastapi import FastAPI, Depends

app = FastAPI()

def get_user_registration_use_case() -> UserRegistrationUseCase:
    # Dependency injection
    session = get_db_session()
    user_repository = SQLAlchemyUserRepository(session)
    email_service = SMTPEmailService()
    return UserRegistrationUseCase(user_repository, email_service)

@app.post("/users/register")
async def register_user(
    user_data: UserRegistrationRequest,
    use_case: UserRegistrationUseCase = Depends(get_user_registration_use_case)
):
    try:
        user = use_case.register_user(user_data.email, user_data.name)
        return {"success": True, "user_id": user.id}
    except ValueError as e:
        return {"success": False, "error": str(e)}

# Тестирование use case изолированно
def test_user_registration_use_case():
    mock_repository = Mock()
    mock_repository.find_by_email.return_value = None
    mock_repository.save.return_value = User("test@example.com", "Test User")
    
    mock_email_service = Mock()
    mock_email_service.send_confirmation.return_value = True
    
    use_case = UserRegistrationUseCase(mock_repository, mock_email_service)
    
    user = use_case.register_user("test@example.com", "Test User")
    
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    mock_repository.save.assert_called_once()
    mock_email_service.send_confirmation.assert_called_once()
```

### 2. Clean Architecture

```python
# Entities - центр архитектуры
class Order:
    def __init__(self, customer_id: int, items: list):
        self.customer_id = customer_id
        self.items = items
        self.status = "pending"
        self.total = self._calculate_total()
    
    def _calculate_total(self) -> float:
        return sum(item.price * item.quantity for item in self.items)
    
    def confirm(self):
        if not self.items:
            raise ValueError("Cannot confirm empty order")
        self.status = "confirmed"
    
    def cancel(self):
        if self.status == "shipped":
            raise ValueError("Cannot cancel shipped order")
        self.status = "cancelled"

# Use Cases
class ConfirmOrderUseCase:
    def __init__(self, 
                 order_repository: OrderRepository,
                 inventory_service: InventoryService,
                 notification_service: NotificationService):
        self.order_repository = order_repository
        self.inventory_service = inventory_service
        self.notification_service = notification_service
    
    def execute(self, order_id: int) -> ConfirmOrderResult:
        order = self.order_repository.find_by_id(order_id)
        if not order:
            return ConfirmOrderResult.failure("Order not found")
        
        # Проверяем наличие товаров
        for item in order.items:
            if not self.inventory_service.is_available(item.product_id, item.quantity):
                return ConfirmOrderResult.failure(f"Product {item.product_id} not available")
        
        # Подтверждаем заказ
        order.confirm()
        self.order_repository.save(order)
        
        # Уведомляем клиента
        self.notification_service.send_order_confirmation(order.customer_id, order.id)
        
        return ConfirmOrderResult.success(order.id)

# Interface Adapters
class OrderController:
    def __init__(self, confirm_order_use_case: ConfirmOrderUseCase):
        self.confirm_order_use_case = confirm_order_use_case
    
    def confirm_order(self, order_id: int) -> dict:
        result = self.confirm_order_use_case.execute(order_id)
        
        if result.is_successful:
            return {
                "status": "success",
                "order_id": result.order_id,
                "message": "Order confirmed successfully"
            }
        else:
            return {
                "status": "error",
                "message": result.error_message
            }

# Frameworks & Drivers
class FlaskOrderController(OrderController):
    def setup_routes(self, app):
        @app.route('/orders/<int:order_id>/confirm', methods=['POST'])
        def confirm_order_endpoint(order_id):
            return self.confirm_order(order_id)

# Тестирование по слоям
def test_order_entity():
    """Тест entity изолированно."""
    items = [Item(product_id=1, quantity=2, price=10.0)]
    order = Order(customer_id=123, items=items)
    
    assert order.total == 20.0
    assert order.status == "pending"
    
    order.confirm()
    assert order.status == "confirmed"

def test_confirm_order_use_case():
    """Тест use case с мокированными зависимостями."""
    mock_repository = Mock()
    mock_inventory = Mock()
    mock_notification = Mock()
    
    # Настраиваем моки
    order = Order(customer_id=123, items=[Item(product_id=1, quantity=1, price=10.0)])
    mock_repository.find_by_id.return_value = order
    mock_inventory.is_available.return_value = True
    
    use_case = ConfirmOrderUseCase(mock_repository, mock_inventory, mock_notification)
    result = use_case.execute(1)
    
    assert result.is_successful
    assert order.status == "confirmed"
    mock_repository.save.assert_called_once_with(order)
    mock_notification.send_order_confirmation.assert_called_once()

def test_order_controller():
    """Тест controller с мокированным use case."""
    mock_use_case = Mock()
    mock_use_case.execute.return_value = ConfirmOrderResult.success(1)
    
    controller = OrderController(mock_use_case)
    response = controller.confirm_order(1)
    
    assert response["status"] == "success"
    assert response["order_id"] == 1
    mock_use_case.execute.assert_called_once_with(1)
```

### 3. CQRS (Command Query Responsibility Segregation)

```python
# Commands - изменяют состояние
class CreateUserCommand:
    def __init__(self, email: str, name: str):
        self.email = email
        self.name = name

class UpdateUserEmailCommand:
    def __init__(self, user_id: int, new_email: str):
        self.user_id = user_id
        self.new_email = new_email

# Queries - читают состояние
class GetUserByIdQuery:
    def __init__(self, user_id: int):
        self.user_id = user_id

class GetUsersByEmailQuery:
    def __init__(self, email_pattern: str):
        self.email_pattern = email_pattern

# Command Handlers
class CreateUserCommandHandler:
    def __init__(self, 
                 user_repository: UserRepository,
                 email_service: EmailService):
        self.user_repository = user_repository
        self.email_service = email_service
    
    def handle(self, command: CreateUserCommand) -> int:
        # Проверяем существующего пользователя
        existing = self.user_repository.find_by_email(command.email)
        if existing:
            raise ValueError("User already exists")
        
        # Создаем пользователя
        user = User(command.email, command.name)
        saved_user = self.user_repository.save(user)
        
        # Отправляем welcome email
        self.email_service.send_welcome_email(saved_user.email)
        
        return saved_user.id

# Query Handlers
class GetUserByIdQueryHandler:
    def __init__(self, user_read_repository: UserReadRepository):
        self.user_read_repository = user_read_repository
    
    def handle(self, query: GetUserByIdQuery) -> Optional[UserDto]:
        return self.user_read_repository.find_by_id(query.user_id)

# Command/Query Bus
class CommandBus:
    def __init__(self):
        self.handlers = {}
    
    def register_handler(self, command_type: type, handler):
        self.handlers[command_type] = handler
    
    def execute(self, command):
        handler = self.handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler for {type(command)}")
        return handler.handle(command)

class QueryBus:
    def __init__(self):
        self.handlers = {}
    
    def register_handler(self, query_type: type, handler):
        self.handlers[query_type] = handler
    
    def execute(self, query):
        handler = self.handlers.get(type(query))
        if not handler:
            raise ValueError(f"No handler for {type(query)}")
        return handler.handle(query)

# Тестирование CQRS
def test_create_user_command_handler():
    mock_repository = Mock()
    mock_repository.find_by_email.return_value = None
    mock_repository.save.return_value = User("test@example.com", "Test User")
    mock_repository.save.return_value.id = 123
    
    mock_email_service = Mock()
    
    handler = CreateUserCommandHandler(mock_repository, mock_email_service)
    command = CreateUserCommand("test@example.com", "Test User")
    
    user_id = handler.handle(command)
    
    assert user_id == 123
    mock_repository.save.assert_called_once()
    mock_email_service.send_welcome_email.assert_called_once_with("test@example.com")

def test_command_bus():
    mock_handler = Mock()
    mock_handler.handle.return_value = 123
    
    command_bus = CommandBus()
    command_bus.register_handler(CreateUserCommand, mock_handler)
    
    command = CreateUserCommand("test@example.com", "Test User")
    result = command_bus.execute(command)
    
    assert result == 123
    mock_handler.handle.assert_called_once_with(command)
```

## 🛠️ Dependency Injection в TDD

### 1. Ручная DI

```python
class ServiceContainer:
    def __init__(self):
        self._services = {}
        self._singletons = {}
    
    def register_transient(self, interface: type, implementation: type):
        self._services[interface] = implementation
    
    def register_singleton(self, interface: type, implementation: type):
        self._services[interface] = implementation
        self._singletons[interface] = None
    
    def get(self, interface: type):
        if interface in self._singletons:
            if self._singletons[interface] is None:
                self._singletons[interface] = self._create_instance(interface)
            return self._singletons[interface]
        
        return self._create_instance(interface)
    
    def _create_instance(self, interface: type):
        implementation = self._services[interface]
        # Простая реализация без автоматического разрешения зависимостей
        return implementation()

# Использование
def setup_container() -> ServiceContainer:
    container = ServiceContainer()
    
    container.register_singleton(UserRepository, SQLAlchemyUserRepository)
    container.register_transient(EmailService, SMTPEmailService)
    container.register_transient(UserService, UserService)
    
    return container

def test_service_container():
    container = ServiceContainer()
    container.register_transient(EmailService, SMTPEmailService)
    
    service1 = container.get(EmailService)
    service2 = container.get(EmailService)
    
    assert isinstance(service1, SMTPEmailService)
    assert service1 is not service2  # Transient services
```

### 2. Dependency Injector Library

```bash
# Установка dependency-injector
uv add dependency-injector
```

```python
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

# Container конфигурация
class ApplicationContainer(containers.DeclarativeContainer):
    # Конфигурация
    config = providers.Configuration()
    
    # Database
    database = providers.Singleton(
        Database,
        host=config.database.host,
        port=config.database.port,
    )
    
    # Repositories
    user_repository = providers.Factory(
        SQLAlchemyUserRepository,
        session=database.provided.session,
    )
    
    # Services
    email_service = providers.Factory(
        SMTPEmailService,
        host=config.email.smtp_host,
        port=config.email.smtp_port,
    )
    
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
        email_service=email_service,
    )

# FastAPI с DI
@app.post("/users")
@inject
async def create_user(
    user_data: UserCreateRequest,
    user_service: UserService = Provide[ApplicationContainer.user_service]
):
    user = await user_service.create_user(user_data.email, user_data.name)
    return {"user_id": user.id}

# Тестирование с override
def test_user_creation_with_di():
    container = ApplicationContainer()
    
    # Override для тестов
    mock_repository = Mock()
    mock_repository.save.return_value = User("test@example.com", "Test User")
    
    mock_email_service = Mock()
    
    with container.user_repository.override(mock_repository), \
         container.email_service.override(mock_email_service):
        
        user_service = container.user_service()
        user = user_service.create_user("test@example.com", "Test User")
        
        assert user.email == "test@example.com"
        mock_repository.save.assert_called_once()
```

## 🧪 Архитектурные тесты

### 1. Тестирование зависимостей

```python
import ast
import os
from pathlib import Path

def test_domain_has_no_infrastructure_dependencies():
    """Проверяет, что домен не зависит от инфраструктуры."""
    domain_path = Path("src/domain")
    
    for python_file in domain_path.glob("**/*.py"):
        with open(python_file, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                continue
        
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
    """Проверяет отсутствие циклических зависимостей."""
    import_graph = {}
    
    def extract_imports(file_path):
        imports = set()
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                return imports
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module.startswith('src.'):
                    imports.add(node.module)
        
        return imports
    
    # Строим граф зависимостей
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                module_name = file_path.replace('/', '.').replace('\\', '.').replace('.py', '')
                imports = extract_imports(file_path)
                import_graph[module_name] = imports
    
    # Проверяем циклы (упрощенная проверка)
    def has_cycle(graph, start, visited, rec_stack):
        visited.add(start)
        rec_stack.add(start)
        
        for neighbor in graph.get(start, []):
            if neighbor in graph:
                if neighbor not in visited:
                    if has_cycle(graph, neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True
        
        rec_stack.remove(start)
        return False
    
    visited = set()
    for module in import_graph:
        if module not in visited:
            if has_cycle(import_graph, module, visited, set()):
                pytest.fail(f"Circular dependency detected involving {module}")
```

### 2. Тестирование архитектурных паттернов

```python
def test_controllers_only_depend_on_use_cases():
    """Проверяет, что контроллеры зависят только от use cases."""
    controllers_path = Path("src/controllers")
    
    for controller_file in controllers_path.glob("**/*.py"):
        with open(controller_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем, что нет прямых импортов репозиториев
        assert 'from src.infrastructure' not in content, \
            f"Controller {controller_file} directly imports infrastructure"
        
        assert 'from src.domain.repositories' not in content, \
            f"Controller {controller_file} directly imports repositories"

def test_use_cases_follow_single_responsibility():
    """Проверяет, что use cases следуют принципу единственной ответственности."""
    use_cases_path = Path("src/use_cases")
    
    for use_case_file in use_cases_path.glob("**/*.py"):
        with open(use_case_file, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        class_count = 0
        method_count = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_count += 1
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and not item.name.startswith('_'):
                        method_count += 1
        
        # Каждый use case должен иметь только один публичный метод
        if class_count > 0:
            assert method_count <= class_count, \
                f"Use case {use_case_file} has too many public methods (SRP violation)"

def test_entities_have_no_infrastructure_dependencies():
    """Проверяет, что entity не зависят от инфраструктуры."""
    entities_path = Path("src/domain/entities")
    
    forbidden_imports = [
        'sqlalchemy',
        'django',
        'flask',
        'fastapi',
        'requests',
        'aiohttp'
    ]
    
    for entity_file in entities_path.glob("**/*.py"):
        with open(entity_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for forbidden in forbidden_imports:
            assert forbidden not in content, \
                f"Entity {entity_file} has infrastructure dependency: {forbidden}"
```

## 🎯 Проектирование с учетом тестируемости

### Design for Testability Principles

1. **Избегайте статических зависимостей**
2. **Используйте dependency injection**
3. **Создавайте маленькие, сфокусированные классы**
4. **Предпочитайте композицию наследованию**
5. **Делайте побочные эффекты явными**

```python
# Плохо - сложно тестировать
class OrderService:
    def process_order(self, order_data):
        # Статические зависимости
        db = Database.get_instance()
        email = EmailSender()
        logger = Logger.get_logger(__name__)
        
        # Скрытые побочные эффекты
        current_time = datetime.now()
        
        # Множественная ответственность
        if self._validate_order(order_data):
            order_id = db.save_order(order_data)
            email.send_confirmation(order_data['email'])
            logger.info(f"Order {order_id} processed at {current_time}")
            return order_id
        
        return None

# Хорошо - легко тестировать
class OrderValidator:
    def validate(self, order_data: dict) -> ValidationResult:
        errors = []
        if not order_data.get('customer_email'):
            errors.append("Email is required")
        if not order_data.get('items'):
            errors.append("Items are required")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

class OrderService:
    def __init__(self, 
                 validator: OrderValidator,
                 repository: OrderRepository,
                 email_service: EmailService,
                 logger: Logger,
                 time_provider: TimeProvider):
        self.validator = validator
        self.repository = repository
        self.email_service = email_service
        self.logger = logger
        self.time_provider = time_provider
    
    def process_order(self, order_data: dict) -> ProcessOrderResult:
        # Явная валидация
        validation = self.validator.validate(order_data)
        if not validation.is_valid:
            return ProcessOrderResult.failure(validation.errors)
        
        # Явные операции
        order = Order.from_dict(order_data)
        order.processed_at = self.time_provider.now()
        
        saved_order = self.repository.save(order)
        
        self.email_service.send_confirmation(order.customer_email, saved_order.id)
        self.logger.info(f"Order {saved_order.id} processed at {order.processed_at}")
        
        return ProcessOrderResult.success(saved_order.id)

# Легкое тестирование
def test_order_service_successful_processing():
    # Arrange
    mock_validator = Mock()
    mock_validator.validate.return_value = ValidationResult(is_valid=True, errors=[])
    
    mock_repository = Mock()
    mock_repository.save.return_value = Order(id=123, customer_email="test@example.com")
    
    mock_email_service = Mock()
    mock_logger = Mock()
    
    mock_time_provider = Mock()
    mock_time_provider.now.return_value = datetime(2024, 8, 26, 12, 0, 0)
    
    service = OrderService(
        mock_validator, 
        mock_repository, 
        mock_email_service, 
        mock_logger,
        mock_time_provider
    )
    
    order_data = {"customer_email": "test@example.com", "items": [{"id": 1}]}
    
    # Act
    result = service.process_order(order_data)
    
    # Assert
    assert result.is_successful
    assert result.order_id == 123
    
    mock_validator.validate.assert_called_once_with(order_data)
    mock_repository.save.assert_called_once()
    mock_email_service.send_confirmation.assert_called_once_with("test@example.com", 123)
    mock_logger.info.assert_called_once()
```

## 🏆 Лучшие практики

### ✅ Архитектурные принципы TDD

1. **Dependency Inversion** — зависьте от абстракций
2. **Single Responsibility** — один класс = одна причина для изменения
3. **Interface Segregation** — много маленьких интерфейсов
4. **Composition over Inheritance** — предпочитайте композицию
5. **Explicit Dependencies** — делайте зависимости явными
6. **Pure Functions** — избегайте побочных эффектов где возможно

### ❌ Антипаттерны

1. **God Object** — классы, делающие слишком много
2. **Tight Coupling** — жесткие связи между компонентами
3. **Hidden Dependencies** — скрытые зависимости от глобального состояния
4. **Mixed Concerns** — смешение бизнес-логики с техническими деталями
5. **Testing Implementation Details** — тестирование приватных методов

## 🔮 Заключение

TDD не просто улучшает качество тестов — он формирует архитектуру, которая:

- **Легко изменяется** при новых требованиях
- **Хорошо тестируется** на всех уровнях
- **Понятна** новым членам команды
- **Масштабируется** с ростом проекта
- **Поддерживается** в долгосрочной перспективе

Следуя принципам TDD и применяя правильные архитектурные паттерны, вы создаете систему, которая будет радовать и разработчиков, и пользователей на протяжении многих лет.

## 🧪 Проверьте свои знания

<div class="quiz-container" id="tdd-architecture-quiz">
<script type="application/json">
{
  "title": "TDD и архитектура приложения",
  "description": "Проверьте понимание влияния TDD на архитектурные решения и паттерны",
  "icon": "🏗️",
  "questions": [
    {
      "question": "Как TDD влияет на архитектуру приложения?",
      "type": "multiple",
      "options": [
        {"text": "Способствует слабой связанности компонентов", "correct": true},
        {"text": "Увеличивает coupling между модулями", "correct": false},
        {"text": "Снижает тестируемость системы", "correct": false},
        {"text": "Повышает гибкость к изменениям", "correct": true},
        {"text": "Усложняет добавление новых функций", "correct": false}
      ],
      "explanation": "TDD естественным образом ведет к слабой связанности и высокой гибкости, так как требует Dependency Injection и абстракций.",
      "points": 2
    },
    {
      "question": "Что означает принцип Single Responsibility Principle (SRP)?",
      "type": "single",
      "options": [
        {"text": "Класс должен иметь только одну причину для изменения", "correct": true},
        {"text": "Класс должен наследоваться только от одного базового класса", "correct": false},
        {"text": "Класс должен иметь только один метод", "correct": false},
        {"text": "Класс должен быть ответственен за все операции с данными", "correct": false}
      ],
      "explanation": "SRP означает, что каждый класс должен иметь только одну ответственность и одну причину для изменения.",
      "points": 1
    },
    {
      "question": "Что такое Dependency Inversion Principle (DIP)?",
      "type": "single",
      "options": [
        {"text": "Высокоуровневые модули не должны зависеть от низкоуровневых", "correct": true},
        {"text": "Зависимости должны быть жестко связаны", "correct": false},
        {"text": "Все модули должны зависеть от конкретных реализаций", "correct": false},
        {"text": "Низкоуровневые модули должны управлять высокоуровневыми", "correct": false}
      ],
      "explanation": "DIP требует, чтобы модули зависели от абстракций, а не от конкретных реализаций, что обеспечивает тестируемость.",
      "points": 1
    },
    {
      "question": "Какие архитектурные паттерны хорошо сочетаются с TDD? (выберите все правильные)",
      "type": "multiple",
      "options": [
        {"text": "Hexagonal Architecture (Ports & Adapters)", "correct": true},
        {"text": "CQRS (Command Query Responsibility Segregation)", "correct": true},
        {"text": "Big Ball of Mud", "correct": false},
        {"text": "Event Sourcing", "correct": true},
        {"text": "God Object Pattern", "correct": false}
      ],
      "explanation": "Hexagonal Architecture, CQRS и Event Sourcing способствуют разделению ответственностей и тестируемости, в отличие от антипаттернов.",
      "points": 2
    },
    {
      "question": "Что такое Ports & Adapters в Hexagonal Architecture?",
      "type": "single",
      "options": [
        {"text": "Ports - интерфейсы, Adapters - реализации для внешних систем", "correct": true},
        {"text": "Ports - физические разъемы, Adapters - переходники", "correct": false},
        {"text": "Ports - сетевое взаимодействие, Adapters - адаптеры сети", "correct": false},
        {"text": "Ports - порты сервера, Adapters - сетевые адаптеры", "correct": false}
      ],
      "explanation": "В Hexagonal Architecture Ports определяют интерфейсы для взаимодействия с внешним миром, а Adapters предоставляют конкретные реализации.",
      "points": 1
    },
    {
      "question": "Какой антипаттерн НЕ способствует TDD?",
      "type": "single",
      "options": [
        {"text": "God Object - класс, делающий слишком много", "correct": true},
        {"text": "Dependency Injection", "correct": false},
        {"text": "Interface Segregation", "correct": false},
        {"text": "Single Responsibility", "correct": false}
      ],
      "explanation": "God Object (класс, делающий слишком много) усложняет тестирование и противоречит принципам TDD.",
      "points": 1
    }
  ]
}
</script>
</div>

---

**Предыдущая глава:** [Продвинутое мокирование](18_advanced_mocking.md)
**Следующая глава:** [Заключение и ресурсы](20_conclusion.md)

*🏗️ Помните: хорошая архитектура — это не случайность, это результат осознанного проектирования через тесты!*
