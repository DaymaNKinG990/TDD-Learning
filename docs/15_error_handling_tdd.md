# Тестирование обработки ошибок и исключений в TDD

## 🎯 Введение

Тестирование обработки ошибок — это критически важная часть TDD, которая часто игнорируется разработчиками. Правильное тестирование исключительных ситуаций гарантирует, что ваше приложение работает корректно не только в "счастливых" сценариях, но и при возникновении ошибок.

## 🧠 Основные понятия

### Определения

- **Ошибка (Error)** — неправильное действие или результат, нарушающий функциональность
- **Исключение (Exception)** — механизм обработки ошибок для передачи информации об исключительных ситуациях
- **Обработка ошибок** — выявление, перехват и реакция на ошибки/исключения
- **Тестирование обработки ошибок** — проверка корректности реакции кода на исключительные ситуации

### Цели тестирования обработки ошибок

1. **Гарантировать корректную работу** приложения при ошибках
2. **Проверить корректный перехват и обработку** ошибок
3. **Обеспечить информативность** сообщений об ошибках
4. **Предотвратить неотловленные исключения** и аварийное завершение

## 🏷 Классификация ошибок

### 1. По времени возникновения

```python
# Синтаксические ошибки (на этапе интерпретации)
def invalid_syntax():
    return "missing quote  # SyntaxError

# Логические ошибки (неправильная реализация)
def calculate_age(birth_year):
    return 2024 + birth_year  # Должно быть: 2024 - birth_year

# Ошибки времени выполнения
def divide_numbers(a, b):
    return a / b  # ZeroDivisionError при b=0
```

### 2. По источнику

```python
# Системные ошибки
def read_config_file():
    with open('config.txt', 'r') as f:  # FileNotFoundError
        return f.read()

# Ошибки валидации входных данных
def create_user(email, age):
    if not email or '@' not in email:
        raise ValueError("Invalid email format")
    if age < 0 or age > 150:
        raise ValueError("Invalid age")

# Ошибки бизнес-логики
def withdraw_money(account, amount):
    if amount > account.balance:
        raise InsufficientFundsError("Not enough money")
```

### 3. Пользовательские исключения

```python
# Создание собственных исключений
class BankAccountError(Exception):
    """Base exception for bank account operations."""
    pass

class InsufficientFundsError(BankAccountError):
    """Raised when account has insufficient funds."""
    pass

class InvalidAmountError(BankAccountError):
    """Raised when amount is invalid."""
    pass

class AccountNotFoundError(BankAccountError):
    """Raised when account doesn't exist."""
    pass
```

## 🔴 TDD подход к тестированию ошибок

### Принципы тестирования обработки ошибок в TDD

1. **Тесты на обработку ошибок пишутся ДО реализации** функциональности
2. **Охват всех возможных ошибочных сценариев**, включая граничные случаи
3. **Явное указание ожидаемого типа и сообщения** исключения
4. **Атомарность и независимость** тестов

### RED-GREEN-REFACTOR для обработки ошибок

#### 🔴 RED: Тест на исключение

```python
# test_bank_account.py
import pytest
from bank_account import BankAccount, InsufficientFundsError

def test_withdraw_more_than_balance_raises_error():
    """Снятие суммы больше баланса должно вызывать исключение."""
    account = BankAccount(100)
    
    with pytest.raises(InsufficientFundsError) as exc_info:
        account.withdraw(150)
    
    assert "insufficient funds" in str(exc_info.value).lower()
    assert account.balance == 100  # Баланс не изменился
```

#### 🟢 GREEN: Минимальная реализация

```python
# bank_account.py
class InsufficientFundsError(Exception):
    pass

class BankAccount:
    def __init__(self, initial_balance=0):
        self.balance = initial_balance
    
    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFundsError("Insufficient funds")
        self.balance -= amount
```

#### 🔵 REFACTOR: Улучшение обработки

