# Unittest: Стандартный модуль тестирования Python

## 🎯 Введение в unittest

Модуль `unittest` — это стандартная библиотека Python для тестирования, вдохновленная JUnit (Java). Хотя pytest более популярен в сообществе, unittest остается важным инструментом, особенно в корпоративной среде и legacy проектах.

## 📚 Основы unittest

### Структура теста

```python
import unittest

class TestCalculator(unittest.TestCase):
    """Тесты для класса Calculator."""
    
    def setUp(self):
        """Вызывается перед каждым тестом."""
        self.calc = Calculator()
    
    def tearDown(self):
        """Вызывается после каждого теста."""
        # Очистка ресурсов, если необходимо
        pass
    
    def test_add_positive_numbers(self):
        """Сложение положительных чисел."""
        result = self.calc.add(2, 3)
        self.assertEqual(result, 5)
    
    def test_divide_by_zero(self):
        """Деление на ноль вызывает исключение."""
        with self.assertRaises(ZeroDivisionError):
            self.calc.divide(10, 0)

if __name__ == '__main__':
    unittest.main()
```

### Запуск тестов

```bash
# Запуск конкретного файла
python test_calculator.py

# Запуск всех тестов в директории
python -m unittest discover

# Запуск с подробным выводом
python -m unittest -v

# Запуск конкретного класса
python -m unittest test_calculator.TestCalculator

# Запуск конкретного теста
python -m unittest test_calculator.TestCalculator.test_add_positive_numbers
```

## 🔧 Методы assertion в unittest

### Базовые проверки

```python
class TestAssertions(unittest.TestCase):
    
    def test_equality_assertions(self):
        """Проверки равенства."""
        self.assertEqual(2 + 2, 4)
        self.assertNotEqual(2 + 2, 5)
        
        # Для чисел с плавающей точкой
        self.assertAlmostEqual(0.1 + 0.2, 0.3, places=7)
        
    def test_boolean_assertions(self):
        """Логические проверки."""
        self.assertTrue(True)
        self.assertFalse(False)
        
    def test_none_assertions(self):
        """Проверки на None."""
        self.assertIsNone(None)
        self.assertIsNotNone("not none")
        
    def test_membership_assertions(self):
        """Проверки принадлежности."""
        self.assertIn(1, [1, 2, 3])
        self.assertNotIn(4, [1, 2, 3])
        
    def test_type_assertions(self):
        """Проверки типов."""
        self.assertIsInstance("hello", str)
        self.assertNotIsInstance("hello", int)
        
    def test_comparison_assertions(self):
        """Проверки сравнения."""
        self.assertGreater(5, 3)
        self.assertLess(3, 5)
        self.assertGreaterEqual(5, 5)
        self.assertLessEqual(3, 5)
```

### Проверки исключений

```python
class TestExceptions(unittest.TestCase):
    
    def test_exception_raised(self):
        """Проверка что исключение возникает."""
        with self.assertRaises(ValueError):
            int("not a number")
    
    def test_exception_message(self):
        """Проверка сообщения исключения."""
        with self.assertRaisesRegex(ValueError, "invalid literal"):
            int("not a number")
    
    def test_no_exception(self):
        """Проверка что исключение НЕ возникает."""
        try:
            result = int("123")
            self.assertEqual(result, 123)
        except ValueError:
            self.fail("int() raised ValueError unexpectedly!")
```

### Проверки строк и регулярных выражений

```python
class TestStringAssertions(unittest.TestCase):
    
    def test_string_comparisons(self):
        """Проверки строк."""
        text = "Hello World"
        
        self.assertRegex(text, r"Hello.*")
        self.assertNotRegex(text, r"Goodbye.*")
        
        self.assertMultiLineEqual(
            "line1\nline2", 
            "line1\nline2"
        )
        
    def test_sequence_assertions(self):
        """Проверки последовательностей."""
        list1 = [1, 2, 3]
        list2 = [1, 2, 3]
        
        self.assertListEqual(list1, list2)
        self.assertCountEqual([1, 2, 3], [3, 2, 1])  # Порядок не важен
```

