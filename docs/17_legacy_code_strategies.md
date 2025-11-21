# Стратегии работы с Legacy Code в TDD

## 🎯 Введение

Работа с унаследованным кодом (Legacy Code) — одна из самых сложных задач в разработке. Большинство разработчиков сталкиваются с ситуацией, когда нужно изменять или расширять существующий код без тестов. В этой главе мы изучим проверенные стратегии применения TDD к Legacy системам.

## 🤔 Что такое Legacy Code?

### Определение по Michael Feathers

> **Legacy Code** — это код без тестов. Без тестов мы не знаем, правильно ли работает код после изменений.

### Характеристики Legacy Code

```python
# Типичный пример Legacy кода
class OrderProcessor:
    def __init__(self):
        self.db = MySQLConnection("localhost", "orders_db")  # Жесткая зависимость
        self.email_service = SMTPService("smtp.company.com")  # Жесткая зависимость
        self.logger = FileLogger("/var/log/orders.log")      # Жесткая зависимость
    
    def process_order(self, order_data):
        # 200+ строк спагетти-кода
        if not order_data:
            return False
        
        # Валидация смешана с бизнес-логикой
        if "customer_id" not in order_data or order_data["customer_id"] < 1:
            self.logger.error("Invalid customer ID")
            return False
        
        # Прямые обращения к БД
        customer = self.db.execute("SELECT * FROM customers WHERE id = %s", 
                                  order_data["customer_id"]).fetchone()
        if not customer:
            return False
        
        # Сложная логика без тестов
        total = 0
        for item in order_data["items"]:
            price = self.db.execute("SELECT price FROM products WHERE id = %s", 
                                   item["product_id"]).fetchone()
            if price:
                total += price[0] * item["quantity"]
        
        # Побочные эффекты
        order_id = self.db.execute("INSERT INTO orders ...", ...)
        self.email_service.send_confirmation(customer["email"], order_id)
        self.logger.info(f"Order {order_id} processed")
        
        return order_id

# Проблемы этого кода:
# 1. Невозможно тестировать (жесткие зависимости)
# 2. Нарушение Single Responsibility Principle
# 3. Тесная связанность (tight coupling)
# 4. Нет инверсии зависимостей
# 5. Сложно изменять и расширять
```

### Проблемы Legacy систем

1. **Отсутствие тестов** — невозможно безопасно изменять
2. **Тесная связанность** — изменение одного компонента ломает другие
3. **Неясная архитектура** — сложно понять как работает система
4. **Большие классы и методы** — трудно понять и тестировать
5. **Глобальное состояние** — непредсказуемое поведение
6. **Устаревшие технологии** — сложно поддерживать

## 🔧 Seams — точки внедрения для тестирования

### Концепция Seam

**Seam** — место в коде, где можно изменить поведение программы не редактируя код в этом месте.

### Типы Seams в Python

#### 1. Object Seam (Полиморфизм)

```python
# Legacy код с жесткой зависимостью
class EmailNotifier:
    def __init__(self):
        self.smtp = SMTPService("smtp.company.com")  # Жесткая зависимость
    
    def notify(self, email, message):
        return self.smtp.send(email, message)

# Создание Seam через полиморфизм
class EmailNotifier:
    def __init__(self, email_service=None):
        self.email_service = email_service or SMTPService("smtp.company.com")
    
    def notify(self, email, message):
        return self.email_service.send(email, message)

# Теперь можно тестировать
def test_email_notification():
    mock_service = Mock()
    mock_service.send.return_value = True
    
    notifier = EmailNotifier(email_service=mock_service)
    result = notifier.notify("test@example.com", "Hello")
    
    assert result is True
    mock_service.send.assert_called_once_with("test@example.com", "Hello")
```

#### 2. Parameter Seam