```python
class BankAccount:
    def __init__(self, initial_balance=0):
        self._validate_amount(initial_balance)
        self.balance = initial_balance
    
    def withdraw(self, amount):
        self._validate_amount(amount)
        if amount > self.balance:
            raise InsufficientFundsError(
                f"Cannot withdraw {amount}. Available balance: {self.balance}"
            )
        self.balance -= amount
    
    def _validate_amount(self, amount):
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        if not isinstance(amount, (int, float)):
            raise TypeError("Amount must be a number")
```

## 🧪 Техники тестирования исключений

### 1. pytest.raises

```python
import pytest

def test_division_by_zero():
    """Тестирование деления на ноль."""
    with pytest.raises(ZeroDivisionError):
        result = 10 / 0

def test_division_by_zero_with_message():
    """Проверка сообщения об ошибке."""
    with pytest.raises(ZeroDivisionError) as exc_info:
        result = 10 / 0
    
    assert "division by zero" in str(exc_info.value)

def test_specific_exception_type():
    """Проверка конкретного типа исключения."""
    with pytest.raises(ValueError, match=r"invalid literal.*"):
        int("not_a_number")
```

### 2. unittest.TestCase

```python
import unittest

class TestErrorHandling(unittest.TestCase):
    
    def test_value_error_raised(self):
        """Тест с unittest assertRaises."""
        with self.assertRaises(ValueError) as context:
            int("not_a_number")
        
        self.assertIn("invalid literal", str(context.exception))
    
    def test_exception_message(self):
        """Проверка сообщения исключения."""
        with self.assertRaisesRegex(ValueError, r"invalid literal.*"):
            int("not_a_number")
    
    def test_no_exception_raised(self):
        """Проверка, что исключение НЕ возникает."""
        try:
            result = int("42")
            self.assertEqual(result, 42)
        except ValueError:
            self.fail("ValueError raised unexpectedly")
```

### 3. Тестирование множественных исключений

```python
def test_user_validation_errors():
    """Тестирование различных ошибок валидации."""
    
    # Тест 1: Пустой email
    with pytest.raises(ValueError, match="Email cannot be empty"):
        create_user("", "password123")
    
    # Тест 2: Невалидный email
    with pytest.raises(ValueError, match="Invalid email format"):
        create_user("invalid-email", "password123")
    
    # Тест 3: Слабый пароль
    with pytest.raises(ValueError, match="Password too weak"):
        create_user("user@example.com", "123")

@pytest.mark.parametrize("invalid_input,expected_error", [
    ("", "Email cannot be empty"),
    ("invalid-email", "Invalid email format"),
    ("user@domain", "Invalid domain"),
])
def test_email_validation_errors(invalid_input, expected_error):
    """Параметризованный тест ошибок валидации."""
    with pytest.raises(ValueError, match=expected_error):
        validate_email(invalid_input)
```

## 🎭 Подходы к тестированию обработки ошибок

### 1. Позитивное тестирование

```python
def test_successful_user_creation():
    """Тест успешного создания пользователя."""
    user = create_user("john@example.com", "StrongP@ssw0rd!")
    
    assert user.email == "john@example.com"
    assert user.is_active is True
    assert user.created_at is not None
```

### 2. Негативное тестирование

```python
def test_user_creation_with_invalid_data():
    """Тест создания пользователя с невалидными данными."""
    
    # Невалидный email
    with pytest.raises(ValueError):
        create_user("invalid-email", "password")
    
    # Пустой пароль
    with pytest.raises(ValueError):
        create_user("user@example.com", "")
    
    # None значения
    with pytest.raises(TypeError):
        create_user(None, None)
```

### 3. Тестирование граничных условий

```python
def test_boundary_conditions():
    """Тест граничных условий."""
    
    # Минимальные валидные значения
    user = create_user("a@b.co", "1234567890")  # Минимальная длина
    assert user is not None
    
    # Максимальные валидные значения
    long_email = "a" * 50 + "@" + "b" * 50 + ".com"
    user = create_user(long_email, "x" * 100)
    assert user is not None
    
    # Превышение границ
    with pytest.raises(ValueError):
        create_user("a" * 300 + "@example.com", "password")  # Слишком длинный email
```

