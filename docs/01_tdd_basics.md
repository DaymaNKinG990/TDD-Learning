# Основы Test-Driven Development

## 🎯 Философия TDD

TDD — это не просто техника тестирования, это **философия разработки**, которая меняет весь процесс создания программного обеспечения. В основе TDD лежит простая, но мощная идея: позвольте тестам направлять дизайн вашего кода.

## 📐 Законы TDD от Uncle Bob

Robert C. Martin (Uncle Bob) сформулировал три фундаментальных закона TDD:

### 🔴 Закон 1: Не пишите код без теста
**Вы не можете писать продуктивный код до тех пор, пока не напишете падающий unit test.**

```python
# ❌ НЕ ДЕЛАЙТЕ ТАК:
def calculate_discount(price, percentage):
    return price * (1 - percentage / 100)

# ✅ СНАЧАЛА ТЕСТ:
def test_calculate_discount():
    assert calculate_discount(100, 10) == 90
```

### 🟢 Закон 2: Минимальный тест
**Вы не можете написать unit test больше, чем необходимо для падения, а ошибки компиляции считаются падениями.**

```python
# ✅ МИНИМАЛЬНЫЙ ТЕСТ:
def test_user_has_name():
    user = User("John")
    assert user.name == "John"  # Только одна проверка!

# ❌ СЛИШКОМ МНОГО В ОДНОМ ТЕСТЕ:
def test_user_everything():
    user = User("John")
    assert user.name == "John"
    assert user.age == 0  # Лишнее для данного теста
    assert user.email is None  # Лишнее для данного теста
```

### 🔵 Закон 3: Минимальный код
**Вы не можете написать продуктивного кода больше, чем необходимо для прохождения текущего падающего теста.**

```python
# Для теста: assert add(2, 3) == 5

# ✅ МИНИМАЛЬНАЯ РЕАЛИЗАЦИЯ:
def add(a, b):
    return 5  # Да, это проходит тест!

# После добавления теста: assert add(1, 1) == 2
def add(a, b):
    return a + b  # Теперь нужна общая реализация
```

## 🔄 Детальный цикл TDD

### Фаза 1: 🔴 RED (Красный)

**Цель:** Написать *минимальный* тест, который падает.

#### Что делать:
1. **Подумайте о требовании** — что должен делать код?
2. **Напишите тест** для одного аспекта этого требования
3. **Запустите тест** — убедитесь, что он падает
4. **Прочитайте сообщение об ошибке** — понимание важно!

#### Пример:
```python
# Требование: создать класс для банковского счета
def test_new_account_has_zero_balance():
    account = Account()  # Класса пока нет!
    assert account.balance == 0
```

**Запуск теста:**
```bash
$ pytest test_account.py
NameError: name 'Account' is not defined
```

### Фаза 2: 🟢 GREEN (Зеленый)

**Цель:** Написать *минимальный* код для прохождения теста.

#### Что делать:
1. **Напишите простейший код** для прохождения теста
2. **Не думайте о красоте** — только о работоспособности
3. **Запустите тест** — убедитесь, что он проходит
4. **Запустите все тесты** — убедитесь, что ничего не сломалось

#### Пример:
```python
# account.py
class Account:
    def __init__(self):
        self.balance = 0  # Минимальная реализация!
```

**Запуск теста:**
```bash
$ pytest test_account.py
test_account.py::test_new_account_has_zero_balance PASSED
```

### Фаза 3: 🔵 REFACTOR (Рефакторинг)

**Цель:** Улучшить код без изменения функциональности.

#### Что делать:
1. **Посмотрите на дублирование** кода
2. **Улучшите именование** переменных и функций
3. **Извлеките константы** и магические числа
4. **Запускайте тесты** после каждого изменения
5. **Остановитесь** когда код станет чистым

#### Пример:
```python
# Было:
class Account:
    def __init__(self):
        self.balance = 0

# Стало (после добавления новых тестов):
class Account:
    def __init__(self, initial_balance: float = 0.0):
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")
        self._balance = initial_balance
    
    @property
    def balance(self) -> float:
        return self._balance
```

## 🎭 Роли в TDD

В TDD вы постоянно переключаетесь между тремя ролями:

### 👤 Роль 1: Клиент (Пишет тесты)
- **Думает о требованиях** и интерфейсах
- **Формулирует ожидания** от кода
- **Не беспокоится о реализации**

### 👤 Роль 2: Программист (Пишет код)
- **Фокусируется на простейшем решении**
- **Игнорирует будущие требования**
- **Делает тесты зелеными любой ценой**

### 👤 Роль 3: Рефакторер (Улучшает код)
- **Устраняет дублирование**
- **Улучшает читаемость**
- **Сохраняет все тесты зелеными**

## 📏 Принципы написания тестов