```python
# Legacy код с глобальными зависимостями
import datetime

def calculate_age(birth_date):
    today = datetime.date.today()  # Глобальная зависимость
    return today.year - birth_date.year

# Создание Parameter Seam
def calculate_age(birth_date, current_date=None):
    if current_date is None:
        current_date = datetime.date.today()
    return current_date.year - birth_date.year

# Тестирование с контролируемой датой
def test_calculate_age():
    birth_date = datetime.date(1990, 5, 15)
    current_date = datetime.date(2024, 8, 26)
    
    age = calculate_age(birth_date, current_date)
    assert age == 34
```

#### 3. Monkey Patching Seam

```python
# Legacy код, который сложно изменить
def process_payment(amount):
    response = requests.post("https://payment.api/charge", 
                           json={"amount": amount})
    return response.json()

# Тестирование через monkey patching
def test_process_payment(mocker):
    mock_response = Mock()
    mock_response.json.return_value = {"status": "success", "id": "123"}
    
    mocker.patch('requests.post', return_value=mock_response)
    
    result = process_payment(100)
    
    assert result["status"] == "success"
    assert result["id"] == "123"
```

## 📝 Characterization Tests

### Что такое Characterization Tests?

Тесты, которые фиксируют **текущее поведение** Legacy кода, даже если это поведение неправильное.

### Процесс создания

1. **Запустите код** с известными входными данными
2. **Зафиксируйте выходные данные** в тесте
3. **Запустите тест** — он должен проходить
4. **Начинайте рефакторинг** под защитой теста

### Практический пример

```python
# Legacy функция с неочевидным поведением
def calculate_shipping_cost(weight, distance, is_express=False):
    """Legacy функция расчета стоимости доставки."""
    base_cost = weight * 0.5
    
    if distance > 100:
        base_cost += distance * 0.1
    elif distance > 50:
        base_cost += distance * 0.05
    
    if is_express:
        base_cost *= 1.5
    
    # Странная логика, но так работает система
    if weight > 10 and distance < 50:
        base_cost -= 2
    
    return round(base_cost, 2)

# Создаем Characterization Tests
class TestShippingCostCharacterization:
    """Тесты, фиксирующие текущее поведение."""
    
    def test_current_behavior_light_package_short_distance(self):
        # Фиксируем как работает сейчас
        result = calculate_shipping_cost(weight=5, distance=30)
        assert result == 2.5
    
    def test_current_behavior_heavy_package_short_distance(self):
        # Странное поведение, но фиксируем
        result = calculate_shipping_cost(weight=15, distance=30)
        assert result == 5.5  # 7.5 - 2 = 5.5 (странная скидка)
    
    def test_current_behavior_express_delivery(self):
        result = calculate_shipping_cost(weight=5, distance=30, is_express=True)
        assert result == 3.75  # 2.5 * 1.5
    
    def test_current_behavior_long_distance(self):
        result = calculate_shipping_cost(weight=5, distance=120)
        assert result == 14.5  # 2.5 + 12
    
    @pytest.mark.parametrize("weight,distance,express,expected", [
        (1, 10, False, 0.5),
        (20, 200, True, 45.0),
        (8, 75, False, 7.75),
        (12, 40, False, 4.0),  # Со скидкой
    ])
    def test_characterization_matrix(self, weight, distance, express, expected):
        """Матрица тестов для фиксации поведения."""
        result = calculate_shipping_cost(weight, distance, express)
        assert result == expected
```

### Создание Characterization Tests для сложных функций

```python
# Сложная Legacy функция
def complex_business_logic(data):
    """Сложная бизнес-логика с множественными путями выполнения."""
    result = {}
    
    # Анализируем функцию и создаем тесты
    pass

# Инструмент для генерации Characterization Tests
def generate_characterization_tests():
    """Генерация тестов на основе выполнения Legacy кода."""
    test_cases = []
    
    # Различные входные данные
    inputs = [
        {"id": 1, "amount": 100, "type": "standard"},
        {"id": 2, "amount": 0, "type": "premium"},
        {"id": 3, "amount": -50, "type": "standard"},
        {},  # Пустые данные
        None,  # None
    ]
    
    for i, input_data in enumerate(inputs):
        try:
            result = complex_business_logic(input_data)
            test_cases.append({
                "name": f"test_case_{i}",
                "input": input_data,
                "expected": result
            })
        except Exception as e:
            test_cases.append({
                "name": f"test_case_{i}_exception",
                "input": input_data,
                "exception": type(e).__name__,
                "message": str(e)
            })
    
    return test_cases

# Использование
test_cases = generate_characterization_tests()
for case in test_cases:
    print(f"def {case['name']}():")
    if 'exception' in case:
        print(f"    with pytest.raises({case['exception']}):")
        print(f"        complex_business_logic({case['input']})")
    else:
        print(f"    result = complex_business_logic({case['input']})")
        print(f"    assert result == {case['expected']}")
    print()
```