## 🏗 Организация тестов

### Фикстуры (setUp/tearDown)

```python
class TestDatabaseOperations(unittest.TestCase):
    """Тесты операций с базой данных."""
    
    @classmethod
    def setUpClass(cls):
        """Вызывается один раз для всего класса."""
        cls.database = create_test_database()
    
    @classmethod
    def tearDownClass(cls):
        """Вызывается один раз после всех тестов класса."""
        cls.database.close()
    
    def setUp(self):
        """Вызывается перед каждым тестом."""
        self.user = User("test@example.com", "Test User")
        self.database.clear()
    
    def tearDown(self):
        """Вызывается после каждого теста."""
        self.database.rollback()
    
    def test_save_user(self):
        """Сохранение пользователя в БД."""
        saved_user = self.database.save(self.user)
        self.assertIsNotNone(saved_user.id)
        
    def test_find_user_by_email(self):
        """Поиск пользователя по email."""
        self.database.save(self.user)
        found_user = self.database.find_by_email("test@example.com")
        self.assertEqual(found_user.email, self.user.email)
```

### Группировка тестов в наборы

```python
def suite():
    """Создание набора тестов."""
    test_suite = unittest.TestSuite()
    
    # Добавление конкретных тестов
    test_suite.addTest(TestCalculator('test_add_positive_numbers'))
    test_suite.addTest(TestCalculator('test_divide_by_zero'))
    
    # Добавление всех тестов класса
    test_suite.addTest(unittest.makeSuite(TestDatabaseOperations))
    
    return test_suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
```

## 🎭 Мокирование в unittest

### Модуль unittest.mock

```python
import unittest
from unittest.mock import Mock, patch, MagicMock

class TestEmailService(unittest.TestCase):
    """Тесты сервиса отправки email."""
    
    def test_send_email_success(self):
        """Успешная отправка email."""
        # Создание мока
        mock_smtp = Mock()
        mock_smtp.send_message.return_value = True
        
        email_service = EmailService(smtp_client=mock_smtp)
        result = email_service.send("test@example.com", "Subject", "Body")
        
        self.assertTrue(result)
        mock_smtp.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_email_with_patch(self, mock_smtp_class):
        """Тест с использованием декоратора patch."""
        mock_smtp = mock_smtp_class.return_value
        mock_smtp.send_message.return_value = True
        
        email_service = EmailService()
        result = email_service.send("test@example.com", "Subject", "Body")
        
        self.assertTrue(result)
        mock_smtp.send_message.assert_called_once()
    
    def test_send_email_failure(self):
        """Обработка ошибки при отправке email."""
        mock_smtp = Mock()
        mock_smtp.send_message.side_effect = Exception("SMTP Error")
        
        email_service = EmailService(smtp_client=mock_smtp)
        
        with self.assertRaises(EmailSendError):
            email_service.send("test@example.com", "Subject", "Body")
```

### Продвинутые техники мокирования

```python
class TestAdvancedMocking(unittest.TestCase):
    """Продвинутые техники мокирования."""
    
    @patch('requests.get')
    def test_api_call_with_mock(self, mock_get):
        """Мокирование HTTP запроса."""
        # Настройка мока
        mock_response = Mock()
        mock_response.json.return_value = {'status': 'success', 'data': []}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Тестируемый код
        api_client = APIClient()
        result = api_client.get_users()
        
        # Проверки
        self.assertEqual(result['status'], 'success')
        mock_get.assert_called_once_with('https://api.example.com/users')
    
    def test_mock_with_side_effect(self):
        """Использование side_effect для последовательности значений."""
        mock_db = Mock()
        mock_db.query.side_effect = [
            [{'id': 1, 'name': 'User 1'}],  # Первый вызов
            [],  # Второй вызов
            Exception("Database error")  # Третий вызов
        ]
        
        service = UserService(database=mock_db)
        
        # Первый вызов - успешно
        users = service.get_all_users()
        self.assertEqual(len(users), 1)
        
        # Второй вызов - пустой результат
        users = service.get_all_users()
        self.assertEqual(len(users), 0)
        
        # Третий вызов - исключение
        with self.assertRaises(Exception):
            service.get_all_users()
    
    @patch.object(User, 'save')
    def test_patch_object(self, mock_save):
        """Мокирование метода объекта."""
        mock_save.return_value = True
        
        user = User("test@example.com")
        result = user.save()
        
        self.assertTrue(result)
        mock_save.assert_called_once()
```