## 🛡 Стратегии обработки ошибок

### 1. Fail Fast (Быстрый отказ)

```python
def process_payment(amount, card_number, cvv):
    """Быстро падаем при первой же ошибке."""
    
    # Валидация входных данных
    if amount <= 0:
        raise ValueError("Amount must be positive")
    
    if not card_number or len(card_number) != 16:
        raise ValueError("Invalid card number")
    
    if not cvv or len(cvv) != 3:
        raise ValueError("Invalid CVV")
    
    # Обработка платежа...
    return process_transaction(amount, card_number, cvv)

def test_payment_fail_fast():
    """Тест стратегии Fail Fast."""
    
    # Тест падает сразу на первой ошибке
    with pytest.raises(ValueError, match="Amount must be positive"):
        process_payment(-100, "1234567890123456", "123")
    
    # Не доходим до проверки карты при неверной сумме
    with pytest.raises(ValueError, match="Amount must be positive"):
        process_payment(0, "invalid", "bad")  # Проверяется только amount
```

### 2. Graceful Degradation (Изящная деградация)

```python
def get_user_profile(user_id):
    """Возвращаем частичные данные при ошибках."""
    profile = {"id": user_id}
    
    try:
        profile["basic_info"] = get_basic_info(user_id)
    except DatabaseError:
        profile["basic_info"] = {"name": "Unknown", "email": "N/A"}
    
    try:
        profile["preferences"] = get_user_preferences(user_id)
    except ServiceUnavailableError:
        profile["preferences"] = get_default_preferences()
    
    return profile

def test_graceful_degradation(mocker):
    """Тест изящной деградации."""
    # Мокируем ошибку получения базовой информации
    mocker.patch('myapp.get_basic_info', side_effect=DatabaseError())
    mocker.patch('myapp.get_user_preferences', return_value={"theme": "dark"})
    
    profile = get_user_profile(123)
    
    assert profile["id"] == 123
    assert profile["basic_info"]["name"] == "Unknown"  # Fallback значения
    assert profile["preferences"]["theme"] == "dark"   # Успешно получено
```

### 3. Retry и Circuit Breaker

```python
import time
from functools import wraps

def retry(max_attempts=3, delay=1):
    """Декоратор для повторных попыток."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (ConnectionError, TimeoutError) as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                    continue
                except Exception as e:
                    # Не повторяем для других типов ошибок
                    raise e
            
            raise last_exception
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.1)
def unreliable_api_call():
    """Ненадежный API вызов."""
    if random.random() < 0.7:  # 70% вероятность ошибки
        raise ConnectionError("Network error")
    return {"status": "success"}

def test_retry_mechanism(mocker):
    """Тест механизма повторных попыток."""
    mock_func = mocker.Mock()
    mock_func.side_effect = [
        ConnectionError("First failure"),
        ConnectionError("Second failure"),
        {"status": "success"}  # Третья попытка успешна
    ]
    
    # Применяем декоратор к mock функции
    retried_func = retry(max_attempts=3, delay=0)(mock_func)
    
    result = retried_func()
    
    assert result == {"status": "success"}
    assert mock_func.call_count == 3  # Было 3 попытки
```

## 🔬 Продвинутые техники

### 1. Тестирование логирования ошибок

```python
import logging
import pytest

def risky_operation(data):
    """Операция с логированием ошибок."""
    logger = logging.getLogger(__name__)
    
    try:
        if not data:
            raise ValueError("Data cannot be empty")
        
        result = process_data(data)
        logger.info(f"Successfully processed {len(data)} items")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        raise

def test_error_logging(caplog):
    """Тест логирования ошибок."""
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError):
            risky_operation(None)
    
    assert "Validation error: Data cannot be empty" in caplog.text
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"
```

### 2. Тестирование восстановления состояния