## 🔄 Техники изоляции Legacy кода

### 1. Extract and Override

```python
# Legacy класс с жесткими зависимостями
class OrderService:
    def process_order(self, order_data):
        # Жесткая зависимость
        email_sent = self._send_email(order_data["customer_email"])
        
        if email_sent:
            return self._save_to_database(order_data)
        return False
    
    def _send_email(self, email):
        # Сложная логика отправки email
        smtp = SMTPService("smtp.company.com")
        return smtp.send(email, "Order confirmation")
    
    def _save_to_database(self, order_data):
        # Сложная логика сохранения в БД
        db = DatabaseConnection()
        return db.save_order(order_data)

# Создаем тестируемый подкласс
class TestableOrderService(OrderService):
    def __init__(self):
        self.email_sent = True
        self.save_result = True
    
    def _send_email(self, email):
        return self.email_sent
    
    def _save_to_database(self, order_data):
        return self.save_result

# Тестируем через наследование
def test_order_processing():
    service = TestableOrderService()
    
    # Тест успешной обработки
    result = service.process_order({"customer_email": "test@example.com"})
    assert result is True
    
    # Тест неуспешной отправки email
    service.email_sent = False
    result = service.process_order({"customer_email": "test@example.com"})
    assert result is False
```

### 2. Wrap Legacy Code

```python
# Legacy код, который нельзя изменить
class LegacyPaymentProcessor:
    def process(self, card_number, amount, merchant_id):
        # 500 строк legacy кода
        # Возвращает странный формат данных
        return f"RESULT:{amount}:PROCESSED:{merchant_id}"

# Создаем обертку
class PaymentGateway:
    def __init__(self, processor=None):
        self.processor = processor or LegacyPaymentProcessor()
    
    def charge(self, card_number, amount, merchant_id):
        """Современный интерфейс для Legacy системы."""
        raw_result = self.processor.process(card_number, amount, merchant_id)
        
        # Парсим странный формат
        parts = raw_result.split(":")
        if len(parts) >= 3 and parts[2] == "PROCESSED":
            return {
                "success": True,
                "amount": float(parts[1]),
                "merchant_id": parts[3],
                "transaction_id": f"TXN_{parts[3]}_{parts[1]}"
            }
        
        return {"success": False, "error": "Payment failed"}

# Тестируем обертку
def test_payment_gateway():
    mock_processor = Mock()
    mock_processor.process.return_value = "RESULT:100.0:PROCESSED:MERCHANT123"
    
    gateway = PaymentGateway(processor=mock_processor)
    result = gateway.charge("1234567890123456", 100.0, "MERCHANT123")
    
    assert result["success"] is True
    assert result["amount"] == 100.0
    assert result["merchant_id"] == "MERCHANT123"
```

### 3. Strangler Fig Pattern

Постепенная замена Legacy кода новым.