## 📊 Пропуск и условные тесты

### Пропуск тестов

```python
import sys
import unittest

class TestConditional(unittest.TestCase):
    """Условные тесты."""
    
    @unittest.skip("Временно отключен")
    def test_temporarily_disabled(self):
        """Этот тест временно отключен."""
        self.fail("Не должен выполняться")
    
    @unittest.skipIf(sys.platform == "win32", "Не работает на Windows")
    def test_unix_only(self):
        """Тест только для Unix систем."""
        import os
        self.assertTrue(hasattr(os, 'fork'))
    
    @unittest.skipUnless(sys.platform.startswith("linux"), "Требует Linux")
    def test_linux_only(self):
        """Тест только для Linux."""
        with open('/proc/version') as f:
            version = f.read()
        self.assertIn('Linux', version)
    
    def test_conditional_skip(self):
        """Условный пропуск внутри теста."""
        if not hasattr(sys, 'gettrace'):
            self.skipTest("Отладчик недоступен")
        
        # Тест выполняется только если доступен отладчик
        self.assertIsNotNone(sys.gettrace)
```

### Ожидаемые падения

```python
class TestExpectedFailures(unittest.TestCase):
    """Ожидаемые падения тестов."""
    
    @unittest.expectedFailure
    def test_known_bug(self):
        """Известный баг, который еще не исправлен."""
        self.assertEqual(1, 0)  # Известно что падает
    
    def test_unexpected_success(self):
        """Если этот тест пройдет, это будет неожиданно."""
        # Если баг исправлен, тест покажет неожиданный успех
        pass
```

## 🎯 Практический пример: TDD с unittest

Создадим систему банковского счета с помощью TDD и unittest:

### Итерация 1: Создание счета

```python
# test_bank_account.py
import unittest
from decimal import Decimal

class TestBankAccount(unittest.TestCase):
    """Тесты банковского счета."""
    
    def test_new_account_has_zero_balance(self):
        """Новый счет имеет нулевой баланс."""
        account = BankAccount("ACC123")  # Класса пока нет!
        self.assertEqual(account.balance, Decimal("0.00"))
    
    def test_account_has_account_number(self):
        """Счет имеет номер."""
        account = BankAccount("ACC123")
        self.assertEqual(account.account_number, "ACC123")

# bank_account.py
from decimal import Decimal

class BankAccount:
    """Банковский счет."""
    
    def __init__(self, account_number: str):
        self.account_number = account_number
        self.balance = Decimal("0.00")
```

### Итерация 2: Пополнение счета

```python
class TestBankAccount(unittest.TestCase):
    # ... предыдущие тесты ...
    
    def setUp(self):
        """Создание счета для каждого теста."""
        self.account = BankAccount("ACC123")
    
    def test_deposit_positive_amount(self):
        """Пополнение положительной суммой."""
        self.account.deposit(Decimal("100.00"))
        self.assertEqual(self.account.balance, Decimal("100.00"))
    
    def test_deposit_negative_amount_raises_error(self):
        """Пополнение отрицательной суммой вызывает ошибку."""
        with self.assertRaises(ValueError):
            self.account.deposit(Decimal("-10.00"))
    
    def test_deposit_zero_raises_error(self):
        """Пополнение нулевой суммой вызывает ошибку."""
        with self.assertRaisesRegex(ValueError, "Amount must be positive"):
            self.account.deposit(Decimal("0.00"))

# Реализация
class BankAccount:
    def __init__(self, account_number: str):
        self.account_number = account_number
        self.balance = Decimal("0.00")
    
    def deposit(self, amount: Decimal) -> None:
        """Пополнить счет."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.balance += amount
```

### Итерация 3: Снятие средств