```python
class DatabaseTransaction:
    def __init__(self, db):
        self.db = db
        self.in_transaction = False
    
    def execute(self, operations):
        """Выполняет операции в транзакции."""
        try:
            self.db.begin_transaction()
            self.in_transaction = True
            
            for operation in operations:
                operation.execute(self.db)
            
            self.db.commit()
            self.in_transaction = False
            
        except Exception as e:
            if self.in_transaction:
                self.db.rollback()
                self.in_transaction = False
            raise e

def test_transaction_rollback_on_error(mocker):
    """Тест отката транзакции при ошибке."""
    mock_db = mocker.Mock()
    failing_operation = mocker.Mock()
    failing_operation.execute.side_effect = RuntimeError("Operation failed")
    
    transaction = DatabaseTransaction(mock_db)
    
    with pytest.raises(RuntimeError):
        transaction.execute([failing_operation])
    
    # Проверяем что транзакция была начата и откачена
    mock_db.begin_transaction.assert_called_once()
    mock_db.rollback.assert_called_once()
    mock_db.commit.assert_not_called()
    assert transaction.in_transaction is False
```

### 3. Тестирование асинхронных ошибок

```python
import asyncio
import pytest

async def async_operation(url):
    """Асинхронная операция с обработкой ошибок."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status >= 400:
                    raise HTTPError(f"HTTP {response.status}")
                return await response.json()
    except asyncio.TimeoutError:
        raise TimeoutError(f"Timeout while accessing {url}")
    except aiohttp.ClientError as e:
        raise ConnectionError(f"Connection failed: {e}")

@pytest.mark.asyncio
async def test_async_timeout_error(mocker):
    """Тест асинхронной ошибки таймаута."""
    # Мокируем aiohttp для имитации таймаута
    mock_session = mocker.patch('aiohttp.ClientSession')
    mock_session.return_value.__aenter__.return_value.get.side_effect = asyncio.TimeoutError()
    
    with pytest.raises(TimeoutError, match="Timeout while accessing"):
        await async_operation("http://example.com")

@pytest.mark.asyncio
async def test_async_http_error(mocker):
    """Тест HTTP ошибки в асинхронной функции."""
    mock_response = mocker.Mock()
    mock_response.status = 404
    
    mock_session = mocker.patch('aiohttp.ClientSession')
    mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
    
    with pytest.raises(HTTPError, match="HTTP 404"):
        await async_operation("http://example.com/not-found")
```

## 🚨 Антипаттерны и ошибки

### ❌ Что НЕ делать

#### 1. Поглощение исключений

```python
# ❌ Плохо: молчаливое поглощение ошибок
def bad_error_handling(data):
    try:
        return process_data(data)
    except:  # Слишком широкий except
        return None  # Теряем информацию об ошибке

# ✅ Хорошо: явная обработка
def good_error_handling(data):
    try:
        return process_data(data)
    except ValueError as e:
        logger.warning(f"Invalid data provided: {e}")
        raise
    except ConnectionError as e:
        logger.error(f"Connection failed: {e}")
        raise ServiceUnavailableError("Service temporarily unavailable")
```

#### 2. Неинформативные сообщения

```python
# ❌ Плохо: неинформативные сообщения
def validate_age(age):
    if age < 0:
        raise ValueError("Bad age")  # Что именно плохого?

# ✅ Хорошо: подробные сообщения
def validate_age(age):
    if not isinstance(age, int):
        raise TypeError(f"Age must be an integer, got {type(age).__name__}")
    if age < 0:
        raise ValueError(f"Age cannot be negative, got {age}")
    if age > 150:
        raise ValueError(f"Age cannot exceed 150, got {age}")
```

#### 3. Тестирование только позитивных сценариев

```python
# ❌ Недостаточно: только позитивные тесты
def test_calculator_add():
    assert add(2, 3) == 5

# ✅ Полно: позитивные и негативные тесты
def test_calculator_add_positive():
    assert add(2, 3) == 5

def test_calculator_add_with_zero():
    assert add(0, 5) == 5
    assert add(5, 0) == 5

def test_calculator_add_negative():
    assert add(-2, 3) == 1
    assert add(2, -3) == -1

def test_calculator_add_invalid_types():
    with pytest.raises(TypeError):
        add("2", 3)
    
    with pytest.raises(TypeError):
        add(2, None)
```