```python
# Этап 1: Legacy система
class LegacyUserService:
    def get_user(self, user_id):
        # Old implementation
        return {"id": user_id, "name": "Legacy User"}
    
    def update_user(self, user_id, data):
        # Old implementation
        return True

# Этап 2: Роутер, который направляет к старой или новой реализации
class UserServiceRouter:
    def __init__(self):
        self.legacy_service = LegacyUserService()
        self.modern_service = ModernUserService()
        self.migration_flags = FeatureFlags()
    
    def get_user(self, user_id):
        if self.migration_flags.is_enabled("modern_user_service"):
            return self.modern_service.get_user(user_id)
        return self.legacy_service.get_user(user_id)
    
    def update_user(self, user_id, data):
        if self.migration_flags.is_enabled("modern_user_updates"):
            return self.modern_service.update_user(user_id, data)
        return self.legacy_service.update_user(user_id, data)

# Этап 3: Новая реализация
class ModernUserService:
    def __init__(self, repository):
        self.repository = repository
    
    def get_user(self, user_id):
        return self.repository.find_by_id(user_id)
    
    def update_user(self, user_id, data):
        user = self.repository.find_by_id(user_id)
        user.update(data)
        return self.repository.save(user)

# Тестирование миграции
def test_strangler_fig_migration():
    router = UserServiceRouter()
    
    # Тест Legacy режима
    router.migration_flags.disable("modern_user_service")
    user = router.get_user(123)
    assert user["name"] == "Legacy User"
    
    # Тест нового режима
    router.migration_flags.enable("modern_user_service")
    # Нужно замокать modern_service
    mock_modern = Mock()
    mock_modern.get_user.return_value = {"id": 123, "name": "Modern User"}
    router.modern_service = mock_modern
    
    user = router.get_user(123)
    assert user["name"] == "Modern User"
```

## 🛠 Постепенное внедрение TDD в Legacy

### Стратегия: Add TDD to New Features

```python
# Существующий Legacy класс
class LegacyOrderProcessor:
    # 1000 строк legacy кода
    pass

# Новая функциональность добавляется через TDD
class OrderValidationService:
    """Новый сервис, разработанный через TDD."""
    
    def validate_order(self, order_data):
        errors = []
        
        if not order_data:
            errors.append("Order data is required")
        
        if "customer_id" not in order_data:
            errors.append("Customer ID is required")
        
        if "items" not in order_data or not order_data["items"]:
            errors.append("Order must contain items")
        
        return {"valid": len(errors) == 0, "errors": errors}

# TDD тесты для нового функционала
class TestOrderValidation:
    def test_empty_order_data(self):
        validator = OrderValidationService()
        result = validator.validate_order(None)
        
        assert result["valid"] is False
        assert "Order data is required" in result["errors"]
    
    def test_missing_customer_id(self):
        validator = OrderValidationService()
        result = validator.validate_order({"items": ["item1"]})
        
        assert result["valid"] is False
        assert "Customer ID is required" in result["errors"]
    
    def test_valid_order(self):
        validator = OrderValidationService()
        order_data = {
            "customer_id": 123,
            "items": [{"id": 1, "quantity": 2}]
        }
        result = validator.validate_order(order_data)
        
        assert result["valid"] is True
        assert result["errors"] == []

# Интеграция с Legacy кодом
class ModernOrderProcessor:
    def __init__(self):
        self.legacy_processor = LegacyOrderProcessor()
        self.validator = OrderValidationService()
    
    def process_order(self, order_data):
        # Новая валидация через TDD
        validation = self.validator.validate_order(order_data)
        if not validation["valid"]:
            return {"success": False, "errors": validation["errors"]}
        
        # Делегирование Legacy коду
        return self.legacy_processor.process_order(order_data)
```

### Стратегия: Refactor Under Test