### 🏗 Arrange-Act-Assert (AAA)

Каждый тест должен иметь четкую структуру:

```python
def test_withdraw_money_from_account():
    # Arrange (Подготовка)
    account = Account(100)
    withdraw_amount = 30
    
    # Act (Действие)
    account.withdraw(withdraw_amount)
    
    # Assert (Проверка)
    assert account.balance == 70
```

### 🎯 F.I.R.S.T. принципы

Хорошие тесты должны быть:

#### **F**ast (Быстрые)
```python
# ✅ БЫСТРО:
def test_add():
    assert add(2, 3) == 5

# ❌ МЕДЛЕННО:
def test_database_connection():
    db = connect_to_real_database()  # Медленно!
    # ...
```

#### **I**ndependent (Независимые)
```python
# ✅ НЕЗАВИСИМЫЕ:
def test_create_user():
    user = User("John")
    assert user.name == "John"

def test_user_email():
    user = User("Jane")  # Новый объект!
    user.set_email("jane@example.com")
    assert user.email == "jane@example.com"
```

#### **R**epeatable (Повторяемые)
```python
# ✅ ПОВТОРЯЕМЫЙ:
def test_sort_numbers():
    numbers = [3, 1, 4, 1, 5]
    result = sort(numbers)
    assert result == [1, 1, 3, 4, 5]

# ❌ НЕ ПОВТОРЯЕМЫЙ:
def test_current_time():
    now = get_current_time()
    assert now == datetime.now()  # Всегда разное время!
```

#### **S**elf-validating (Самопроверяющиеся)
```python
# ✅ САМОПРОВЕРЯЮЩИЙСЯ:
def test_is_even():
    assert is_even(4) == True
    assert is_even(3) == False

# ❌ ТРЕБУЕТ РУЧНОЙ ПРОВЕРКИ:
def test_generate_report():
    report = generate_report()
    print(report)  # Нужно вручную проверить вывод
```

#### **T**imely (Своевременные)
Тесты пишутся **до** кода, а не после!

## 🎨 Типы тестов в TDD

### Unit Tests (Модульные тесты)
**90% ваших тестов должны быть unit тестами.**

```python
def test_password_validation():
    validator = PasswordValidator()
    
    # Тестируем один компонент изолированно
    assert validator.is_valid("password123") == False
    assert validator.is_valid("StrongP@ss1") == True
```

### Integration Tests (Интеграционные тесты)
**Тестируют взаимодействие компонентов.**

```python
def test_user_registration_flow():
    # Тестируем взаимодействие нескольких компонентов
    user_service = UserService()
    email_service = EmailService()
    
    user = user_service.register("john@example.com", "password")
    
    assert user.is_active == False
    assert email_service.was_confirmation_sent(user.email)
```

### End-to-End Tests (E2E тесты)
**Тестируют систему полностью.**

```python
def test_complete_purchase_flow():
    # Имитируем действия пользователя от начала до конца
    browser.visit("/products")
    browser.click_link("Buy Now")
    browser.fill_form({"email": "user@test.com"})
    browser.click_button("Complete Purchase")
    
    assert "Thank you for your purchase" in browser.html
```

## 🔧 Практическое упражнение: Калькулятор

Давайте применим TDD для создания простого калькулятора:

### Шаг 1: Первый тест 🔴
```python
# test_calculator.py
def test_add_two_positive_numbers():
    calc = Calculator()  # Класса пока нет!
    result = calc.add(2, 3)
    assert result == 5
```

### Шаг 2: Минимальная реализация 🟢
```python
# calculator.py
class Calculator:
    def add(self, a, b):
        return 5  # Хардкод для прохождения теста!
```

### Шаг 3: Второй тест 🔴
```python
def test_add_two_different_numbers():
    calc = Calculator()
    result = calc.add(1, 1)
    assert result == 2  # Теперь хардкод не поможет!
```

### Шаг 4: Общая реализация 🟢
```python
class Calculator:
    def add(self, a, b):
        return a + b  # Теперь нужна настоящая логика
```

### Шаг 5: Рефакторинг 🔵
```python
class Calculator:
    def add(self, a: float, b: float) -> float:
        """Add two numbers and return the result."""
        return a + b
```

## 🚀 Что дальше?

В следующей главе мы детально разберем:
- Настройку окружения для TDD в Python
- Выбор инструментов тестирования
- Конфигурацию pytest и unittest

## 💡 Ключевые выводы

1. **TDD — это дисциплина**, а не просто техника
2. **Тесты направляют дизайн** кода
3. **Маленькие шаги** лучше больших прыжков
4. **Рефакторинг безопасен** под защитой тестов
5. **Практика — ключ к мастерству**

---

**Следующая глава:** [Настройка окружения](02_environment_setup.md)

*📈 Продолжаем наше путешествие к мастерству TDD!*