## 📊 Метрики качества обработки ошибок

### 1. Покрытие ошибочных путей

```python
# Используем coverage.py для измерения покрытия
# Запуск: uv run pytest --cov=myapp --cov-branch --cov-report=html

def calculate_discount(price, discount_percent):
    if price < 0:                    # Ошибочный путь 1
        raise ValueError("Price cannot be negative")
    
    if discount_percent < 0:         # Ошибочный путь 2
        raise ValueError("Discount cannot be negative")
    
    if discount_percent > 100:       # Ошибочный путь 3
        raise ValueError("Discount cannot exceed 100%")
    
    return price * (1 - discount_percent / 100)  # Успешный путь

# Тесты должны покрыть ВСЕ пути
def test_calculate_discount_coverage():
    # Успешный путь
    assert calculate_discount(100, 10) == 90
    
    # Все ошибочные пути
    with pytest.raises(ValueError, match="Price cannot be negative"):
        calculate_discount(-100, 10)
    
    with pytest.raises(ValueError, match="Discount cannot be negative"):
        calculate_discount(100, -10)
    
    with pytest.raises(ValueError, match="Discount cannot exceed 100%"):
        calculate_discount(100, 110)
```

### 2. Время восстановления после ошибки

```python
import time

def test_error_recovery_time():
    """Тест времени восстановления после ошибки."""
    service = ResilientService()
    
    # Имитируем ошибку
    start_time = time.time()
    
    try:
        service.failing_operation()
    except ServiceError:
        pass
    
    # Проверяем быстрое восстановление
    recovery_time = time.time() - start_time
    assert recovery_time < 1.0  # Восстановление менее чем за 1 секунду
    
    # Сервис должен работать после ошибки
    result = service.normal_operation()
    assert result is not None
```

## 🎯 Лучшие практики

### ✅ Рекомендации

1. **Покрывайте тестами все ветви обработки ошибок**
2. **Используйте специфичные типы исключений**
3. **Пишите информативные сообщения об ошибках**
4. **Тестируйте восстановление состояния после ошибок**
5. **Используйте pytest.mark.parametrize для тестирования множественных ошибок**
6. **Логируйте ошибки с соответствующим уровнем важности**
7. **Документируйте возможные исключения в docstring**

### 📝 Чек-лист для code review

- [ ] Все возможные исключения покрыты тестами?
- [ ] Сообщения об ошибках информативны?
- [ ] Используются специфичные типы исключений?
- [ ] Состояние корректно восстанавливается после ошибок?
- [ ] Ошибки правильно логируются?
- [ ] Нет молчаливого поглощения исключений?
- [ ] Граничные условия протестированы?

## 🔮 Следующие шаги

В следующей главе мы изучим **метрики покрытия кода**, которые помогут измерить качество наших тестов и убедиться, что все пути выполнения (включая ошибочные) протестированы.

## 🧪 Проверьте свои знания