```python
# Legacy метод, который нужно рефакторить
class UserAccount:
    def calculate_monthly_fee(self, account_type, balance, transaction_count):
        # Сложная legacy логика
        fee = 0
        
        if account_type == "premium":
            fee = 10
        elif account_type == "standard":
            fee = 5
        else:
            fee = 0
        
        if balance < 1000:
            fee += 2
        
        if transaction_count > 10:
            fee += transaction_count * 0.1
        
        return fee

# Шаг 1: Создаем Characterization Tests
def test_monthly_fee_characterization():
    account = UserAccount()
    
    # Фиксируем текущее поведение
    assert account.calculate_monthly_fee("premium", 2000, 5) == 10.0
    assert account.calculate_monthly_fee("standard", 500, 15) == 8.5  # 5 + 2 + 1.5
    assert account.calculate_monthly_fee("basic", 1500, 8) == 0.0

# Шаг 2: Рефакторим под защитой тестов
class UserAccount:
    def calculate_monthly_fee(self, account_type, balance, transaction_count):
        fee = self._get_base_fee(account_type)
        fee += self._get_balance_fee(balance)
        fee += self._get_transaction_fee(transaction_count)
        return fee
    
    def _get_base_fee(self, account_type):
        fees = {"premium": 10, "standard": 5}
        return fees.get(account_type, 0)
    
    def _get_balance_fee(self, balance):
        return 2 if balance < 1000 else 0
    
    def _get_transaction_fee(self, transaction_count):
        return max(0, transaction_count - 10) * 0.1

# Шаг 3: Добавляем новые TDD тесты для новой функциональности
def test_fee_calculation_edge_cases():
    account = UserAccount()
    
    # Новые edge cases через TDD
    assert account.calculate_monthly_fee("unknown", 0, 0) == 2.0
    assert account.calculate_monthly_fee("premium", 999, 100) == 21.0
```

## 🧪 Работа с большими Legacy классами

### God Object Refactoring

```python
# Типичный God Object в Legacy коде
class OrderManager:
    def __init__(self):
        self.db = DatabaseConnection()
        self.email_service = EmailService()
        self.payment_processor = PaymentProcessor()
        self.inventory = InventoryService()
        self.logger = Logger()
    
    def process_complete_order(self, order_data):
        # 300+ строк кода, который делает все
        
        # Валидация
        if not self._validate_order(order_data):
            return False
        
        # Проверка inventory
        if not self._check_inventory(order_data):
            return False
        
        # Обработка платежа
        payment_result = self._process_payment(order_data)
        if not payment_result:
            return False
        
        # Сохранение заказа
        order_id = self._save_order(order_data)
        
        # Отправка email
        self._send_confirmation_email(order_data, order_id)
        
        # Обновление inventory
        self._update_inventory(order_data)
        
        return order_id
    
    # 20+ приватных методов...

# Стратегия рефакторинга: Extract Service Object
class OrderValidator:
    """Выделенный сервис валидации."""
    
    @staticmethod
    def validate(order_data):
        errors = []
        
        if not order_data:
            errors.append("Order data is required")
        
        if "customer_id" not in order_data:
            errors.append("Customer ID is required")
        
        return {"valid": len(errors) == 0, "errors": errors}

class InventoryChecker:
    """Выделенный сервис проверки inventory."""
    
    def __init__(self, inventory_service):
        self.inventory = inventory_service
    
    def check_availability(self, items):
        for item in items:
            if not self.inventory.is_available(item["id"], item["quantity"]):
                return False
        return True

class OrderOrchestrator:
    """Новый класс, координирующий процесс."""
    
    def __init__(self, validator, inventory_checker, payment_processor):
        self.validator = validator
        self.inventory_checker = inventory_checker
        self.payment_processor = payment_processor
    
    def process_order(self, order_data):
        # Координация через dependency injection
        validation = self.validator.validate(order_data)
        if not validation["valid"]:
            return {"success": False, "errors": validation["errors"]}
        
        if not self.inventory_checker.check_availability(order_data["items"]):
            return {"success": False, "errors": ["Items not available"]}
        
        payment_result = self.payment_processor.process(order_data)
        return payment_result

# Тестирование новой архитектуры
def test_order_orchestrator():
    mock_validator = Mock()
    mock_validator.validate.return_value = {"valid": True, "errors": []}
    
    mock_inventory = Mock()
    mock_inventory.check_availability.return_value = True
    
    mock_payment = Mock()
    mock_payment.process.return_value = {"success": True, "order_id": 123}
    
    orchestrator = OrderOrchestrator(mock_validator, mock_inventory, mock_payment)
    result = orchestrator.process_order({"customer_id": 1, "items": []})
    
    assert result["success"] is True
    assert result["order_id"] == 123
```

## 🔒 Безопасные изменения Legacy кода

### Принципы безопасного рефакторинга