```python
class TestBankAccount(unittest.TestCase):
    # ... предыдущие тесты ...
    
    def test_withdraw_valid_amount(self):
        """Снятие допустимой суммы."""
        self.account.deposit(Decimal("100.00"))
        self.account.withdraw(Decimal("30.00"))
        self.assertEqual(self.account.balance, Decimal("70.00"))
    
    def test_withdraw_more_than_balance_raises_error(self):
        """Снятие суммы больше баланса вызывает ошибку."""
        self.account.deposit(Decimal("50.00"))
        with self.assertRaisesRegex(ValueError, "Insufficient funds"):
            self.account.withdraw(Decimal("100.00"))

# Реализация
class BankAccount:
    # ... предыдущий код ...
    
    def withdraw(self, amount: Decimal) -> None:
        """Снять средства."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
```

## 🔧 Настройка и конфигурация

### Настройка вывода

```python
import unittest
import sys

class ColoredTextTestResult(unittest.TextTestResult):
    """Цветной вывод результатов тестов."""
    
    def addSuccess(self, test):
        super().addSuccess(test)
        if self.showAll:
            self.stream.write("✅ PASS\n")
    
    def addError(self, test, err):
        super().addError(test, err)
        if self.showAll:
            self.stream.write("💥 ERROR\n")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.showAll:
            self.stream.write("❌ FAIL\n")

class ColoredTextTestRunner(unittest.TextTestRunner):
    """Тестраннер с цветным выводом."""
    resultclass = ColoredTextTestResult

if __name__ == '__main__':
    unittest.main(testRunner=ColoredTextTestRunner(verbosity=2))
```

### Конфигурационный файл

```python
# test_config.py
import unittest
import os

class TestConfig:
    """Конфигурация для тестов."""
    
    def __init__(self):
        self.database_url = os.getenv(
            'TEST_DATABASE_URL', 
            'sqlite:///:memory:'
        )
        self.api_base_url = os.getenv(
            'TEST_API_URL', 
            'http://localhost:8000'
        )
        self.timeout = int(os.getenv('TEST_TIMEOUT', '30'))

# Использование в тестах
class TestWithConfig(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.config = TestConfig()
    
    def test_database_connection(self):
        """Тест подключения к БД."""
        db = Database(self.config.database_url)
        self.assertTrue(db.is_connected())
```

## 📈 Сравнение unittest vs pytest

| Критерий | unittest | pytest |
|----------|----------|---------|
| **Синтаксис** | Verbose (self.assertEqual) | Простой (assert) |
| **Фикстуры** | setUp/tearDown методы | Декораторы @pytest.fixture |
| **Обнаружение тестов** | Строгие правила именования | Гибкое автообнаружение |
| **Параметризация** | Требует дополнительного кода | @pytest.mark.parametrize |
| **Плагины** | Ограниченная экосистема | Богатая экосистема |
| **Совместимость** | Стандартная библиотека | Внешняя зависимость |

### Миграция с unittest на pytest

```python
# unittest код
class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()
    
    def test_add(self):
        result = self.calc.add(2, 3)
        self.assertEqual(result, 5)

# pytest эквивалент
@pytest.fixture
def calc():
    return Calculator()

def test_add(calc):
    result = calc.add(2, 3)
    assert result == 5
```

## 🎯 Когда использовать unittest

### ✅ Unittest подходит для:
- **Корпоративных проектов** с ограничениями на внешние зависимости
- **Legacy кода** который уже использует unittest
- **Строгих стандартов** кодирования в команде
- **Образовательных целей** (понимание основ)

### ❌ Лучше использовать pytest для:
- **Новых проектов** без ограничений
- **Быстрого прототипирования** тестов
- **Сложных фикстур** и параметризации
- **Интеграции с современными инструментами**

## 🎯 Следующие шаги

В следующей главе мы изучим pytest — более современный и мощный фреймворк тестирования, который стал стандартом в Python сообществе.

---

**Следующая глава:** [Pytest фреймворк](06_pytest.md)

*🧪 Основы unittest освоены — время познакомиться с pytest!*