<div class="quiz-container" id="error-handling-tdd-quiz">
<script type="application/json">
{
  "title": "Тестирование обработки ошибок",
  "description": "Проверьте знание техник тестирования исключений и ошибок",
  "icon": "⚠️",
  "questions": [
    {
      "question": "Какие основные категории ошибок нужно тестировать? (выберите все правильные)",
      "type": "multiple",
      "options": [
        {"text": "Валидационные ошибки (некорректные данные)", "correct": true},
        {"text": "Системные ошибки (недоступность ресурсов)", "correct": true},
        {"text": "Бизнес-логические ошибки (нарушение правил)", "correct": true},
        {"text": "Неожиданные ошибки (непредвиденные ситуации)", "correct": true},
        {"text": "Синтаксические ошибки Python", "correct": false}
      ],
      "explanation": "В TDD тестируются: валидационные, системные, бизнес-логические и неожиданные ошибки. Синтаксические ошибки обнаруживаются на этапе компиляции.",
      "points": 2
    },
    {
      "question": "Какая стратегия обработки ошибок предполагает немедленное прерывание при ошибке?",
      "type": "single",
      "options": [
        {"text": "Graceful Degradation", "correct": false},
        {"text": "Fail Fast", "correct": true},
        {"text": "Error Recovery", "correct": false},
        {"text": "Silent Failure", "correct": false}
      ],
      "explanation": "Fail Fast - стратегия немедленного прерывания работы при обнаружении ошибки, что помогает быстро локализовать проблему.",
      "points": 1
    },
    {
      "question": "Как правильно тестировать асинхронные исключения?",
      "type": "single",
      "options": [
        {"text": "Использовать только try/except блоки", "correct": false},
        {"text": "pytest.raises + @pytest.mark.asyncio", "correct": true},
        {"text": "Только через unittest.TestCase", "correct": false},
        {"text": "Асинхронные исключения нельзя тестировать", "correct": false}
      ],
      "explanation": "Для тестирования асинхронных исключений используется pytest.raises в сочетании с @pytest.mark.asyncio для корректного выполнения async/await кода.",
      "points": 1
    },
    {
      "question": "Что включает в себя тестирование восстановления состояния?",
      "type": "multiple",
      "options": [
        {"text": "Проверка корректного отката транзакций", "correct": true},
        {"text": "Освобождение ресурсов (файлы, соединения)", "correct": true},
        {"text": "Очистка временных данных", "correct": true},
        {"text": "Восстановление исходного состояния объектов", "correct": true},
        {"text": "Автоматическое исправление ошибок", "correct": false}
      ],
      "explanation": "Тестирование восстановления включает проверку отката транзакций, освобождения ресурсов, очистки данных и восстановления состояния. Автоматическое исправление - отдельная тема.",
      "points": 2
    },
    {
      "question": "Какой подход лучше для создания кастомных исключений?",
      "type": "single",
      "options": [
        {"text": "Использовать только стандартные исключения Python", "correct": false},
        {"text": "Создать иерархию специфичных исключений для домена", "correct": true},
        {"text": "Использовать только Exception", "correct": false},
        {"text": "Создавать новое исключение для каждой функции", "correct": false}
      ],
      "explanation": "Лучший подход - создать иерархию доменно-специфичных исключений, которые наследуются от базовых и несут смысловую нагрузку для конкретной предметной области.",
      "points": 1
    },
    {
      "question": "Что НЕ рекомендуется делать при обработке ошибок в тестах?",
      "type": "single",
      "options": [
        {"text": "Тестировать сообщения об ошибках", "correct": false},
        {"text": "Проверять типы исключений", "correct": false},
        {"text": "Молчаливо поглощать исключения (except: pass)", "correct": true},
        {"text": "Использовать pytest.raises", "correct": false}
      ],
      "explanation": "Молчаливое поглощение исключений (bare except: pass) является анти-паттерном, так как скрывает реальные проблемы и делает отладку невозможной.",
      "points": 1
    }
  ]
}
</script>
</div>

---

## 🔗 Связанные темы

- **[Практические примеры](07_practical_examples.md)** - примеры обработки ошибок
- **[Mock объекты](08_mocking.md)** - мокирование исключений
- **[CI/CD и автоматизация](14_ci_cd_automation.md)** - обработка ошибок в CI/CD
- **[Метрики покрытия кода](16_code_coverage_metrics.md)** - покрытие обработки ошибок
- **[Стратегии работы с Legacy Code](17_legacy_code_strategies.md)** - обработка ошибок в legacy коде
- **[Лучшие практики](12_best_practices.md)** - лучшие практики обработки ошибок

**Предыдущая глава:** [CI/CD и автоматизация](14_ci_cd_automation.md)  
**Следующая глава:** [Метрики покрытия кода](16_code_coverage_metrics.md)

*⚠️ Помните: правильная обработка ошибок — это не только про исключения, но и про пользовательский опыт!*