1. **Создайте Safety Net** из тестов
2. **Делайте маленькие шаги**
3. **Запускайте тесты после каждого изменения**
4. **Коммитьте часто**
5. **Имейте план отката**

### Техника: Parallel Change

```python
# Этап 1: Старый интерфейс
class UserService:
    def get_user_by_id(self, user_id):
        # Legacy implementation
        return self.db.query(f"SELECT * FROM users WHERE id = {user_id}")

# Этап 2: Добавляем новый интерфейс параллельно
class UserService:
    def get_user_by_id(self, user_id):
        # Legacy implementation - оставляем как есть
        return self.db.query(f"SELECT * FROM users WHERE id = {user_id}")
    
    def find_user(self, user_id):
        # Новая безопасная реализация
        return self.repository.find_by_id(user_id)

# Этап 3: Переводим клиентов на новый интерфейс
class OrderService:
    def __init__(self, user_service):
        self.user_service = user_service
    
    def process_order(self, user_id, order_data):
        # Используем новый интерфейс
        user = self.user_service.find_user(user_id)
        # ...

# Этап 4: Удаляем старый интерфейс (когда все клиенты мигрированы)
class UserService:
    def find_user(self, user_id):
        return self.repository.find_by_id(user_id)
```

### Branch by Abstraction

```python
# Legacy реализация
def send_notification(user_id, message):
    email = get_user_email(user_id)
    smtp_send(email, message)

# Шаг 1: Создаем абстракцию
class NotificationSender:
    def send(self, user_id, message):
        raise NotImplementedError

class EmailNotificationSender(NotificationSender):
    def send(self, user_id, message):
        email = get_user_email(user_id)
        smtp_send(email, message)

# Шаг 2: Создаем роутер с feature flag
class NotificationRouter(NotificationSender):
    def __init__(self):
        self.email_sender = EmailNotificationSender()
        self.push_sender = PushNotificationSender()  # Новая реализация
        self.feature_flags = FeatureFlags()
    
    def send(self, user_id, message):
        if self.feature_flags.is_enabled("push_notifications"):
            return self.push_sender.send(user_id, message)
        return self.email_sender.send(user_id, message)

# Шаг 3: Заменяем глобальную функцию
def send_notification(user_id, message):
    router = NotificationRouter()
    return router.send(user_id, message)

# Тестирование миграции
def test_notification_migration():
    with feature_flag("push_notifications", enabled=True):
        # Тест новой реализации
        pass
    
    with feature_flag("push_notifications", enabled=False):
        # Тест старой реализации
        pass
```

## 📊 Метрики успеха работы с Legacy

### Code Health Metrics

```python
# Скрипт для отслеживания здоровья Legacy кода
import ast
import os
from pathlib import Path

class LegacyHealthTracker:
    def __init__(self, source_dir):
        self.source_dir = Path(source_dir)
    
    def calculate_metrics(self):
        metrics = {
            "total_files": 0,
            "files_with_tests": 0,
            "average_complexity": 0,
            "large_classes": 0,
            "large_methods": 0,
            "dependency_violations": 0
        }
        
        for py_file in self.source_dir.glob("**/*.py"):
            metrics["total_files"] += 1
            
            # Проверяем наличие тестов
            test_file = self._find_test_file(py_file)
            if test_file.exists():
                metrics["files_with_tests"] += 1
            
            # Анализируем сложность
            complexity = self._calculate_complexity(py_file)
            metrics["average_complexity"] += complexity
            
            # Ищем большие классы/методы
            large_classes, large_methods = self._find_large_constructs(py_file)
            metrics["large_classes"] += large_classes
            metrics["large_methods"] += large_methods
        
        if metrics["total_files"] > 0:
            metrics["average_complexity"] /= metrics["total_files"]
            metrics["test_coverage_ratio"] = metrics["files_with_tests"] / metrics["total_files"]
        
        return metrics
    
    def _find_test_file(self, source_file):
        # Ищем соответствующий тестовый файл
        test_name = f"test_{source_file.name}"
        return source_file.parent / "tests" / test_name
    
    def _calculate_complexity(self, file_path):
        # Упрощенный расчет цикломатической сложности
        with open(file_path, 'r') as f:
            try:
                tree = ast.parse(f.read())
                complexity = 1  # Базовая сложность
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                        complexity += 1
                
                return complexity
            except:
                return 0
    
    def _find_large_constructs(self, file_path):
        # Ищем большие классы и методы
        large_classes = 0
        large_methods = 0
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
            # Простой подсчет строк в классах/методах
            # В реальности нужен более сложный анализ
            
        return large_classes, large_methods

# Использование
tracker = LegacyHealthTracker("src/")
metrics = tracker.calculate_metrics()

print(f"Test Coverage: {metrics['test_coverage_ratio']:.2%}")
print(f"Average Complexity: {metrics['average_complexity']:.1f}")
print(f"Large Classes: {metrics['large_classes']}")
```

### Regression Testing

```python
# Автоматическое создание regression тестов
class RegressionTestGenerator:
    def __init__(self, module):
        self.module = module
        self.test_cases = []
    
    def capture_behavior(self, function_name, test_inputs):
        """Захватывает поведение функции для regression тестов."""
        func = getattr(self.module, function_name)
        
        for i, inputs in enumerate(test_inputs):
            try:
                if isinstance(inputs, dict):
                    result = func(**inputs)
                else:
                    result = func(*inputs)
                
                self.test_cases.append({
                    "function": function_name,
                    "inputs": inputs,
                    "expected": result,
                    "test_name": f"test_{function_name}_case_{i}"
                })
                
            except Exception as e:
                self.test_cases.append({
                    "function": function_name,
                    "inputs": inputs,
                    "exception": type(e).__name__,
                    "message": str(e),
                    "test_name": f"test_{function_name}_exception_case_{i}"
                })
    
    def generate_test_file(self, output_path):
        """Генерирует файл с regression тестами."""
        with open(output_path, 'w') as f:
            f.write("import pytest\n")
            f.write(f"from {self.module.__name__} import *\n\n")
            
            for case in self.test_cases:
                f.write(f"def {case['test_name']}():\n")
                f.write(f'    """Regression test for {case["function"]}."""\n')
                
                if "exception" in case:
                    f.write(f"    with pytest.raises({case['exception']}):\n")
                    f.write(f"        {case['function']}{case['inputs']}\n")
                else:
                    f.write(f"    result = {case['function']}{case['inputs']}\n")
                    f.write(f"    assert result == {repr(case['expected'])}\n")
                
                f.write("\n")

# Использование для Legacy функции
import legacy_module

generator = RegressionTestGenerator(legacy_module)
generator.capture_behavior("calculate_discount", [
    (100, 10),
    (50, 25),
    (0, 10),
    (-10, 5),
])

generator.generate_test_file("test_legacy_regression.py")
```

## 🎯 Лучшие практики

### ✅ Do's

1. **Начинайте с Characterization Tests**
2. **Создавайте Seams для тестирования**
3. **Рефакторьте маленькими шагами**
4. **Используйте Strangler Fig для больших изменений**
5. **Измеряйте прогресс метриками**
6. **Документируйте Legacy поведение**
7. **Имейте план отката**

### ❌ Don'ts

1. **Не переписывайте с нуля** без острой необходимости
2. **Не изменяйте код без тестов**
3. **Не делайте большие изменения за раз**
4. **Не игнорируйте существующее поведение**
5. **Не удаляйте код "просто потому что он старый"**

## 🔮 Следующие шаги

В следующей главе мы изучим **продвинутые техники мокирования** для работы со сложными зависимостями: базами данных, асинхронным кодом и внешними сервисами.

## 🧪 Проверьте свои знания

<div class="quiz-container" id="legacy-code-strategies-quiz">
<script type="application/json">
{
  "title": "Стратегии работы с Legacy Code",
  "description": "Проверьте понимание подходов к работе с унаследованным кодом в TDD",
  "icon": "🏗️",
  "questions": [
    {
      "question": "Что такое Legacy Code по определению Michael Feathers?",
      "type": "single",
      "options": [
        {"text": "Код без тестов", "correct": true},
        {"text": "Код старше 5 лет", "correct": false},
        {"text": "Код без документации", "correct": false},
        {"text": "Код без типизации", "correct": false}
      ],
      "explanation": "Legacy Code — это код без тестов. Без тестов мы не можем быть уверены в корректности изменений.",
      "points": 1
    },
    {
      "question": "Что такое Characterization Tests?",
      "type": "single",
      "options": [
        {"text": "Тесты для проверки производительности", "correct": false},
        {"text": "Тесты, которые фиксируют существующее поведение Legacy кода", "correct": true},
        {"text": "Тесты для новых функций", "correct": false},
        {"text": "Тесты для проверки типов", "correct": false}
      ],
      "explanation": "Characterization Tests фиксируют существующее поведение Legacy кода, создавая 'безопасную сеть' перед рефакторингом.",
      "points": 1
    },
    {
      "question": "Какие стратегии работы с Legacy Code вы знаете? (выберите все правильные)",
      "type": "multiple",
      "options": [
        {"text": "Sprout Method - добавление нового кода в виде отдельного метода", "correct": true},
        {"text": "Wrap Method - обертывание существующего кода", "correct": true},
        {"text": "Strangler Fig - постепенная замена функциональности", "correct": true},
        {"text": "Complete Rewrite - полная переписывание системы", "correct": false},
        {"text": "Big Bang Migration - одновременная миграция всего кода", "correct": false}
      ],
      "explanation": "Основные стратегии: Sprout Method (добавление нового), Wrap Method (обертывание), Strangler Fig (постепенная замена).",
      "points": 2
    },
    {
      "question": "Что такое Seam в контексте работы с Legacy Code?",
      "type": "single",
      "options": [
        {"text": "Раздел в коде, где можно вставить тестовые зависимости", "correct": true},
        {"text": "Тип ошибки в Legacy коде", "correct": false},
        {"text": "Метрика качества кода", "correct": false},
        {"text": "Паттерн проектирования", "correct": false}
      ],
      "explanation": "Seam — это место в коде, где можно вставить тестовые зависимости без изменения основного кода.",
      "points": 1
    },
    {
      "question": "Какой тип Seam позволяет передать зависимость через параметр?",
      "type": "single",
      "options": [
        {"text": "Dependency Injection Seam", "correct": false},
        {"text": "Parameter Seam", "correct": true},
        {"text": "Monkey Patching Seam", "correct": false},
        {"text": "Subclass Seam", "correct": false}
      ],
      "explanation": "Parameter Seam позволяет передать зависимость (например, текущую дату) через параметр метода.",
      "points": 1
    },
    {
      "question": "Что НЕ рекомендуется делать при работе с Legacy Code?",
      "type": "single",
      "options": [
        {"text": "Начинать с Characterization Tests", "correct": false},
        {"text": "Переписывать всю систему с нуля без необходимости", "correct": true},
        {"text": "Создавать Seams для тестирования", "correct": false},
        {"text": "Рефакторить маленькими шагами", "correct": false}
      ],
      "explanation": "Не рекомендуется переписывать всю систему с нуля без острой необходимости — это слишком рискованно.",
      "points": 1
    }
  ]
}
</script>
</div>

---

## 🔗 Связанные темы

- **[Основы TDD](01_tdd_basics.md)** - применение TDD к legacy коду
- **[Mock объекты](08_mocking.md)** - мокирование для legacy кода
- **[Метрики покрытия кода](16_code_coverage_metrics.md)** - измерение покрытия legacy кода
- **[Продвинутое мокирование](18_advanced_mocking.md)** - сложные моки для legacy
- **[TDD и архитектура](19_tdd_architecture.md)** - рефакторинг legacy архитектуры
- **[Лучшие практики](12_best_practices.md)** - практики работы с legacy кодом

**Следующая глава:** [Продвинутое мокирование](18_advanced_mocking.md)

*🏗️ Помните: Legacy код — это не технический долг, это возможность для улучшения!*
